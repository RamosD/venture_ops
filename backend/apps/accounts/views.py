"""Autenticação backend: CSRF, login, sessão, logout, recuperação e perfil.

Sem registo público. Recuperação por token temporário de utilização única.
Rate limiting persistente (PostgreSQL) em login e recuperação. As mensagens de
erro não revelam se o email existe.
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts import passwords, rate_limit
from apps.audit.models import AuditAction, AuditResult
from apps.audit.service import record_event

GENERIC_RECOVERY_MESSAGE = (
    "Se existir uma conta com esse email, enviámos instruções de recuperação."
)


def _user_payload(user) -> dict:
    return {"id": str(user.pk), "email": user.email, "name": user.name}


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        return Response({"detail": "CSRF cookie definido."})


class LoginView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        email = (request.data.get("email") or "").strip()
        password = request.data.get("password") or ""
        key = rate_limit.make_key("login", email or "unknown")

        if rate_limit.is_blocked(
            key, settings.RATE_LIMIT_LOGIN_MAX, settings.RATE_LIMIT_LOGIN_WINDOW
        ):
            record_event(
                action=AuditAction.AUTH_FAILED,
                result=AuditResult.DENIED,
                metadata={"reason": "rate_limited", "scope": "login"},
            )
            return Response(
                {"detail": "Demasiadas tentativas. Tente novamente mais tarde."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(request, username=email, password=password)
        if user is None:
            rate_limit.register(key, settings.RATE_LIMIT_LOGIN_WINDOW)
            record_event(action=AuditAction.AUTH_FAILED, result=AuditResult.FAILURE)
            return Response(
                {"detail": "Credenciais inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        rate_limit.clear(key)  # sucesso limpa as falhas
        django_login(request, user)
        record_event(
            action=AuditAction.AUTH_LOGIN, actor=user, result=AuditResult.SUCCESS
        )
        return Response(_user_payload(user))


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        user = request.user
        django_logout(request)
        record_event(
            action=AuditAction.AUTH_LOGOUT, actor=user, result=AuditResult.SUCCESS
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        if request.user.is_authenticated:
            return Response(
                {"authenticated": True, "user": _user_payload(request.user)}
            )
        return Response({"authenticated": False})


class PasswordResetRequestView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        email = (request.data.get("email") or "").strip().lower()
        key = rate_limit.make_key("recovery", email or "unknown")

        if rate_limit.is_blocked(
            key,
            settings.RATE_LIMIT_RECOVERY_MAX,
            settings.RATE_LIMIT_RECOVERY_WINDOW,
        ):
            record_event(
                action=AuditAction.AUTH_FAILED,
                result=AuditResult.DENIED,
                metadata={"reason": "rate_limited", "scope": "recovery"},
            )
            return Response(
                {"detail": GENERIC_RECOVERY_MESSAGE},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        rate_limit.register(key, settings.RATE_LIMIT_RECOVERY_WINDOW)

        user = get_user_model().objects.filter(email__iexact=email).first()
        if user is not None:
            raw = passwords.create_reset_token(user)
            passwords.send_reset_email(user, raw)

        # Resposta idêntica exista ou não a conta (sem revelar existência).
        return Response({"detail": GENERIC_RECOVERY_MESSAGE})


class PasswordResetConfirmView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    @method_decorator(csrf_protect)
    def post(self, request: Request) -> Response:
        token = request.data.get("token") or ""
        new_password = request.data.get("new_password") or ""
        if len(new_password) < 8:
            return Response(
                {"detail": "A palavra-passe tem de ter pelo menos 8 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = passwords.consume_reset_token(token, new_password)
        if user is None:
            return Response(
                {"detail": "Token inválido, expirado ou já utilizado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Palavra-passe redefinida com sucesso."})


class ProfileView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(_user_payload(request.user))

    @method_decorator(csrf_protect)
    def patch(self, request: Request) -> Response:
        user = request.user  # sempre o próprio; não há forma de indicar outro
        name = request.data.get("name")
        email = request.data.get("email")

        if name is not None:
            user.name = str(name).strip()
        if email is not None:
            email = str(email).strip().lower()
            if (
                get_user_model()
                .objects.filter(email__iexact=email)
                .exclude(pk=user.pk)
                .exists()
            ):
                return Response(
                    {"detail": "Esse email já está em uso."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = email
        user.save()
        return Response(_user_payload(user))
