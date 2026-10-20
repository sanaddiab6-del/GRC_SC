"""Human-reviewed new-case preflight. Authenticated; never calls .save()."""
from __future__ import annotations
from django.http import Http404
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .workforce_case_plan_service import prepare_new_case_plan


class NewCasePlanInput(serializers.Serializer):
    organization = serializers.CharField(min_length=3, max_length=150)
    scope = serializers.CharField(min_length=5, max_length=500)
    framework_id = serializers.UUIDField()
    domain_strategy = serializers.ChoiceField(choices=['create', 'reuse'])
    selected_folder_id = serializers.UUIDField(required=False, allow_null=True)
    parent_folder_id = serializers.UUIDField(required=False, allow_null=True)
    framework_review_confirmed = serializers.BooleanField(default=False)

    def validate(self, data):
        if data['domain_strategy'] == 'reuse' and not data.get('selected_folder_id'):
            raise serializers.ValidationError({'selected_folder_id':'Choose the existing organizational domain.'})
        if data['domain_strategy'] == 'create' and not data.get('parent_folder_id'):
            raise serializers.ValidationError({'parent_folder_id':'Choose an authorized parent organizational scope.'})
        return data


class AiWorkforceNewCasePlanView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        input_serializer = NewCasePlanInput(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            result = prepare_new_case_plan(request.user, **input_serializer.validated_data)
        except Http404:
            return Response({'detail':'Selected platform record unavailable or not accessible.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({'detail':str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
