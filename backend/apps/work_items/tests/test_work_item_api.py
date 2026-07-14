"""Testes da API de pendências (F1-P04-PR05).

Cobrem os cinco tipos, validações de enumeração, ciclo de vida (open→completed/
cancelled, finais imutáveis), vencimento calculado, isolamento (responsável/
produto/decisão alheios, coerência), filtros/paginação, concorrência e auditoria
(evento 9 sem conteúdo integral).
"""
from __future__ import annotations

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.decisions.models import Decision
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.work_items.models import WorkItem

ITEMS = "/api/v1/work-items"
NOTES_TOKEN = "ZZnotasUNICO4242"


def _company(email, org_name, *, active=True):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=org_name, status=Organisation.Status.ACTIVE)
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=active
    )
    return user, org


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json"
    )
    return client


class WorkItemApiTests(TestCase):
    def setUp(self):
        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")
        self.product_a = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="P", purpose="p"
        )
        self.product_b = Product.objects.create(
            organisation=self.org_b, responsible=self.user_b, name="PB", purpose="p"
        )

    def _payload(self, **over):
        data = {
            "product": str(self.product_a.pk),
            "title": "Rever contrato",
            "work_type": "obligation",
            "notes": f"Notas {NOTES_TOKEN}",
        }
        data.update(over)
        return data

    def _create(self, client=None, **over):
        return (client or self.client_a).post(
            ITEMS, self._payload(**over), format="json"
        )

    # 1 — criação com cada um dos cinco tipos
    def test_create_with_each_type(self):
        for wt in (
            "action",
            "review",
            "validation",
            "obligation",
            "decision_follow_up",
        ):
            resp = self._create(work_type=wt, title=f"Item {wt}")
            self.assertEqual(resp.status_code, 201, resp.content)
            self.assertEqual(resp.json()["work_type"], wt)
        self.assertEqual(WorkItem.objects.count(), 5)

    # 2 — tipo inválido rejeitado
    def test_invalid_type_rejected(self):
        resp = self._create(work_type="bug")
        self.assertEqual(resp.status_code, 400)

    # 3 — estado inicial open
    def test_initial_status_open(self):
        body = self._create().json()
        self.assertEqual(body["status"], "open")
        self.assertEqual(body["version"], 1)
        self.assertIsNone(body["completed_at"])
        self.assertIsNone(body["cancelled_at"])

    # 4 — prioridade inválida rejeitada
    def test_invalid_priority_rejected(self):
        resp = self._create(priority="urgent")
        self.assertEqual(resp.status_code, 400)

    # 4b — prioridade válida persiste (default medium)
    def test_priority_default_and_set(self):
        self.assertEqual(self._create().json()["priority"], "medium")
        self.assertEqual(self._create(priority="high").json()["priority"], "high")

    # 5 — prazo persistido
    def test_due_at_persisted(self):
        due = (timezone.now() + timedelta(days=3)).isoformat()
        body = self._create(due_at=due).json()
        self.assertIsNotNone(body["due_at"])

    # 6 — vencimento calculado para pendência open (prazo passado)
    def test_overdue_calculated_for_open(self):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        body = self._create(due_at=past).json()
        self.assertTrue(body["is_overdue"])

    # 6b — sem prazo nunca é vencida
    def test_no_due_never_overdue(self):
        self.assertFalse(self._create().json()["is_overdue"])

    # 7 — completed não é vencida
    def test_completed_not_overdue(self):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        created = self._create(due_at=past).json()
        done = self.client_a.post(
            f"{ITEMS}/{created['id']}/complete",
            {"expected_version": created["version"]},
            format="json",
        ).json()
        self.assertEqual(done["status"], "completed")
        self.assertFalse(done["is_overdue"])

    # 8 — cancelada não é vencida
    def test_cancelled_not_overdue(self):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        created = self._create(due_at=past).json()
        cancelled = self.client_a.post(
            f"{ITEMS}/{created['id']}/cancel",
            {"expected_version": created["version"]},
            format="json",
        ).json()
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertFalse(cancelled["is_overdue"])

    # 9 — conclusão válida
    def test_complete_valid(self):
        created = self._create().json()
        resp = self.client_a.post(
            f"{ITEMS}/{created['id']}/complete",
            {"expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "completed")
        self.assertIsNotNone(resp.json()["completed_at"])

    # 10 — cancelamento válido
    def test_cancel_valid(self):
        created = self._create().json()
        resp = self.client_a.post(
            f"{ITEMS}/{created['id']}/cancel",
            {"expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "cancelled")
        self.assertIsNotNone(resp.json()["cancelled_at"])

    # 11 — transição a partir de estado final devolve 409
    def test_transition_from_final_returns_409(self):
        created = self._create().json()
        self.client_a.post(
            f"{ITEMS}/{created['id']}/complete",
            {"expected_version": 1},
            format="json",
        )
        # Cancelar uma já concluída (v2) → 409.
        resp = self.client_a.post(
            f"{ITEMS}/{created['id']}/cancel",
            {"expected_version": 2},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 12 — edição de estado final é rejeitada
    def test_edit_final_rejected(self):
        created = self._create().json()
        self.client_a.post(
            f"{ITEMS}/{created['id']}/cancel", {"expected_version": 1}, format="json"
        )
        resp = self.client_a.patch(
            f"{ITEMS}/{created['id']}",
            {"title": "novo", "expected_version": 2},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 12b — edição enquanto open
    def test_edit_open(self):
        created = self._create().json()
        resp = self.client_a.patch(
            f"{ITEMS}/{created['id']}",
            {"title": "Rever contrato revisto", "priority": "high", "expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["title"], "Rever contrato revisto")
        self.assertEqual(resp.json()["priority"], "high")
        self.assertEqual(resp.json()["version"], 2)

    # 13 — responsável alheio rejeitado
    def test_foreign_responsible_rejected(self):
        resp = self._create(responsible=str(self.user_b.pk))
        self.assertEqual(resp.status_code, 400)

    # 14 — Product alheio rejeitado
    def test_foreign_product_rejected(self):
        resp = self._create(product=str(self.product_b.pk))
        self.assertEqual(resp.status_code, 400)

    # 15 — Decision alheia rejeitada
    def test_foreign_decision_rejected(self):
        foreign_decision = Decision.objects.create(
            organisation=self.org_b,
            responsible=self.user_b,
            title="D",
            context="c",
            decision_text="d",
        )
        resp = self._create(decision=str(foreign_decision.pk))
        self.assertEqual(resp.status_code, 400)

    # 16 — ligação Product–Decision incoerente rejeitada
    def test_incoherent_product_decision_rejected(self):
        other_product = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="Outro", purpose="p"
        )
        decision_other = Decision.objects.create(
            organisation=self.org_a,
            responsible=self.user_a,
            title="D",
            context="c",
            decision_text="d",
            product=other_product,
        )
        resp = self._create(
            product=str(self.product_a.pk), decision=str(decision_other.pk)
        )
        self.assertEqual(resp.status_code, 400)

    # 16b — decisão coerente (mesmo produto) é aceite
    def test_coherent_decision_accepted(self):
        decision = Decision.objects.create(
            organisation=self.org_a,
            responsible=self.user_a,
            title="D",
            context="c",
            decision_text="d",
            product=self.product_a,
        )
        resp = self._create(
            work_type="decision_follow_up", decision=str(decision.pk)
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["decision"], str(decision.pk))

    # 17 — filtros e paginação isolados
    def test_filters_isolated(self):
        self._create(work_type="action", title="A1")
        self._create(work_type="review", title="R1")
        # Isolamento: empresa B não vê nada.
        self.assertEqual(self.client_b.get(ITEMS).json()["count"], 0)
        # Filtro por tipo.
        self.assertEqual(
            self.client_a.get(f"{ITEMS}?work_type=action").json()["count"], 1
        )
        # Filtro por produto.
        self.assertEqual(
            self.client_a.get(f"{ITEMS}?product={self.product_a.pk}").json()["count"],
            2,
        )

    # 17b — filtro por vencimento
    def test_overdue_filter(self):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        future = (timezone.now() + timedelta(days=1)).isoformat()
        self._create(due_at=past, title="Vencida")
        self._create(due_at=future, title="Futura")
        resp = self.client_a.get(f"{ITEMS}?overdue=true").json()
        self.assertEqual(resp["count"], 1)
        self.assertEqual(resp["results"][0]["title"], "Vencida")

    # detalhe alheio → 404 auditado
    def test_foreign_detail_404_audited(self):
        created = self._create().json()
        resp = self.client_b.get(f"{ITEMS}/{created['id']}")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
                entity_type="work_item",
                entity_id=created["id"],
            ).exists()
        )

    # versão obsoleta → 409
    def test_version_conflict(self):
        created = self._create().json()
        resp = self.client_a.post(
            f"{ITEMS}/{created['id']}/complete",
            {"expected_version": 999},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 19/20 — operações auditadas; sem conteúdo integral
    def test_audit_events_and_no_content(self):
        created = self._create().json()
        self.client_a.patch(
            f"{ITEMS}/{created['id']}",
            {"notes": f"outras {NOTES_TOKEN}", "expected_version": 1},
            format="json",
        )
        self.client_a.post(
            f"{ITEMS}/{created['id']}/complete", {"expected_version": 2}, format="json"
        )
        actions = list(
            AuditEvent.objects.filter(entity_type="work_item").values_list(
                "action", flat=True
            )
        )
        self.assertEqual(actions.count(AuditAction.WORK_ITEM_CREATED), 1)
        self.assertEqual(actions.count(AuditAction.WORK_ITEM_UPDATED), 2)  # edição + conclusão
        for event in AuditEvent.objects.all():
            self.assertNotIn(NOTES_TOKEN, str(event.metadata))

    # sem DELETE
    def test_no_delete(self):
        created = self._create().json()
        self.assertEqual(
            self.client_a.delete(f"{ITEMS}/{created['id']}").status_code, 405
        )

    # sem contexto de empresa → 403
    def test_requires_company_context(self):
        get_user_model().objects.create_user(email="solo@x.pt", password="senha-123")
        client = _client_for("solo@x.pt")
        self.assertEqual(client.get(ITEMS).status_code, 403)
