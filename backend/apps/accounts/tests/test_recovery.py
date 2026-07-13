"""Testes de recuperação de acesso (token temporário de utilização única)."""
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts import passwords
from apps.accounts.models import PasswordResetToken

RR = "/api/v1/auth/password/reset-request"
RC = "/api/v1/auth/password/reset-confirm"


class PasswordRecoveryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-antiga-123"
        )

    def test_request_does_not_reveal_account_existence(self):
        existing = self.client.post(RR, {"email": "owner@x.pt"}, format="json")
        missing = self.client.post(RR, {"email": "naoexiste@x.pt"}, format="json")
        self.assertEqual(existing.status_code, 200)
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(existing.json(), missing.json())

    def test_valid_token_resets_password(self):
        raw = passwords.create_reset_token(self.user)
        response = self.client.post(
            RC, {"token": raw, "new_password": "nova-senha-forte-1"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("nova-senha-forte-1"))

    def test_expired_token_is_rejected(self):
        with override_settings(PASSWORD_RESET_TTL_SECONDS=-1):
            raw = passwords.create_reset_token(self.user)  # já expirado
        response = self.client.post(
            RC, {"token": raw, "new_password": "nova-senha-forte-1"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_reused_token_is_rejected(self):
        raw = passwords.create_reset_token(self.user)
        first = self.client.post(
            RC, {"token": raw, "new_password": "nova-senha-forte-1"}, format="json"
        )
        second = self.client.post(
            RC, {"token": raw, "new_password": "outra-senha-forte-2"}, format="json"
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 400)

    def test_reset_invalidates_previous_sessions(self):
        # Sessão activa do utilizador.
        logged = APIClient()
        logged.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "senha-antiga-123"},
            format="json",
        )
        self.assertTrue(logged.get("/api/v1/auth/session").json()["authenticated"])

        # Redefinição a partir de outro cliente (anónimo).
        raw = passwords.create_reset_token(self.user)
        self.client.post(
            RC, {"token": raw, "new_password": "nova-senha-forte-1"}, format="json"
        )

        # A sessão anterior deixa de ser válida (hash de sessão mudou).
        self.assertFalse(logged.get("/api/v1/auth/session").json()["authenticated"])

    def test_only_hash_is_stored(self):
        raw = passwords.create_reset_token(self.user)
        token = PasswordResetToken.objects.get(user=self.user)
        self.assertNotEqual(token.token_hash, raw)
        self.assertEqual(len(token.token_hash), 64)
