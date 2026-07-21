# AI Canonical Workflow Dictionary

## 1. Executive Summary

This canonical dictionary is required before implementing any AI-assisted GRC feature because Sanadcom uses several platform-native object names that do not match common business GRC terminology. Without a verified translation contract, an AI can produce outputs that are correct in business language but wrong for the actual Django models, serializers, API endpoints, frontend CRUD keys, or write semantics.

Future AI outputs must use platform-native object names internally even if the UI displays business-facing terms. In practice, this means:

- user explanations may say `Domain`, `Audit`, or `Framework`
- structured JSON, internal orchestration, and API calls must use the verified platform contract such as `Folder`, `ComplianceAssessment`, `StoredLibrary`, `LoadedLibrary`, `Framework`, `RequirementNode`, and `RequirementAssessment`

This Step 0.1 report is documentation and verification only. No application code, migrations, dependencies, or AI logic were added.

Primary verified source files:

- `backend/iam/models.py` with `Folder`
- `backend/core/models.py` with the main GRC domain models
- `backend/core/serializers.py` with read/write and permission behavior
- `backend/core/views.py` with viewsets, custom actions, and create side effects
- `backend/core/urls.py` with router registrations and custom endpoints
- `backend/library/serializers.py` with stored/loaded library serializers
- `backend/library/views.py` with library import/load/unload/apply behavior
- `frontend/src/lib/utils/crud.ts` with `URL_MODEL_MAP`
- `frontend/src/lib/utils/schemas.ts` with frontend payload schemas
- `frontend/src/lib/utils/types.ts` with `URL_MODEL`
- `frontend/src/lib/components/Forms/ModelForm.svelte` with model-to-form dispatch
- `frontend/src/lib/components/Modals/CreateModal.svelte` with generic modal create flow
- `frontend/src/lib/components/SideBar/QuickStart/QuickStartModal.svelte` and `frontend/src/routes/(app)/(internal)/quick-start/+page.server.ts` with the existing quick-start bootstrap flow

## 2. Canonical Business-to-Platform Dictionary

| Business GRC Term | Sanadcom Platform Entity | Django Model | Serializer | ViewSet/API | API Endpoint | Frontend Model Key / CRUD Config | Notes / Constraints |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Framework | Framework | `core.models.Framework` | `FrameworkReadSerializer`, `FrameworkWriteSerializer` in `backend/core/serializers.py` | `FrameworkViewSet` in `backend/core/views.py` | `/api/frameworks/` | `frameworks` in `frontend/src/lib/utils/crud.ts` | Do not confuse with library artifacts. A `Framework` is the loaded, usable control/requirement object, usually backed by a `LoadedLibrary`. |
| Stored Library | Stored library artifact | `core.models.StoredLibrary` | `StoredLibrarySerializer`, `StoredLibraryDetailedSerializer` in `backend/library/serializers.py` | `StoredLibraryViewSet` in `backend/library/views.py` | `/api/stored-libraries/`, `/api/stored-libraries/{id-or-urn}/import/`, `/api/stored-libraries/{id-or-urn}/unload/`, `/api/stored-libraries/{id-or-urn}/apply/`, `/api/stored-libraries/upload/` | `stored-libraries` in `frontend/src/lib/utils/crud.ts` | This is the importable source package. Business requests like "load framework" must often start here. |
| Loaded Library | Loaded library artifact | `core.models.LoadedLibrary` | `LoadedLibrarySerializer`, `LoadedLibraryDetailedSerializer` in `backend/library/serializers.py` | `LoadedLibraryViewSet` in `backend/library/views.py` | `/api/loaded-libraries/`, `/api/loaded-libraries/{id-or-urn}/tree/`, `/api/loaded-libraries/{id-or-urn}/content/`, `/api/loaded-libraries/{id-or-urn}/update/` | `loaded-libraries` in `frontend/src/lib/utils/crud.ts` | Intermediate runtime library object. `Framework`, `RiskMatrix`, `Threat`, and other referential objects can resolve from here. |
| Domain | Folder with domain content type | `iam.models.Folder` | `FolderReadSerializer`, `FolderWriteSerializer` in `backend/core/serializers.py` | `FolderViewSet` in `backend/core/views.py` | `/api/folders/` | `folders` with `localName: 'domain'` and `listViewUrlParams: '?content_type=DO&content_type=GL'` in `frontend/src/lib/utils/crud.ts` | Internally use `Folder`, not `Domain`. `Folder.ContentType.DOMAIN` lives in `backend/iam/models.py`. `FolderViewSet.perform_create()` creates default IAM groups. |
| Perimeter | Perimeter | `core.models.Perimeter` | `PerimeterReadSerializer`, `PerimeterWriteSerializer` | `PerimeterViewSet` | `/api/perimeters/` | `perimeters` | `Perimeter.folder` is the owning domain. `PerimeterWriteSerializer.update()` forbids changing the domain after creation. |
| Audit | Compliance assessment | `core.models.ComplianceAssessment` | `ComplianceAssessmentReadSerializer`, `ComplianceAssessmentWriteSerializer` | `ComplianceAssessmentViewSet` | `/api/compliance-assessments/` | `compliance-assessments` | Internally use `ComplianceAssessment`, not `Audit`. `ComplianceAssessmentViewSet.perform_create()` auto-creates `RequirementAssessment` children. |
| Requirement | Requirement node | `core.models.RequirementNode` | `RequirementNodeReadSerializer`, `RequirementNodeWriteSerializer` | `RequirementViewSet` in `backend/core/views.py` | `/api/requirement-nodes/` | `requirements` in `frontend/src/lib/utils/crud.ts` and `frontend/src/lib/utils/types.ts` | Naming mismatch: frontend key is `requirements`, backend route is `requirement-nodes`. Use `RequirementNode` as the internal canonical model. |
| Requirement Assessment | Requirement assessment | `core.models.RequirementAssessment` | `RequirementAssessmentReadSerializer`, `RequirementAssessmentWriteSerializer` | `RequirementAssessmentViewSet` | `/api/requirement-assessments/` | `requirement-assessments` | Usually auto-created from `ComplianceAssessmentViewSet.perform_create()`. AI should update these after audit creation instead of inventing standalone requirement objects. |
| Asset | Asset | `core.models.Asset` | `AssetReadSerializer`, `AssetWriteSerializer` | `AssetViewSet` | `/api/assets/` | `assets` | Folder-scoped primary/support asset graph. `AssetWriteSerializer` validates against cyclic parent/support relations. |
| Applied Control | Applied control | `core.models.AppliedControl` | `AppliedControlReadSerializer`, `AppliedControlWriteSerializer` | `AppliedControlViewSet` | `/api/applied-controls/` | `applied-controls` | Use this for implemented or proposed remediation controls. Do not confuse with `ReferenceControl`. `AppliedControlWriteSerializer.create()` handles extra `findings` and `task_templates` linkage after create. |
| Evidence | Evidence container | `core.models.Evidence` | `EvidenceReadSerializer`, `EvidenceWriteSerializer` | `EvidenceViewSet` | `/api/evidences/` and `/api/evidences/{id}/upload/` | `evidences` | Use `Evidence` for the logical evidence record. Actual file/link versioning is on `EvidenceRevision`. `EvidenceWriteSerializer.create()` auto-creates the initial revision. |
| Evidence Revision | Evidence revision | `core.models.EvidenceRevision` | `EvidenceRevisionReadSerializer`, `EvidenceRevisionWriteSerializer` | `EvidenceRevisionViewSet` | `/api/evidence-revisions/` and `/api/evidence-revisions/{id}/upload/` | `evidence-revisions` | Use for a specific uploaded or linked revision. `EvidenceRevisionWriteSerializer.create()` increments version and sets parent evidence status to `in_review`. |
| Risk Assessment | Risk assessment | `core.models.RiskAssessment` | `RiskAssessmentReadSerializer`, `RiskAssessmentWriteSerializer` | `RiskAssessmentViewSet` | `/api/risk-assessments/` | `risk-assessments` | `RiskAssessmentViewSet.perform_create()` may auto-create `RiskScenario` records when linked to an EBIOS RM study. |
| Vulnerability | Vulnerability | `core.models.Vulnerability` | `VulnerabilityReadSerializer`, `VulnerabilityWriteSerializer` | `VulnerabilityViewSet` | `/api/vulnerabilities/` | `vulnerabilities` | Folder-scoped object that can link to assets and applied controls. |
| Threat | Threat | `core.models.Threat` | `ThreatReadSerializer`, `ThreatWriteSerializer` | `ThreatViewSet` | `/api/threats/` | `threats` | Usually library-backed referential data. Useful in risk scenarios and findings. |
| Risk Scenario | Risk scenario | `core.models.RiskScenario` | `RiskScenarioReadSerializer`, `RiskScenarioWriteSerializer` | `RiskScenarioViewSet` | `/api/risk-scenarios/` | `risk-scenarios` | `RiskScenarioWriteSerializer.create()` derives `folder` from `risk_assessment`. Parent risk assessment lock state controls editability. |
| Finding Assessment | Findings assessment | `core.models.FindingsAssessment` | `FindingsAssessmentReadSerializer`, `FindingsAssessmentWriteSerializer` | `FindingsAssessmentViewSet` | `/api/findings-assessments/` | `findings-assessments` | Container object for follow-up, gaps, or findings. This is not the individual gap item. |
| Finding / Gap | Finding | `core.models.Finding` | `FindingReadSerializer`, `FindingWriteSerializer` | `FindingViewSet` | `/api/findings/` | `findings` | Use `Finding` for the individual gap/finding. `FindingWriteSerializer.create()` requires `findings_assessment` and derives `folder` from it. |
| Remediation / Action Plan | Applied control plus action-plan views | Primary model: `core.models.AppliedControl` | Primary serializers: `AppliedControlReadSerializer`, `AppliedControlWriteSerializer` | Primary API: `AppliedControlViewSet`; derived plan APIs: `ComplianceAssessmentActionPlanList`, `RiskAssessmentActionPlanList` in `backend/core/views.py` | `/api/applied-controls/`, `/api/compliance-assessments/{id}/action-plan/`, `/api/risk-assessments/{id}/action-plan/` | `applied-controls` | There is no dedicated `Remediation` or `ActionPlan` Django model in the inspected core domain. Treat remediation as linked `AppliedControl` records plus action-plan reporting surfaces. |
| Risk Acceptance | Risk acceptance | `core.models.RiskAcceptance` | `RiskAcceptanceReadSerializer`, `RiskAcceptanceWriteSerializer` | `RiskAcceptanceViewSet` | `/api/risk-acceptances/`, plus `/submit/`, `/draft/`, `/accept/`, `/reject/`, `/revoke/` actions | `risk-acceptances` | Acceptance is explicit stateful workflow. `RiskAcceptance.set_state()` updates timestamps and sets linked scenario treatment to `accept` on approval. |
| Validation Flow | Validation flow | `core.models.ValidationFlow` | `ValidationFlowReadSerializer`, `ValidationFlowWriteSerializer` | `ValidationFlowViewSet` | `/api/validation-flows/` | `validation-flows` | Cross-object approval/review workflow. `ValidationFlowWriteSerializer.create()` auto-sets requester and creates initial `FlowEvent`. |
| Workflow Case | Workflow case | `core.models.WorkflowCase` | `WorkflowCaseReadSerializer` and related serializers are referenced from `backend/core/views.py` but their definitions were not located in the inspected backend serializer files. `Needs verification.` | `WorkflowCaseViewSet` | `/api/workflow-cases/` | `workflow-cases`; schema present as `WorkflowCaseSchema` in `frontend/src/lib/utils/schemas.ts` | Good candidate orchestration object. Backend custom actions exist for closure readiness, review submission, residual-risk reassessment, and traceability. Exact serializer definitions need verification. |

Additional naming contract notes:

- Use `ReferenceControl` only when referring to a catalog or library control. Use `AppliedControl` when referring to an implemented, assigned, or proposed control instance.
- Use `Evidence` for the logical record and `EvidenceRevision` for a concrete uploaded or linked version.
- Use `FindingsAssessment` for the container and `Finding` for the individual gap/finding.
- Use `StoredLibrary` and `LoadedLibrary` when the workflow is dealing with framework import, activation, update, or unload behavior. Do not collapse all of that into `Framework`.

## 3. Required Creation Order

Safest canonical order for AI-assisted GRC case setup:

1. **Framework library resolution**
   - Resolve the requested framework library by stored library `id` or `urn` through `StoredLibraryViewSet` in `backend/library/views.py`.
   - If the framework is not yet loaded, call `StoredLibraryViewSet.import_library()` at `/api/stored-libraries/{id-or-urn}/import/`.
   - Resolve the usable `Framework` object from the resulting `LoadedLibrary`.
   - If risk setup also needs a risk matrix library, resolve and load that separately.

2. **Domain / Folder lookup or creation**
   - Look up an existing `Folder` first.
   - If none exists, create a `Folder` through `FolderWriteSerializer` and `FolderViewSet`.
   - Treat the business concept `Domain` as `Folder` with `content_type=DOMAIN` from `iam.models.Folder.ContentType.DOMAIN`.
   - `FolderViewSet.perform_create()` automatically creates default user groups and role assignments.

3. **Perimeter creation**
   - Create `Perimeter` with the owning `folder`.
   - Do not plan on changing the perimeter's domain later; `PerimeterWriteSerializer.update()` blocks folder changes.

4. **Audit / ComplianceAssessment creation**
   - Create `ComplianceAssessment` using the verified `framework`, `folder`, and `perimeter`.
   - If cloning from a baseline audit, use the `baseline` field during create.
   - Do not create child requirement assessments manually before this step.

5. **RequirementAssessment creation behavior**
   - `ComplianceAssessmentViewSet.perform_create()` calls `instance.create_requirement_assessments(baseline)`.
   - Canonical AI behavior: wait for the platform to generate `RequirementAssessment` records automatically.
   - If a baseline from another framework is used, mapping inference may also run in `ComplianceAssessmentViewSet.perform_create()`.

6. **Asset creation**
   - Create `Asset` records in the folder scope.
   - Link parent/support asset relationships during create only if the graph is already known and non-cyclic.

7. **AppliedControl creation**
   - Create `AppliedControl` records in the folder scope.
   - If the AI is drafting remediation controls, this is the canonical object to create.
   - Link to assets, findings, requirement assessments, or task templates only when those targets already exist and are visible.

8. **Vulnerability creation**
   - Create `Vulnerability` records once relevant assets and controls exist.
   - Link to `assets` and `applied_controls` during create if known.

9. **RiskAssessment creation**
   - Create `RiskAssessment` with the correct `folder`, `perimeter`, and `risk_matrix`.
   - If created from an EBIOS RM study, `RiskAssessmentViewSet.perform_create()` may auto-create risk scenarios.

10. **RiskScenario creation**
   - Create `RiskScenario` records after the risk assessment exists.
   - Canonical minimum required field is `risk_assessment`.
   - `RiskScenarioWriteSerializer.create()` derives `folder` from `risk_assessment` automatically.
   - Link assets, vulnerabilities, threats, and applied controls during create when the references already exist.

11. **Evidence creation**
   - Create `Evidence` records after the main target objects exist.
   - Link directly to `requirement_assessments`, `applied_controls`, `findings`, or `findings_assessments` when known.
   - `EvidenceWriteSerializer.create()` automatically creates the initial `EvidenceRevision`.

12. **RequirementAssessment update with controls / evidence / results**
   - After the platform auto-generates `RequirementAssessment` records, update them with:
     - `applied_controls`
     - `evidences`
     - `result`
     - `extended_result`
     - `score`
     - `observation`
     - `answers`
   - This is the preferred step for AI-produced audit result drafts.

13. **Finding generation**
   - Create or reuse a `FindingsAssessment` container first.
   - Then create `Finding` records under that container.
   - Canonical create target for a single generated gap is `Finding`, not `FindingsAssessment`.

14. **Remediation / action plan linkage**
   - Represent remediation as `AppliedControl` records linked to:
     - `RequirementAssessment`
     - `Finding`
     - `RiskScenario`
     - optionally `Asset`
   - Use action-plan endpoints only as reporting/aggregation surfaces, not as canonical creation targets.

15. **RiskAcceptance draft creation**
   - Create `RiskAcceptance` only after the relevant `RiskScenario` records exist.
   - Link one or more `risk_scenarios` and the intended `approver`.
   - Leave stateful transitions to the explicit workflow actions in `RiskAcceptanceViewSet`.

Canonical caution points:

- Do not create `RequirementAssessment` before `ComplianceAssessment`.
- Do not create `EvidenceRevision` before `Evidence`.
- Do not create `RiskScenario` without `RiskAssessment`.
- Do not treat action-plan endpoints as the canonical remediation write target.
- Do not emit a `Domain` object type in structured AI outputs. Use `Folder`.

## 4. Relationship Rules

Global write constraints verified in `backend/core/serializers.py`:

- `BaseModelSerializer.create()` enforces folder-scoped `add_*` permission through `_check_object_perm()`
- `BaseModelSerializer.update()` enforces folder-scoped `change_*` permission
- `BaseModelSerializer.delete()` enforces folder-scoped `delete_*` permission
- `BaseModelSerializer._check_m2m_visibility()` blocks linking M2M objects the requester cannot view

| Source entity | Target entity | Relationship field name | Relation type | Writable during create | Follow-up update required | Visibility / permission constraints |
| --- | --- | --- | --- | --- | --- | --- |
| `Folder` | `Perimeter` | `Perimeter.folder` | FK | Yes | No | `PerimeterWriteSerializer.update()` forbids changing the folder later. Folder add permission required. |
| `Folder` | `Asset` | `Asset.folder` | FK | Yes | No | Folder add/change permission required. Asset graph links must also pass visibility and cycle validation. |
| `Folder` | `AppliedControl` | `AppliedControl.folder` | FK | Yes | No | Folder add/change permission required. Linked M2M objects must be visible. |
| `Folder` | `Evidence` | `Evidence.folder` | FK | Yes | No | Folder add/change permission required. If folder changes later, evidence revisions are cascaded in `EvidenceWriteSerializer.update()`. |
| `Perimeter` | `ComplianceAssessment` | `ComplianceAssessment.perimeter` | FK | Yes | No | Supply `folder` consistently with the perimeter. On update, `ComplianceAssessmentWriteSerializer.update()` will realign folder from perimeter. |
| `Perimeter` | `RiskAssessment` | `RiskAssessment.perimeter` | FK | Yes | No | Supply `folder` consistently with the perimeter. On update, `RiskAssessmentWriteSerializer.update()` realigns folder and cascades to child risk scenarios. |
| `ComplianceAssessment` | `RequirementAssessment` | `RequirementAssessment.compliance_assessment` | Reverse FK with automatic create side effect | No nested create on audit create | No, if using the golden path | `ComplianceAssessmentViewSet.perform_create()` auto-creates requirement assessments through `instance.create_requirement_assessments(baseline)`. AI should wait for platform-generated children. |
| `RequirementAssessment` | `AppliedControl` | `RequirementAssessment.applied_controls` | M2M | Technically yes on requirement-assessment writes | Preferred as follow-up update | Blocked if parent audit is locked or in review. Linked controls must be visible to the requester. |
| `RequirementAssessment` | `Evidence` | `RequirementAssessment.evidences` | M2M | Technically yes on requirement-assessment writes | Preferred as follow-up update | Same lock/review restrictions as above. Linked evidences must be visible. |
| `RiskAssessment` | `RiskScenario` | `RiskScenario.risk_assessment` | FK / reverse relation | Yes | No | `RiskScenarioWriteSerializer.create()` derives folder from parent risk assessment. Parent lock blocks edits. EBIOS RM integration may also auto-create scenarios. |
| `RiskScenario` | `Asset` | `RiskScenario.assets` | M2M | Yes | No | Linked assets must be visible. Parent risk assessment lock blocks writes. |
| `RiskScenario` | `Vulnerability` | `RiskScenario.vulnerabilities` | M2M | Yes | No | Linked vulnerabilities must be visible. Parent risk assessment lock blocks writes. |
| `RiskScenario` | `AppliedControl` | `RiskScenario.applied_controls` | M2M | Yes | No | Linked controls must be visible. Parent risk assessment lock blocks writes. |
| `Finding` | `RequirementAssessment` | No direct field on `Finding` | Not supported as direct relation | No | Would require indirect linkage through controls, evidences, workflow case, or custom logic | `Needs verification` only if future modules add such a field. No direct field found in `core.models.Finding` or `FindingWriteSerializer`. |
| `Finding` | `Evidence` | `Finding.evidences` | M2M | Yes | No | Linked evidences must be visible. Finding parent assessment lock blocks writes. |
| `Finding` | `AppliedControl` | `Finding.applied_controls` | M2M | Yes | No | Linked controls must be visible. Finding parent assessment lock blocks writes. |
| `Finding` | `RiskScenario` | No direct field on `Finding` | Not supported as direct relation | No | Would require indirect linkage through `WorkflowCase` or shared controls/evidences | No direct `risk_scenarios` field found on `core.models.Finding`. |
| `RiskAcceptance` | `RiskScenario` | `RiskAcceptance.risk_scenarios` | M2M | Yes | No | Linked scenarios must be in visible folder scope. `RiskAcceptanceViewSet.perform_update()` verifies approver permission across each selected scenario folder. Accept/reject/revoke actions are restricted to the approver. |
| `WorkflowCase` | Related objects | `owners`, `reviewers`, `affected_assets`, `requirement_assessments`, `findings`, `findings_assessments`, `risk_scenarios`, `incidents`, `applied_controls`, `task_templates`, `evidences`, `validation_flows`, `security_exceptions` | M2M | Frontend schema indicates yes | Needs verification for exact backend serializer behavior | Model fields are verified in `core.models.WorkflowCase` and CRUD/schema support exists in frontend. Exact backend serializer definitions were not located in the inspected serializer file set. |

Important derived or action-based relationships:

- `RiskScenario.folder` is derived during create from `risk_assessment` in `RiskScenarioWriteSerializer.create()`.
- `Finding.folder` is derived during create from `findings_assessment.folder` in `FindingWriteSerializer.create()`.
- `EvidenceRevision.version` is derived during create from prior revisions in `EvidenceRevisionWriteSerializer.create()`.
- `RiskAcceptance.state` changes are not free-form status edits. They are workflow actions in `RiskAcceptanceViewSet`.
- `ValidationFlow` links to multiple object families through explicit M2M fields and also creates `FlowEvent` records on transitions.

## 5. AI Output Naming Rules

Future AI features must follow these naming rules:

1. AI may use user-facing business labels in narrative explanations.
   - Example: "Create a domain and an audit."

2. AI structured JSON must use canonical internal entity names.
   - Example: use `Folder`, `ComplianceAssessment`, `RequirementAssessment`, `AppliedControl`, `RiskScenario`.

3. AI must not invent entity types that do not exist.
   - Invalid examples: `DomainRecord`, `AuditRecord`, `RemediationPlan`, `ComplianceGapCase`, `FrameworkLoadRequest`.

4. AI must split ambiguous business terms into the correct platform-native type.
   - `Framework` may mean `StoredLibrary`, `LoadedLibrary`, or `Framework`.
   - `Control` may mean `ReferenceControl` or `AppliedControl`.
   - `Evidence` may mean `Evidence` or `EvidenceRevision`.

5. Every AI suggestion payload must include at minimum:
   - `source_text`
   - `rationale`
   - `confidence`
   - `required_human_action`

6. Every uncertain or heuristic mapping must include:
   - `needs_review: true`

7. Every structured draft should carry both business and platform naming when useful.
   - Recommended pattern: `business_label`, `platform_entity`, `api_resource`.

8. AI must preserve the distinction between object creation and object update.
   - Example: creating an `Audit` means creating a `ComplianceAssessment`.
   - Updating audit results means updating existing `RequirementAssessment` records, not creating new requirement nodes.

9. AI must preserve the distinction between first-class models and derived/reporting surfaces.
   - `Action plan` is not a canonical model.
   - `ComplianceAssessment` action-plan and `RiskAssessment` action-plan endpoints are aggregation/reporting surfaces.

10. AI must respect platform state machines.
    - `RiskAcceptance` state changes must use explicit workflow actions.
    - `ValidationFlow` transitions must respect requester/approver rules.
    - Locked audits, findings assessments, and risk assessments must not be silently overwritten.

## 6. Draft JSON Schema Names

The following are proposed stable draft schema names for future AI outputs. Only top-level fields are defined here.

| Schema name | Proposed top-level fields |
| --- | --- |
| `AiCaseIntakeDraft` | `draft_id`, `case_title`, `case_summary`, `business_goal`, `input_sources`, `detected_terms`, `canonical_mappings`, `target_folder`, `target_perimeter`, `requested_frameworks`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiCaseSetupDraft` | `draft_id`, `platform_entity`, `folder`, `perimeter`, `framework_resolution`, `audit_plan`, `risk_plan`, `asset_plan`, `control_plan`, `evidence_plan`, `finding_plan`, `risk_acceptance_plan`, `workflow_case_plan`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiAssetDraft` | `draft_id`, `platform_entity`, `folder`, `name`, `description`, `asset_type`, `asset_class`, `owner_ids`, `parent_asset_ids`, `support_asset_ids`, `reference_link`, `observation`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiAppliedControlDraft` | `draft_id`, `platform_entity`, `folder`, `name`, `description`, `reference_control_id`, `category`, `status`, `owner_ids`, `asset_ids`, `requirement_assessment_ids`, `risk_scenario_ids`, `finding_ids`, `eta`, `effort`, `priority`, `observation`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiVulnerabilityDraft` | `draft_id`, `platform_entity`, `folder`, `name`, `description`, `severity`, `status`, `asset_ids`, `applied_control_ids`, `security_exception_ids`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiRiskScenarioDraft` | `draft_id`, `platform_entity`, `risk_assessment_id`, `name`, `description`, `threat_ids`, `asset_ids`, `vulnerability_ids`, `applied_control_ids`, `existing_applied_control_ids`, `treatment`, `owner_ids`, `justification`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiRequirementAssessmentDraft` | `draft_id`, `platform_entity`, `requirement_assessment_id`, `compliance_assessment_id`, `requirement_id`, `status`, `result`, `extended_result`, `score`, `documentation_score`, `answers`, `evidence_ids`, `applied_control_ids`, `observation`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiEvidenceAnalysisDraft` | `draft_id`, `platform_entity`, `folder`, `evidence_id`, `evidence_revision_id`, `linked_requirement_assessment_ids`, `linked_applied_control_ids`, `linked_finding_ids`, `status_recommendation`, `expiry_assessment`, `summary`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiComplianceResultDraft` | `draft_id`, `platform_entity`, `compliance_assessment_id`, `requirement_results`, `overall_summary`, `non_compliant_count`, `partially_compliant_count`, `compliant_count`, `not_applicable_count`, `recommended_findings`, `recommended_controls`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiFindingDraft` | `draft_id`, `platform_entity`, `findings_assessment_id`, `name`, `description`, `severity`, `priority`, `status`, `threat_ids`, `vulnerability_ids`, `applied_control_ids`, `evidence_ids`, `reference_control_ids`, `owner_ids`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |
| `AiRemediationDraft` | `draft_id`, `platform_entity`, `primary_target_type`, `primary_target_id`, `recommended_applied_controls`, `related_requirement_assessment_ids`, `related_finding_ids`, `related_risk_scenario_ids`, `related_asset_ids`, `target_eta`, `priority`, `implementation_notes`, `needs_review`, `confidence`, `required_human_action`, `source_text`, `rationale` |

Schema naming rules:

- Use singular, stable, platform-aware names.
- Prefer `Draft` suffix for all non-committed AI output.
- Include `platform_entity` and object IDs whenever the draft references existing persisted records.
- Do not use business-only names like `AiAuditDraft` unless they map unambiguously to `ComplianceAssessment` and that mapping is explicitly stored.

## 7. Unsafe or Ambiguous Terms

| Ambiguous business term | Why it is dangerous in this codebase | What the AI must do instead |
| --- | --- | --- |
| Domain | There is no standalone `Domain` model in the core GRC domain. The business concept maps to the IAM-backed `Folder` model. | Use `Folder` internally and specify `content_type=DOMAIN` semantics in logic or metadata. |
| Audit | There is no `Audit` Django model. The platform object is `ComplianceAssessment`. | Use `ComplianceAssessment` for create/update/API/JSON. Use `Audit` only in end-user narrative text. |
| Framework | The term may mean the source package, the loaded package, or the usable framework object. | Force a three-way distinction: `StoredLibrary`, `LoadedLibrary`, `Framework`. |
| Control | The term can mean a catalog control or an implemented control instance. | Use `ReferenceControl` for catalog/library content and `AppliedControl` for implementation/remediation instances. |
| Evidence | The term can mean the logical record or a specific uploaded/link version. | Use `Evidence` for the container and `EvidenceRevision` for a specific revision. |
| Finding | The term may mean the individual gap item or the container that groups multiple findings. | Use `Finding` for the individual item and `FindingsAssessment` for the container. |
| Remediation | No dedicated `Remediation` model was found in the inspected platform core. | Represent remediation as `AppliedControl` records plus related action-plan/reporting endpoints. |
| Closure | Closure is not owned by a single universal object. Different objects close differently. | Use the specific platform object and state machine: `Finding.status`, `WorkflowCase.status`, `RiskAcceptance.state`, `ValidationFlow.status`, or assessment locks as applicable. |

Additional unsafe terms the AI should avoid unless explicitly disambiguated:

- `Requirement`: must resolve to `RequirementNode` or `RequirementAssessment`
- `Library`: must resolve to `StoredLibrary` or `LoadedLibrary`
- `Gap`: should usually resolve to `Finding`, not `FindingsAssessment`
- `Review`: could mean `ValidationFlow`, assessment reviewer assignment, or risk acceptance approval

## 8. Step 0.1 Acceptance Criteria

Step 0.1 is complete only when all of the following are true:

1. A canonical business-to-platform dictionary exists and is agreed by engineering and product.
2. Every future AI feature is required to use platform-native internal object names in structured outputs.
3. The following semantic translations are explicitly locked:
   - `Domain` -> `Folder`
   - `Audit` -> `ComplianceAssessment`
   - `Framework load` -> `StoredLibrary` -> `LoadedLibrary` -> `Framework`
   - `Requirement` -> `RequirementNode`
   - `Finding / Gap` -> `Finding`
   - `Remediation` -> `AppliedControl` plus action-plan surfaces
4. The safest object creation order is documented, including automatic child creation behavior for `RequirementAssessment`.
5. Relationship rules are documented with field names, relation types, write timing, and permission constraints.
6. The AI naming rules require:
   - `source_text`
   - `rationale`
   - `confidence`
   - `required_human_action`
   - `needs_review=true` for uncertain mappings
7. Unsafe and ambiguous business terms are explicitly prohibited from being used as internal object types.
8. Known uncertainties are preserved rather than guessed.
   - `WorkflowCase` backend serializer definitions were not located in the inspected serializer file set. `Needs verification.`
   - Frontend uses `requirements` while backend routes use `requirement-nodes`. This naming mismatch must be handled explicitly in Step 0.2 and Step 1.
9. No application code, migrations, dependencies, or AI implementation changes were introduced during Step 0.1.
10. The contract is precise enough that a future AI Case Intake or AI Case Setup implementation can generate JSON using the correct internal vocabulary and correct API targets.
