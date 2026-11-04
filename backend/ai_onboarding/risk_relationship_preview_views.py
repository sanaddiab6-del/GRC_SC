"""Phase 2A: authenticated read-only matching of EXISTING risk relationships.

No database writes, no AI calls and no ratings. This endpoint is separate from
Step 8B; Step 8B's previously reviewed create contract remains unchanged.
"""
from __future__ import annotations

import uuid

from core.models import RiskAssessment, RiskScenario, Threat, Vulnerability
from iam.models import Folder, RoleAssignment
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .risk_relationship_matcher import advisory_line, match_candidates

MAX_CANDIDATES_SCANNED = 300


def _is_readable(user, model, item) -> bool:
    return bool(RoleAssignment.is_object_readable(user, model, item.id))


def _readable_candidates(user, model, folder_id):
    # Never perform an unscoped query. A platform-wide library catalog can be
    # considered in a separate future, explicitly designed permission contract.
    candidates = model.objects.filter(folder_id=folder_id).order_by('name', 'id')[:MAX_CANDIDATES_SCANNED]
    result = []
    for item in candidates:
        if _is_readable(user, model, item):
            result.append({
                'id': str(item.id),
                'name': item.name or '',
                'description': (getattr(item, 'description', '') or '')[:2000],
                'reference': getattr(item, 'ref_id', '') or '',
            })
    return result


class AiRiskRelationshipPreviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'options', 'head']

    def post(self, request, format=None):
        body = request.data
        if not isinstance(body, dict) or set(body) != {'scenario_reference'}:
            return Response({'detail': 'Only scenario_reference is accepted.'}, status=400)
        raw_reference = body.get('scenario_reference')
        if not isinstance(raw_reference, str):
            return Response({'detail': 'A valid scenario_reference is required.'}, status=400)
        try:
            reference = uuid.UUID(raw_reference.strip())
        except (ValueError, AttributeError):
            return Response({'detail': 'A valid scenario_reference UUID is required.'}, status=400)

        # Match the risk to its existing assessment and exact organizational
        # folder. Deny on any missing, inconsistent, or unreadable relationship.
        risk = (RiskScenario.objects
                .select_related('risk_assessment', 'risk_assessment__folder', 'folder')
                .filter(id=reference).first())
        if risk is None:
            return Response({'detail': 'Risk scenario not found or not accessible.'}, status=404)
        assessment = risk.risk_assessment
        folder = assessment.folder
        if (folder is None or risk.folder_id != folder.id
                or not _is_readable(request.user, RiskScenario, risk)
                or not _is_readable(request.user, RiskAssessment, assessment)
                or not _is_readable(request.user, Folder, folder)):
            return Response({'detail': 'Risk scenario not found or not accessible.'}, status=404)

        threat_hint = advisory_line(risk.description, 'Threat')
        vulnerability_hint = advisory_line(risk.description, 'Vulnerability')
        existing_threats = list(risk.threats.filter(folder_id=folder.id))
        existing_vulnerabilities = list(risk.vulnerabilities.filter(folder_id=folder.id))
        # Do not disclose linked objects unless separately readable. If a linked
        # object is outside this folder, do not return it in this endpoint.
        readable_threats = [x for x in existing_threats if _is_readable(request.user, Threat, x)]
        readable_vulnerabilities = [x for x in existing_vulnerabilities if _is_readable(request.user, Vulnerability, x)]
        threat_candidates = _readable_candidates(request.user, Threat, folder.id)
        vulnerability_candidates = _readable_candidates(request.user, Vulnerability, folder.id)
        linked_threat_ids = {str(x.id) for x in readable_threats}
        linked_vulnerability_ids = {str(x.id) for x in readable_vulnerabilities}
        threat_matches = [x for x in match_candidates(threat_hint, threat_candidates) if x['id'] not in linked_threat_ids]
        vulnerability_matches = [x for x in match_candidates(vulnerability_hint, vulnerability_candidates) if x['id'] not in linked_vulnerability_ids]

        return Response({
            'status': 'preview_only',
            'read_only': True,
            'match_method': 'keyword_overlap_not_evidence_verified',
            'scope': {'folder_name': folder.name, 'assessment_name': assessment.name},
            'scenario': {'id': str(risk.id), 'name': risk.name},
            'advisory': {'threat': threat_hint, 'vulnerability': vulnerability_hint},
            'linked': {
                'threats': [{'id': str(x.id), 'name': x.name} for x in readable_threats],
                'vulnerabilities': [{'id': str(x.id), 'name': x.name} for x in readable_vulnerabilities],
            },
            'suggestions': {
                'threats': threat_matches,
                'vulnerabilities': vulnerability_matches,
            },
            'limitations': [
                'Candidates are restricted to the same folder and readable records.',
                f'At most {MAX_CANDIDATES_SCANNED} records per type were scanned. No match does not prove absence.',
                'Keyword overlap is not proof a threat or vulnerability exists or is applicable.',
                'No records were created, linked, rated, treated, or changed.',
            ],
        }, status=status.HTTP_200_OK)
