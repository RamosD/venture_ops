"""Rotas de autenticação (montadas sob /api/v1/auth/)."""
from django.urls import path

from apps.accounts.views import (
    CsrfView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SessionView,
)

urlpatterns = [
    path("csrf", CsrfView.as_view(), name="auth-csrf"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
    path("session", SessionView.as_view(), name="auth-session"),
    path(
        "password/reset-request",
        PasswordResetRequestView.as_view(),
        name="auth-password-reset-request",
    ),
    path(
        "password/reset-confirm",
        PasswordResetConfirmView.as_view(),
        name="auth-password-reset-confirm",
    ),
]
