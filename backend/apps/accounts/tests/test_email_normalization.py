"""Testes de normalização e unicidade case-insensitive do email (Parte A)."""
from importlib import import_module

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import PasswordResetToken

LOGIN = "/api/v1/auth/login"
RESET = "/api/v1/auth/password/reset-request"
PROFILE = "/api/v1/profile"


class EmailNormalizationTests(TestCase):
    def test_create_strips_and_lowercases(self):
        user = get_user_model().objects.create_user(
            email="  Owner@Example.COM  ", password="senha-mvp-forte-1"
        )
        self.assertEqual(user.email, "owner@example.com")

    def test_manager_blocks_case_variant(self):
        get_user_model().objects.create_user(
            email="owner@example.com", password="senha-mvp-forte-1"
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                get_user_model().objects.create_user(
                    email="OWNER@example.com", password="senha-mvp-forte-1"
                )

    def test_db_constraint_blocks_unnormalized_case_variant(self):
        # Insere um valor sem passar pela normalização do manager: a constraint
        # funcional Lower(email) tem de bloquear.
        get_user_model().objects.create_user(
            email="owner@example.com", password="senha-mvp-forte-1"
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                get_user_model()(email="OWNER@example.com").save()

    def test_login_is_case_insensitive(self):
        get_user_model().objects.create_user(
            email="owner@example.com", password="senha-mvp-forte-1"
        )
        response = APIClient().post(
            LOGIN,
            {"email": "  OWNER@Example.com ", "password": "senha-mvp-forte-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_recovery_is_case_insensitive(self):
        user = get_user_model().objects.create_user(
            email="owner@example.com", password="senha-mvp-forte-1"
        )
        response = APIClient().post(
            RESET, {"email": "OWNER@EXAMPLE.COM"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(PasswordResetToken.objects.filter(user=user).exists())

    def test_profile_email_collision_with_other_account(self):
        get_user_model().objects.create_user(
            email="other@example.com", password="senha-mvp-forte-1"
        )
        get_user_model().objects.create_user(
            email="owner@example.com", password="senha-mvp-forte-1"
        )
        client = APIClient()
        client.post(
            LOGIN,
            {"email": "owner@example.com", "password": "senha-mvp-forte-1"},
            format="json",
        )
        response = client.patch(
            PROFILE, {"email": "OTHER@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 400)


class MigrationCollisionLogicTests(TestCase):
    """Testa a lógica de detecção de colisão da migração 0003 (sem BD)."""

    def _migration_module(self):
        return import_module(
            "apps.accounts.migrations."
            "0003_ratelimitattempt_accounts_ra_created_47fe39_idx_and_more"
        )

    def _fake_apps(self, users):
        class FakeQS(list):
            def all(self):
                return self

            def order_by(self, *_a):
                return self

        class FakeModel:
            objects = FakeQS(users)

        class FakeApps:
            def get_model(self, *_a):
                return FakeModel

        return FakeApps()

    class _FakeUser:
        def __init__(self, pk, email):
            self.pk = pk
            self.email = email
            self.saved = False

        def save(self, update_fields=None):
            self.saved = True

    def test_detects_case_insensitive_collision(self):
        mod = self._migration_module()
        users = [self._FakeUser(1, "owner@x.pt"), self._FakeUser(2, "OWNER@x.pt")]
        with self.assertRaises(RuntimeError):
            mod.normalize_existing_emails(self._fake_apps(users), None)

    def test_normalizes_when_no_collision(self):
        mod = self._migration_module()
        user = self._FakeUser(1, "  Mixed@Case.PT ")
        mod.normalize_existing_emails(self._fake_apps([user]), None)
        self.assertEqual(user.email, "mixed@case.pt")
        self.assertTrue(user.saved)
