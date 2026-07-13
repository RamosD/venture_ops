"""Testes de ciclo de vida, revisão explícita, filtros e paginação (F1-P03-PR04).

Cobrem arquivo/reactivação, "marcar como revisto" (única fonte de actualização de
`last_reviewed_at` — CLR-02), concorrência optimista por operação, filtros
(estado/responsável) isolados por empresa, paginação estável e auditoria sem
conteúdo integral.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product

PRODUCTS = "/api/v1/products"


def _company(email, org_name, *, active=True):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(
        name=org_name, status=Organisation.Status.ACTIVE
    )
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=active
    )
    return user, org


def _member(email, organisation):
    """Cria um utilizador com Membership activa numa empresa existente."""
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    Membership.objects.create(
        user=user, organisation=organisation, role=Membership.Role.OWNER, is_active=True
    )
    return user


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": "senha-123"},
        format="json",
    )
    return client


class ProductLifecycleTests(TestCase):
    def setUp(self):
        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.client_a = _client_for("a@x.pt")

    def _create(self, client=None, **payload):
        client = client or self.client_a
        payload.setdefault("name", "Produto")
        payload.setdefault("purpose", "Propósito")
        return client.post(PRODUCTS, payload, format="json").json()

    def _archive(self, pid, version):
        return self.client_a.post(
            f"{PRODUCTS}/{pid}/archive", {"expected_version": version}, format="json"
        )

    def _reactivate(self, pid, version):
        return self.client_a.post(
            f"{PRODUCTS}/{pid}/reactivate", {"expected_version": version}, format="json"
        )

    def _mark_reviewed(self, pid, version):
        return self.client_a.post(
            f"{PRODUCTS}/{pid}/mark-reviewed",
            {"expected_version": version},
            format="json",
        )

    # 1 — active pode ser archived
    def test_active_can_be_archived(self):
        p = self._create()
        resp = self._archive(p["id"], 1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "archived")
        self.assertEqual(resp.json()["version"], 2)

    # 2 — archived não pode ser arquivado novamente
    def test_archived_cannot_be_archived_again(self):
        p = self._create()
        self._archive(p["id"], 1)
        resp = self._archive(p["id"], 2)
        self.assertEqual(resp.status_code, 409)

    # 3 — archived pode ser reactivado
    def test_archived_can_be_reactivated(self):
        p = self._create()
        self._archive(p["id"], 1)
        resp = self._reactivate(p["id"], 2)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "active")
        self.assertEqual(resp.json()["version"], 3)

    # 4 — active não pode ser reactivado
    def test_active_cannot_be_reactivated(self):
        p = self._create()
        resp = self._reactivate(p["id"], 1)
        self.assertEqual(resp.status_code, 409)

    # 5 — versão obsoleta falha em cada comando
    def test_stale_version_fails_on_each_command(self):
        p = self._create()
        pid = p["id"]
        # archive avança a versão para 2; comandos com expected_version=1 são obsoletos.
        self._archive(pid, 1)
        self.assertEqual(self._archive(pid, 1).status_code, 409)
        self.assertEqual(self._reactivate(pid, 1).status_code, 409)
        # reactiva (versão 2 → 3) para testar mark-reviewed com versão obsoleta.
        self._reactivate(pid, 2)
        self.assertEqual(self._mark_reviewed(pid, 1).status_code, 409)

    # 6 — arquivo não apaga o produto
    def test_archive_does_not_delete(self):
        p = self._create()
        self._archive(p["id"], 1)
        self.assertTrue(Product.objects.filter(pk=p["id"]).exists())

    # 7 — arquivo não altera last_reviewed_at
    def test_archive_does_not_change_last_reviewed_at(self):
        p = self._create()
        resp = self._archive(p["id"], 1)
        self.assertEqual(resp.json()["last_reviewed_at"], p["last_reviewed_at"])

    # 8 — reactivação não altera last_reviewed_at
    def test_reactivate_does_not_change_last_reviewed_at(self):
        p = self._create()
        self._archive(p["id"], 1)
        resp = self._reactivate(p["id"], 2)
        self.assertEqual(resp.json()["last_reviewed_at"], p["last_reviewed_at"])

    # 9 — edição comum não altera last_reviewed_at
    def test_common_edit_does_not_change_last_reviewed_at(self):
        p = self._create()
        resp = self.client_a.patch(
            f"{PRODUCTS}/{p['id']}",
            {"expected_version": 1, "notes": "nota"},
            format="json",
        )
        self.assertEqual(resp.json()["last_reviewed_at"], p["last_reviewed_at"])

    # 10 — mark-reviewed altera last_reviewed_at
    def test_mark_reviewed_changes_last_reviewed_at(self):
        p = self._create()
        resp = self._mark_reviewed(p["id"], 1)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.json()["last_reviewed_at"], p["last_reviewed_at"])
        self.assertGreater(resp.json()["last_reviewed_at"], p["last_reviewed_at"])

    # 11 — mark-reviewed incrementa version
    def test_mark_reviewed_increments_version(self):
        p = self._create()
        resp = self._mark_reviewed(p["id"], 1)
        self.assertEqual(resp.json()["version"], 2)

    # 12 — archived não pode ser marcado como revisto
    def test_archived_cannot_be_marked_reviewed(self):
        p = self._create()
        self._archive(p["id"], 1)
        resp = self._mark_reviewed(p["id"], 2)
        self.assertEqual(resp.status_code, 409)

    # 13 / 14 — filtro por estado (active / archived)
    def test_status_filters(self):
        p1 = self._create(name="Activo")
        p2 = self._create(name="Arquivar")
        self._archive(p2["id"], 1)

        active = self.client_a.get(f"{PRODUCTS}?status=active").json()["results"]
        archived = self.client_a.get(f"{PRODUCTS}?status=archived").json()["results"]
        all_ = self.client_a.get(f"{PRODUCTS}?status=all").json()["results"]
        default = self.client_a.get(PRODUCTS).json()["results"]

        self.assertEqual({r["id"] for r in active}, {p1["id"]})
        self.assertEqual({r["id"] for r in archived}, {p2["id"]})
        self.assertEqual({r["id"] for r in all_}, {p1["id"], p2["id"]})
        self.assertEqual({r["id"] for r in default}, {p1["id"]})  # default = active

    # 15 — filtro por responsável funciona
    def test_responsible_filter(self):
        other = _member("colega@x.pt", self.org_a)
        mine = self._create(name="Meu")
        theirs = self._create(name="Dele", responsible=str(other.pk))

        results = self.client_a.get(
            f"{PRODUCTS}?responsible={other.pk}"
        ).json()["results"]
        self.assertEqual({r["id"] for r in results}, {theirs["id"]})
        self.assertNotIn(mine["id"], {r["id"] for r in results})

    # 16 — paginação é estável e determinística
    def test_pagination_is_stable(self):
        created = {self._create(name=f"P{i}")["id"] for i in range(3)}
        page1 = self.client_a.get(f"{PRODUCTS}?page=1&page_size=2").json()
        page2 = self.client_a.get(f"{PRODUCTS}?page=2&page_size=2").json()

        self.assertEqual(page1["count"], 3)
        self.assertEqual(page1["num_pages"], 2)
        self.assertEqual(len(page1["results"]), 2)
        self.assertEqual(len(page2["results"]), 1)
        ids1 = {r["id"] for r in page1["results"]}
        ids2 = {r["id"] for r in page2["results"]}
        self.assertEqual(ids1 & ids2, set())  # sem sobreposição
        self.assertEqual(ids1 | ids2, created)  # cobertura total

    # 17 — filtro não expõe produtos de outra empresa
    def test_filters_do_not_leak_across_companies(self):
        _user_b, _org_b = _company("b@x.pt", "Empresa B")
        client_b = _client_for("b@x.pt")
        foreign = client_b.post(
            PRODUCTS, {"name": "B1", "purpose": "p"}, format="json"
        ).json()
        mine = self._create(name="A1")

        all_a = self.client_a.get(f"{PRODUCTS}?status=all").json()["results"]
        ids = {r["id"] for r in all_a}
        self.assertIn(mine["id"], ids)
        self.assertNotIn(foreign["id"], ids)

    # 18 — operações de ciclo de vida são auditadas
    def test_lifecycle_operations_are_audited(self):
        p = self._create()
        pid = p["id"]
        self._archive(pid, 1)
        self._reactivate(pid, 2)
        self._mark_reviewed(pid, 3)

        archived = AuditEvent.objects.filter(
            action=AuditAction.PRODUCT_ARCHIVED, entity_id=pid
        ).latest("created_at")
        self.assertEqual(archived.metadata["operation"], "archive")

        reactivated = AuditEvent.objects.filter(
            entity_id=pid, metadata__operation="reactivate"
        )
        reviewed = AuditEvent.objects.filter(
            entity_id=pid, metadata__operation="mark_reviewed"
        )
        self.assertTrue(reactivated.exists())
        self.assertTrue(reviewed.exists())
        # Reactivação e revisão usam a acção agregada PRODUCT_UPDATED.
        self.assertEqual(
            reactivated.first().action, AuditAction.PRODUCT_UPDATED
        )
        self.assertEqual(reviewed.first().action, AuditAction.PRODUCT_UPDATED)

    # 19 — conteúdo integral não entra na auditoria das operações de ciclo de vida
    def test_full_content_not_in_lifecycle_audit(self):
        secret = "PROPOSITO SECRETO QUE NAO PODE SER AUDITADO"
        p = self._create(purpose=secret, notes="NOTA SECRETA")
        self._mark_reviewed(p["id"], 1)
        event = AuditEvent.objects.filter(
            entity_id=p["id"], metadata__operation="mark_reviewed"
        ).latest("created_at")
        serialized = str(event.metadata)
        self.assertNotIn(secret, serialized)
        self.assertNotIn("NOTA SECRETA", serialized)
        self.assertEqual(event.metadata["fields"], ["last_reviewed_at"])

    # Extra — operações de ciclo de vida rejeitam campo organisation (400)
    def test_lifecycle_rejects_unknown_fields(self):
        p = self._create()
        resp = self.client_a.post(
            f"{PRODUCTS}/{p['id']}/archive",
            {"expected_version": 1, "organisation": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    # Extra — operação de ciclo de vida sobre produto alheio devolve 404
    def test_lifecycle_on_foreign_product_returns_404(self):
        _user_b, _org_b = _company("b2@x.pt", "Empresa B2")
        client_b = _client_for("b2@x.pt")
        foreign = client_b.post(
            PRODUCTS, {"name": "B", "purpose": "p"}, format="json"
        ).json()
        resp = self._archive(foreign["id"], 1)
        self.assertEqual(resp.status_code, 404)

    # Extra — campos opcionais permanecem editáveis, sem obrigatoriedade
    def test_optional_fields_editable(self):
        p = self._create()
        resp = self.client_a.patch(
            f"{PRODUCTS}/{p['id']}",
            {
                "expected_version": 1,
                "target_audience": "Fundadores",
                "phase": "operação",
                "next_review_at": "2026-09-01T00:00:00Z",
                "notes": "acompanhar",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["target_audience"], "Fundadores")
        self.assertEqual(body["phase"], "operação")
        self.assertEqual(body["notes"], "acompanhar")
        self.assertTrue(body["next_review_at"].startswith("2026-09-01"))

    # Extra — data inválida em campo opcional é rejeitada (400)
    def test_invalid_optional_date_rejected(self):
        p = self._create()
        resp = self.client_a.patch(
            f"{PRODUCTS}/{p['id']}",
            {"expected_version": 1, "next_review_at": "não-é-data"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    # Extra — status inválido no filtro devolve 400
    def test_invalid_status_filter_rejected(self):
        resp = self.client_a.get(f"{PRODUCTS}?status=deleted")
        self.assertEqual(resp.status_code, 400)
