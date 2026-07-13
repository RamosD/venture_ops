"""Testes do rate limiting persistente de login e recuperação."""
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts import rate_limit
from apps.accounts.models import RateLimitAttempt
from apps.audit.models import AuditAction, AuditEvent

LOGIN = "/api/v1/auth/login"


@override_settings(RATE_LIMIT_LOGIN_MAX=3, RATE_LIMIT_LOGIN_WINDOW=300)
class LoginRateLimitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-correcta-123"
        )

    def _bad_login(self):
        return self.client.post(
            LOGIN, {"email": "owner@x.pt", "password": "errada"}, format="json"
        )

    def test_blocks_after_threshold(self):
        for _ in range(3):
            self.assertEqual(self._bad_login().status_code, 401)
        # A 4.ª tentativa é bloqueada pelo rate limit.
        blocked = self._bad_login()
        self.assertEqual(blocked.status_code, 429)

    def test_repeated_failures_are_audited(self):
        for _ in range(3):
            self._bad_login()
        self._bad_login()  # bloqueada
        denied = AuditEvent.objects.filter(
            action=AuditAction.AUTH_FAILED, result="denied"
        )
        self.assertTrue(denied.exists())
        self.assertEqual(denied.first().metadata.get("reason"), "rate_limited")

    def test_successful_login_clears_failures(self):
        self._bad_login()
        self._bad_login()
        ok = self.client.post(
            LOGIN, {"email": "owner@x.pt", "password": "senha-correcta-123"},
            format="json",
        )
        self.assertEqual(ok.status_code, 200)
        # Após sucesso, as falhas anteriores foram limpas.
        key = rate_limit.make_key("login", "owner@x.pt")
        self.assertEqual(RateLimitAttempt.objects.filter(key=key).count(), 0)


class RateLimitWindowTests(TestCase):
    """Verifica a janela deslizante e a recuperação após expirar."""

    def test_window_expires_and_access_recovers(self):
        key = rate_limit.make_key("login", "a@x.pt")
        for _ in range(5):
            rate_limit.register(key)
        self.assertTrue(rate_limit.is_blocked(key, limit=5, window_seconds=300))
        # Janela de 0s: nenhuma tentativa cai dentro da janela → recupera.
        self.assertFalse(rate_limit.is_blocked(key, limit=5, window_seconds=0))

    def test_key_is_hashed_no_raw_identifier(self):
        key = rate_limit.make_key("login", "Owner@X.pt")
        self.assertTrue(key.startswith("login:"))
        self.assertNotIn("owner@x.pt", key)
        self.assertEqual(len(key.split(":")[1]), 64)  # sha256 hex
