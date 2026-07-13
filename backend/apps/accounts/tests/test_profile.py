"""Testes do perfil mínimo (consulta/edição do próprio utilizador)."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

PROFILE = "/api/v1/profile"


class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-123", name="Dono"
        )
        self.other = get_user_model().objects.create_user(
            email="outro@x.pt", password="senha-123", name="Outro"
        )
        self.client.post(
            "/api/v1/auth/login",
            {"email": "owner@x.pt", "password": "senha-123"},
            format="json",
        )

    def test_requires_authentication(self):
        anon = APIClient()
        self.assertIn(anon.get(PROFILE).status_code, (401, 403))

    def test_returns_own_profile(self):
        response = self.client.get(PROFILE)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "owner@x.pt")

    def test_edits_own_name(self):
        response = self.client.patch(PROFILE, {"name": "Novo Nome"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Novo Nome")

    def test_email_uniqueness_enforced(self):
        response = self.client.patch(
            PROFILE, {"email": "outro@x.pt"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "owner@x.pt")

    def test_can_only_edit_self(self):
        # O endpoint opera sempre sobre request.user; alterar o nome não afecta
        # o outro utilizador.
        self.client.patch(PROFILE, {"name": "Alterado"}, format="json")
        self.other.refresh_from_db()
        self.assertEqual(self.other.name, "Outro")
