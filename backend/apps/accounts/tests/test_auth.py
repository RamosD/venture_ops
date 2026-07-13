"""Testes da autenticação backend (login/sessão/logout, CSRF, auditoria)."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="owner@x.pt", password="uma-pw-forte-123", name="Dono"
        )

    def test_login_valid_creates_session(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "uma-pw-forte-123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "owner@x.pt")
        self.assertIn("sessionid", response.cookies)

    def test_login_invalid_is_rejected_without_detail(self):
        wrong_pw = self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "errada"},
            format="json",
        )
        unknown = self.client.post(
            "/api/v1/auth/login",
            {"email": "naoexiste@x.pt", "password": "seja-o-que-for"},
            format="json",
        )
        self.assertEqual(wrong_pw.status_code, 401)
        self.assertEqual(unknown.status_code, 401)
        # Mensagem idêntica: não permite enumeração de emails.
        self.assertEqual(wrong_pw.json(), unknown.json())
        self.assertEqual(wrong_pw.json()["detail"], "Credenciais inválidas.")

    def test_session_cookie_has_secure_flags(self):
        response = self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "uma-pw-forte-123"},
            format="json",
        )
        cookie = response.cookies["sessionid"]
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")

    def test_session_returns_current_user_when_authenticated(self):
        self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "uma-pw-forte-123"},
            format="json",
        )
        response = self.client.get("/api/v1/auth/session")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["authenticated"])
        self.assertEqual(body["user"]["email"], "owner@x.pt")

    def test_session_anonymous_when_not_authenticated(self):
        response = self.client.get("/api/v1/auth/session")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["authenticated"])

    def test_logout_invalidates_session(self):
        self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "uma-pw-forte-123"},
            format="json",
        )
        logout = self.client.post("/api/v1/auth/logout")
        self.assertEqual(logout.status_code, 204)
        session = self.client.get("/api/v1/auth/session")
        self.assertFalse(session.json()["authenticated"])

    def test_login_audits_success_event_without_secrets(self):
        self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "uma-pw-forte-123"},
            format="json",
        )
        event = AuditEvent.objects.filter(action=AuditAction.AUTH_LOGIN).latest(
            "created_at"
        )
        self.assertEqual(event.actor, self.user)
        # Nenhum segredo/palavra-passe nos metadados.
        self.assertNotIn("password", str(event.metadata).lower())
        self.assertEqual(event.metadata, {})

    def test_failed_login_is_audited(self):
        self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "errada"},
            format="json",
        )
        self.assertTrue(
            AuditEvent.objects.filter(action=AuditAction.AUTH_FAILED).exists()
        )


class CsrfEnforcementTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            email="owner@x.pt", password="uma-pw-forte-123"
        )

    def test_login_requires_csrf_token(self):
        enforcing = APIClient(enforce_csrf_checks=True)
        response = enforcing.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "uma-pw-forte-123"},
            format="json",
        )
        # Sem token CSRF, a operação mutável é rejeitada.
        self.assertEqual(response.status_code, 403)

    def test_csrf_endpoint_sets_cookie(self):
        response = self.client.get("/api/v1/auth/csrf")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)


class NoPublicRegistrationTests(TestCase):
    def test_no_registration_or_password_reset_endpoint(self):
        from django.urls import Resolver404, resolve

        for path in [
            "/api/v1/auth/register",
            "/api/v1/auth/signup",
            "/api/v1/auth/password/reset",
        ]:
            with self.assertRaises(Resolver404):
                resolve(path)
