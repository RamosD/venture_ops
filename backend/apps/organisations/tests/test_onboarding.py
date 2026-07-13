"""Testes de onboarding, bloqueio de segunda empresa, edição e auditoria."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.organisations import service
from apps.organisations.models import Membership, Organisation

ONBOARDING = "/api/v1/onboarding"
ORGANISATION = "/api/v1/organisation"


def _login(client, email, password="senha-123"):
    client.post(
        "/api/v1/auth/login", {"email": email, "password": password}, format="json"
    )


class OnboardingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-123"
        )
        _login(self.client, "owner@x.pt")

    def test_first_entry_without_organisation_requires_onboarding(self):
        response = self.client.get(ORGANISATION)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["onboarding_required"])
        self.assertIsNone(response.json()["organisation"])

    def test_onboarding_creates_org_and_owner_membership(self):
        response = self.client.post(
            ONBOARDING, {"name": "Minha Empresa"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        org = Organisation.objects.get(name="Minha Empresa")
        self.assertEqual(org.status, Organisation.Status.ACTIVE)
        membership = Membership.objects.get(user=self.user, organisation=org)
        self.assertEqual(membership.role, Membership.Role.OWNER)
        self.assertTrue(membership.is_active)

    def test_onboarding_is_audited(self):
        self.client.post(ONBOARDING, {"name": "Empresa Auditada"}, format="json")
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.ORGANISATION_CREATED, actor=self.user
            ).exists()
        )

    def test_second_organisation_is_blocked(self):
        self.client.post(ONBOARDING, {"name": "Primeira"}, format="json")
        second = self.client.post(ONBOARDING, {"name": "Segunda"}, format="json")
        self.assertEqual(second.status_code, 409)
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertEqual(Membership.objects.filter(user=self.user).count(), 1)

    def test_onboarding_requires_name(self):
        response = self.client.post(ONBOARDING, {"name": "  "}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_onboarding_requires_authentication(self):
        anon = APIClient()
        self.assertIn(
            anon.post(ONBOARDING, {"name": "X"}, format="json").status_code,
            (401, 403),
        )


class OrganisationEditTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-123"
        )
        _login(self.client, "owner@x.pt")
        self.client.post(ONBOARDING, {"name": "Empresa Owner"}, format="json")
        self.org = Organisation.objects.get(name="Empresa Owner")

    def test_owner_edits_organisation(self):
        response = self.client.patch(
            ORGANISATION, {"name": "Empresa Renomeada"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.org.refresh_from_db()
        self.assertEqual(self.org.name, "Empresa Renomeada")

    def test_edit_is_audited(self):
        self.client.patch(ORGANISATION, {"name": "Nova"}, format="json")
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.ORGANISATION_UPDATED
            ).exists()
        )

    def test_other_user_cannot_edit_someone_elses_org(self):
        # Um segundo utilizador sem empresa não consegue editar a empresa alheia:
        # a operação deriva sempre da própria Membership.
        other_client = APIClient()
        get_user_model().objects.create_user(email="outro@x.pt", password="senha-123")
        _login(other_client, "outro@x.pt")
        response = other_client.patch(
            ORGANISATION, {"name": "Invadida"}, format="json"
        )
        # Sem Membership activa → 403 (sem contexto de empresa).
        self.assertEqual(response.status_code, 403)
        self.org.refresh_from_db()
        self.assertEqual(self.org.name, "Empresa Owner")


class OnboardingServiceTests(TestCase):
    def test_service_blocks_duplicate_sequentially(self):
        user = get_user_model().objects.create_user(
            email="a@x.pt", password="senha-123"
        )
        service.complete_onboarding(user, "Primeira")
        with self.assertRaises(service.AlreadyHasOrganisationError):
            service.complete_onboarding(user, "Segunda")
        self.assertEqual(Membership.objects.filter(user=user).count(), 1)
