"""Isolamento entre empresas do módulo Product (F1-P03-PR06).

Consolida a prova de que **todas** as operações sobre um produto de outra empresa
falham com 404 indistinguível de inexistente e são **auditadas** como tentativa
de acesso cruzado (`security.cross_org_attempt`), incluindo as operações de ciclo
de vida (arquivo/reactivação/revisão) introduzidas em PR04.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.organisations.models import Membership, Organisation

PRODUCTS = "/api/v1/products"


def _company(email, org_name):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(
        name=org_name, status=Organisation.Status.ACTIVE
    )
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": "senha-123"},
        format="json",
    )
    return client


class ProductCrossOrgIsolationTests(TestCase):
    def setUp(self):
        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")
        # Produto pertencente à Empresa B.
        self.foreign = self.client_b.post(
            PRODUCTS, {"name": "B1", "purpose": "propósito de B"}, format="json"
        ).json()

    def _cross_events(self):
        return AuditEvent.objects.filter(
            action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
            actor=self.user_a,
            entity_id=self.foreign["id"],
        )

    def test_listing_does_not_mix_companies(self):
        results = self.client_a.get(f"{PRODUCTS}?status=all").json()["results"]
        self.assertEqual(results, [])  # A não vê o produto de B

    def test_foreign_detail_returns_404_and_is_audited(self):
        resp = self.client_a.get(f"{PRODUCTS}/{self.foreign['id']}")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(self._cross_events().exists())

    def test_foreign_edit_returns_404_and_is_audited(self):
        resp = self.client_a.patch(
            f"{PRODUCTS}/{self.foreign['id']}",
            {"expected_version": 1, "name": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(self._cross_events().exists())

    def test_foreign_archive_returns_404_and_is_audited(self):
        resp = self.client_a.post(
            f"{PRODUCTS}/{self.foreign['id']}/archive",
            {"expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(self._cross_events().exists())

    def test_foreign_reactivate_returns_404_and_is_audited(self):
        resp = self.client_a.post(
            f"{PRODUCTS}/{self.foreign['id']}/reactivate",
            {"expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(self._cross_events().exists())

    def test_foreign_mark_reviewed_returns_404_and_is_audited(self):
        resp = self.client_a.post(
            f"{PRODUCTS}/{self.foreign['id']}/mark-reviewed",
            {"expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(self._cross_events().exists())

    def test_cross_event_carries_context_and_correlation(self):
        self.client_a.post(
            f"{PRODUCTS}/{self.foreign['id']}/archive",
            {"expected_version": 1},
            format="json",
        )
        event = self._cross_events().latest("created_at")
        self.assertEqual(event.organisation, self.org_a)  # empresa do contexto, não a alvo
        self.assertEqual(event.entity_type, "product")
        self.assertIsNotNone(event.correlation_id)
        # Sem conteúdo sensível: apenas o motivo.
        self.assertEqual(event.metadata, {"reason": "cross_org"})

    def test_foreign_product_is_not_modified_by_cross_attempts(self):
        # Nenhuma tentativa cruzada altera o produto de B.
        for path in ("", "/archive", "/reactivate", "/mark-reviewed"):
            self.client_a.post(
                f"{PRODUCTS}/{self.foreign['id']}{path}",
                {"expected_version": 1},
                format="json",
            )
        current = self.client_b.get(f"{PRODUCTS}/{self.foreign['id']}").json()
        self.assertEqual(current["status"], "active")
        self.assertEqual(current["version"], 1)
