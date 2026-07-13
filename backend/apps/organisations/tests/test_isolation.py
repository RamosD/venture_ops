"""Bateria inicial de isolamento entre empresas (semente de MVP-18).

Cria dois utilizadores e duas empresas directamente (factories/fixtures). A
regra de uma empresa por conta na experiência do MVP não impede estes cenários
técnicos com vários utilizadores e empresas.
"""
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.organisations.models import Membership, Organisation

ORGANISATION = "/api/v1/organisation"


def _make_company(email, org_name, *, active=True):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(
        name=org_name, status=Organisation.Status.ACTIVE
    )
    Membership.objects.create(
        user=user,
        organisation=org,
        role=Membership.Role.OWNER,
        is_active=active,
    )
    return user, org


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json"
    )
    return client


class CompanyIsolationTests(TestCase):
    def setUp(self):
        self.user_a, self.org_a = _make_company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _make_company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")

    # 1 — contexto derivado da Membership
    def test_context_is_derived_from_membership(self):
        self.assertEqual(
            self.client_a.get(ORGANISATION).json()["organisation"]["name"],
            "Empresa A",
        )
        self.assertEqual(
            self.client_b.get(ORGANISATION).json()["organisation"]["name"],
            "Empresa B",
        )

    # 2 / 6 — cliente não troca de empresa por parâmetro (id alheio → 404)
    def test_cannot_switch_company_by_id(self):
        own = self.client_a.get(f"/api/v1/organisations/{self.org_a.pk}")
        cross = self.client_a.get(f"/api/v1/organisations/{self.org_b.pk}")
        self.assertEqual(own.status_code, 200)
        self.assertEqual(own.json()["name"], "Empresa A")
        self.assertEqual(cross.status_code, 404)

    # 4 — leitura cruzada falha e não revela existência
    def test_cross_read_does_not_reveal_existence(self):
        cross = self.client_a.get(f"/api/v1/organisations/{self.org_b.pk}")
        random = self.client_a.get(f"/api/v1/organisations/{uuid.uuid4()}")
        self.assertEqual(cross.status_code, 404)
        self.assertEqual(random.status_code, 404)
        self.assertEqual(cross.json(), random.json())  # respostas idênticas

    # 5 — alteração cruzada falha (A não afecta a empresa de B)
    def test_cross_alteration_is_impossible(self):
        self.client_a.patch(ORGANISATION, {"name": "Renomeada por A"}, format="json")
        self.org_b.refresh_from_db()
        self.assertEqual(self.org_b.name, "Empresa B")

    # 3 — pedido sem Membership é rejeitado (403)
    def test_request_without_membership_is_rejected(self):
        get_user_model().objects.create_user(email="c@x.pt", password="senha-123")
        client_c = _client_for("c@x.pt")
        self.assertEqual(
            client_c.get(f"/api/v1/organisations/{self.org_a.pk}").status_code, 403
        )
        self.assertEqual(
            client_c.patch(ORGANISATION, {"name": "X"}, format="json").status_code,
            403,
        )

    # 9 — Membership inactiva é tratada como sem contexto
    def test_inactive_membership_has_no_context(self):
        _user_d, _org_d = _make_company("d@x.pt", "Empresa D", active=False)
        client_d = _client_for("d@x.pt")
        self.assertTrue(client_d.get(ORGANISATION).json()["onboarding_required"])
        self.assertEqual(
            client_d.patch(ORGANISATION, {"name": "X"}, format="json").status_code,
            403,
        )

    # 7 — tentativas cruzadas são auditadas (evento, correlação, sem payload)
    def test_cross_attempt_is_audited(self):
        self.client_a.get(f"/api/v1/organisations/{self.org_b.pk}")
        event = AuditEvent.objects.filter(
            action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT, actor=self.user_a
        ).latest("created_at")
        self.assertEqual(event.organisation, self.org_a)  # contexto, não alvo
        self.assertEqual(event.entity_id, str(self.org_b.pk))
        self.assertIsNotNone(event.correlation_id)
        self.assertNotIn("password", str(event.metadata).lower())
        self.assertEqual(event.metadata, {"reason": "cross_org"})

    # 8 — acesso legítimo dentro da própria empresa funciona
    def test_legitimate_access_within_own_company(self):
        read = self.client_a.get(f"/api/v1/organisations/{self.org_a.pk}")
        edit = self.client_a.patch(
            ORGANISATION, {"name": "Empresa A v2"}, format="json"
        )
        self.assertEqual(read.status_code, 200)
        self.assertEqual(edit.status_code, 200)
        self.org_a.refresh_from_db()
        self.assertEqual(self.org_a.name, "Empresa A v2")
