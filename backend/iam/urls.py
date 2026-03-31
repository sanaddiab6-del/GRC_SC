import knox.views as knox_views  # type: ignore[import-untyped]
from django.urls import include, path

from .views import (
    AuthTokenDetailView,
    PersonalAccessTokenViewSet,
    ChangePasswordView,
    CurrentUserView,
    LoginView,
    PasswordResetView,
    RegistrationRequestCountView,
    RegistrationRequestCreateView,
    RegistrationRequestDetailView,
    RegistrationRequestListView,
    RegistrationRequestReviewView,
    ResetPasswordConfirmView,
    SessionTokenView,
    SetPasswordView,
    RevokeOtherSessionsView,
)
from .jwt_auth import (
    GRCTokenObtainPairView,
    GRCTokenRefreshView,
    JWTTokenInfoView,
    JWTLogoutView,
    JWTRoleHierarchyView,
)

urlpatterns = [
    path(r"login/", LoginView.as_view(), name="knox_login"),
    path(r"logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(r"logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset/confirm/",
        ResetPasswordConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("set-password/", SetPasswordView.as_view(), name="set-password"),
    path("revoke-sessions/", RevokeOtherSessionsView.as_view()),
    path("sso/", include("iam.sso.urls")),
    path(
        "session-token/",
        SessionTokenView.as_view(),
        name="session-token",
    ),
    path("auth-tokens/", PersonalAccessTokenViewSet.as_view(), name="auth-tokens"),
    path(
        "auth-tokens/<str:pk>/",
        AuthTokenDetailView.as_view(),
        name="auth-token-detail",
    ),
    # ── JWT endpoints ────────────────────────────────────────────────────────
    # Uses Bearer tokens; does not affect existing Knox (Token) auth flows.
    path("jwt/token/", GRCTokenObtainPairView.as_view(), name="jwt-token-obtain"),
    path("jwt/refresh/", GRCTokenRefreshView.as_view(), name="jwt-token-refresh"),
    path("jwt/logout/", JWTLogoutView.as_view(), name="jwt-logout"),
    path("jwt/info/", JWTTokenInfoView.as_view(), name="jwt-token-info"),
    path("jwt/roles/", JWTRoleHierarchyView.as_view(), name="jwt-role-hierarchy"),
    # ── Registration / onboarding ────────────────────────────────────────────
    path(
        "registration-requests/",
        RegistrationRequestCreateView.as_view(),
        name="registration-request-create",
    ),
    path(
        "registration-requests/list/",
        RegistrationRequestListView.as_view(),
        name="registration-request-list",
    ),
    path(
        "registration-requests/<uuid:pk>/",
        RegistrationRequestDetailView.as_view(),
        name="registration-request-detail",
    ),
    path(
        "registration-requests/<uuid:pk>/review/",
        RegistrationRequestReviewView.as_view(),
        name="registration-request-review",
    ),
    path(
        "registration-requests/count/",
        RegistrationRequestCountView.as_view(),
        name="registration-request-count",
    ),
]
