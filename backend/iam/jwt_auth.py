"""
JWT Authentication for CISO Assistant GRC Platform
====================================================
Provides stateless JWT authentication coexisting with Knox tokens.
Suited for API clients, M2M communication, and external integrations.

Role / Responsibility Hierarchy
---------------------------------
Tier 1 – System Administrator : Full platform governance
Tier 2 – Domain Manager       : Manage domain-level settings & users
Tier 3 – Analyst              : Create/edit risk assessments
Tier 4 – Approver             : Sign-off on findings & controls
Tier 5 – Reader               : Audit-trail / read-only visibility
Tier 6 – Auditee              : Interact with assigned compliance tasks
Tier 7 – Third-Party          : Scoped external respondent

Endpoints
---------
POST /api/iam/jwt/token/    – Obtain access + refresh token pair
POST /api/iam/jwt/refresh/  – Exchange refresh token for a new access token
POST /api/iam/jwt/logout/   – Blacklist a refresh token
GET  /api/iam/jwt/info/     – Decode current token claims (authenticated)
GET  /api/iam/jwt/roles/    – Browse platform role hierarchy (public)
"""

from __future__ import annotations

import structlog
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

logger = structlog.get_logger(__name__)

User = get_user_model()

# ─────────────────────────────────────────────
#  Role Hierarchy Definition
# ─────────────────────────────────────────────

#: Maps built-in role codenames to privilege tiers (lower = more privileged).
ROLE_TIER_MAP: dict[str, int] = {
    "BI-RL-ADM": 1,  # System Administrator  — full platform control
    "BI-RL-DMA": 2,  # Domain Manager        — manage assigned domains
    "BI-RL-ANA": 3,  # Analyst               — create/edit assessments
    "BI-RL-APP": 4,  # Approver              — sign-off findings
    "BI-RL-AUD": 5,  # Reader                — read-only visibility
    "BI-RL-ADE": 6,  # Auditee               — respond to compliance tasks
    "BI-RL-TPR": 7,  # Third-Party           — scoped external access
}

#: Full hierarchy descriptor returned by the public /jwt/roles/ endpoint.
ROLE_HIERARCHY: list[dict] = [
    {
        "tier": 1,
        "codename": "BI-RL-ADM",
        "label": "System Administrator",
        "responsibilities": [
            "Manage platform-level configuration and settings",
            "Create, modify, and delete domains and folders",
            "Manage all users, groups, and role assignments",
            "Access all modules, assessments, and reports",
            "Perform backup, restore, and system operations",
        ],
        "can_manage_tiers": list(range(1, 8)),
    },
    {
        "tier": 2,
        "codename": "BI-RL-DMA",
        "label": "Domain Manager",
        "responsibilities": [
            "Manage users and permissions within assigned domains",
            "Configure domain-level settings and workflows",
            "Oversee risk and compliance programs for the domain",
            "Assign Analyst and Approver roles within scope",
            "Review domain-level dashboards and reports",
        ],
        "can_manage_tiers": list(range(3, 8)),
    },
    {
        "tier": 3,
        "codename": "BI-RL-ANA",
        "label": "Analyst",
        "responsibilities": [
            "Create, edit, and delete risk assessments",
            "Associate controls, mitigations, and threats",
            "Upload and manage evidence artifacts",
            "Conduct compliance assessments against frameworks",
            "Generate and export compliance and risk reports",
        ],
        "can_manage_tiers": [],
    },
    {
        "tier": 4,
        "codename": "BI-RL-APP",
        "label": "Approver",
        "responsibilities": [
            "Review and approve or reject risk findings",
            "Validate compliance assessment results",
            "Sign-off on remediation and treatment plans",
            "Accept residual risk on behalf of the organisation",
        ],
        "can_manage_tiers": [],
    },
    {
        "tier": 5,
        "codename": "BI-RL-AUD",
        "label": "Reader",
        "responsibilities": [
            "View all objects within assigned scope",
            "Export and download reports",
            "No write access to any module",
        ],
        "can_manage_tiers": [],
    },
    {
        "tier": 6,
        "codename": "BI-RL-ADE",
        "label": "Auditee",
        "responsibilities": [
            "Respond to assigned compliance tasks and questionnaires",
            "View assigned audits, checklists, and assessments",
            "Upload evidence for assigned controls",
        ],
        "can_manage_tiers": [],
    },
    {
        "tier": 7,
        "codename": "BI-RL-TPR",
        "label": "Third-Party Respondent",
        "responsibilities": [
            "Respond to assigned TPRM questionnaires",
            "Upload evidence for third-party reviews",
            "Limited read access to assigned scopes only",
        ],
        "can_manage_tiers": [],
    },
]


def _user_tier(user) -> tuple[int, str]:
    """
    Compute the highest-privilege tier (lowest tier number) held by this user.
    Returns a (tier_number, tier_label) tuple.
    """
    roles: list[str] = user.get_roles()
    tiers = [ROLE_TIER_MAP[r] for r in roles if r in ROLE_TIER_MAP]
    tier = min(tiers, default=7)
    label = next(
        (r["label"] for r in ROLE_HIERARCHY if r["tier"] == tier),
        "Third-Party Respondent",
    )
    return tier, label


# ─────────────────────────────────────────────
#  Custom Token Serializer (embeds GRC claims)
# ─────────────────────────────────────────────


class GRCTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends simplejwt's pair serializer with GRC role-hierarchy claims.

    The platform's User model uses `email` as USERNAME_FIELD, so simplejwt
    picks that up automatically.  Request body: { "email": "...", "password": "..." }.

    Extra claims embedded in both access and refresh tokens:
      - ``user_id``   : UUID string
      - ``email``     : user email address
      - ``is_admin``  : boolean shortcut
      - ``tier``      : integer privilege tier (1 = highest, 7 = lowest)
      - ``tier_label``: human-readable tier name
      - ``roles``     : list of role codenames (e.g. ["BI-RL-ANA"])
    """

    @classmethod
    def get_token(cls, user) -> RefreshToken:
        token = super().get_token(user)

        # Identity claims
        token["user_id"] = str(user.id)
        token["email"] = user.email
        token["is_admin"] = user.is_admin()

        # Role-hierarchy claims
        roles = user.get_roles()
        tier, tier_label = _user_tier(user)
        token["tier"] = tier
        token["tier_label"] = tier_label
        token["roles"] = roles

        logger.info(
            "jwt_token_issued",
            user_email=user.email,
            tier=tier,
            roles=roles,
        )
        return token

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)

        # Defense-in-depth: prevent SSO-only accounts from using local JWT login
        if not self.user.is_local:
            raise serializers.ValidationError(
                _("This account uses SSO. Local JWT login is not permitted."),
                code="sso_required",
            )

        return data


# ─────────────────────────────────────────────
#  Views
# ─────────────────────────────────────────────


class GRCTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/iam/jwt/token/

    Obtain a JWT access + refresh token pair.

    Request body::

        { "email": "user@example.com", "password": "secret" }

    Response::

        {
            "access":  "<jwt_access_token>",
            "refresh": "<jwt_refresh_token>",
            "user": {
                "id":         "<uuid>",
                "email":      "user@example.com",
                "is_admin":   false,
                "tier":       3,
                "tier_label": "Analyst",
                "roles":      ["BI-RL-ANA"]
            }
        }
    """

    serializer_class = GRCTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc

        response_data: dict = dict(serializer.validated_data)
        user = serializer.user
        tier, tier_label = _user_tier(user)

        # Augment with a human-readable user summary
        response_data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "is_admin": user.is_admin(),
            "tier": tier,
            "tier_label": tier_label,
            "roles": user.get_roles(),
        }

        return Response(response_data, status=status.HTTP_200_OK)


class GRCTokenRefreshView(TokenRefreshView):
    """
    POST /api/iam/jwt/refresh/

    Exchange a valid refresh token for a new access token.
    When ``ROTATE_REFRESH_TOKENS`` is enabled the old refresh token is
    blacklisted and a new one is returned.

    Request body::

        { "refresh": "<refresh_token>" }
    """

    pass  # Inherits all refresh logic; rotation controlled via SIMPLE_JWT settings


class JWTTokenInfoView(APIView):
    """
    GET /api/iam/jwt/info/

    Returns the authenticated user's identity, privilege tier, current roles,
    and a subset of the JWT's own claims.

    Requires ``Authorization: Bearer <access_token>`` header.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = request.user
        tier, tier_label = _user_tier(user)

        # Expose a safe subset of the token's own claims for debugging / auditing
        token_claims: dict = {}
        if hasattr(request.auth, "payload"):
            safe_keys = {"exp", "iat", "jti", "token_type", "tier", "roles", "is_admin"}
            token_claims = {
                k: v for k, v in request.auth.payload.items() if k in safe_keys
            }

        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "is_admin": user.is_admin(),
                "tier": tier,
                "tier_label": tier_label,
                "roles": user.get_roles(),
                "token_claims": token_claims,
            }
        )


class JWTLogoutView(APIView):
    """
    POST /api/iam/jwt/logout/

    Blacklists the provided refresh token, preventing it from being used to
    issue further access tokens.  Returns 200 regardless (best-effort).

    Request body::

        { "refresh": "<refresh_token>" }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": _("Refresh token is required.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("jwt_token_blacklisted", user=request.user.email)
        except TokenError as exc:
            logger.warning("jwt_blacklist_failed", error=str(exc))

        return Response({"detail": _("Token successfully invalidated.")})


class JWTRoleHierarchyView(APIView):
    """
    GET /api/iam/jwt/roles/

    Public endpoint.  Returns the full platform role hierarchy with tier
    numbers, codenames, labels, responsibilities, and delegation rules.
    No authentication required.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        return Response({"hierarchy": ROLE_HIERARCHY})
