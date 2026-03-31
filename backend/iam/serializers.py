import structlog
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.serializer_fields import FieldsRelatedField

from .models import PersonalAccessToken, RegistrationRequest, User

logger = structlog.get_logger(__name__)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(
        # This will be used when the DRF browsable API is enabled
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )
            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_new_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_new_password(self, data):
        password_validation.validate_password(data)
        return data

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "The two password fields didn't match."}
            )
        return data


class SetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password set endpoint as an administrator.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    new_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_new_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_new_password(self, data):
        password_validation.validate_password(data)
        return data

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "The two password fields didn't match."}
            )
        return data


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset endpoint.
    """

    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_new_password = serializers.CharField(
        max_length=128, write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_new_password(self, data):
        password_validation.validate_password(data)
        return data

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "The two password fields didn't match."}
            )
        return data


class PersonalAccessTokenReadSerializer(serializers.ModelSerializer):
    """
    Serializer for PersonalAccessToken model.
    """

    user = FieldsRelatedField(["email", "id"])

    class Meta:
        model = PersonalAccessToken
        fields = ["name", "user", "created", "expiry", "digest"]


# ── Registration request serializers ─────────────────────────────────────


class RegistrationRequestCreateSerializer(serializers.Serializer):
    """Public-facing serializer for self-service registration."""

    email = serializers.EmailField(max_length=100)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    company = serializers.CharField(max_length=200)
    job_title = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    department = serializers.CharField(max_length=150, required=False, allow_blank=True)
    reason = serializers.CharField(max_length=2000)
    password = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )

    def validate_email(self, value):
        email = value.lower().strip()
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        if RegistrationRequest.objects.filter(
            email__iexact=email,
            status=RegistrationRequest.Status.PENDING,
        ).exists():
            raise serializers.ValidationError(
                "A registration request for this email is already pending."
            )
        return email

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "The two password fields didn't match."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        validated_data["password_hash"] = make_password(password)
        return RegistrationRequest.objects.create(**validated_data)


class RegistrationRequestReadSerializer(serializers.ModelSerializer):
    """Admin-facing serializer to list/retrieve registration requests."""

    reviewed_by = FieldsRelatedField(["email", "id"], required=False)

    class Meta:
        model = RegistrationRequest
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "company",
            "job_title",
            "phone",
            "department",
            "reason",
            "status",
            "created_at",
            "updated_at",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "assigned_user_groups",
            "assigned_folder",
        ]
        read_only_fields = fields


class RegistrationRequestReviewSerializer(serializers.Serializer):
    """Serializer for the approve/reject action by admin."""

    action = serializers.ChoiceField(choices=["approve", "reject"])
    review_notes = serializers.CharField(required=False, allow_blank=True, default="")
    user_groups = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    folder = serializers.UUIDField(required=False, allow_null=True, default=None)
