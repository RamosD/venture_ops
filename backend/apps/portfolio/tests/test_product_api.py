"""Testes da API inicial do portefólio (F1-P03-PR02).

Cobrem criação (só `name`+`purpose`), defaults no servidor, isolamento por
empresa (produto alheio → 404 indistinguível, tentativa cruzada auditada),
concorrência optimista (409 em versão obsoleta), regra de `last_reviewed_at`
(imune à edição comum), rejeição de produto arquivado e de responsável alheio, e
auditoria sem conteúdo sensível.
"""
from __future__ import annotations

import uuid

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


def _client_for(email):
    client = APIClient()
    client.post(
        "/api/v1/auth/login",
        {"email": email, "password": "senha-123"},
        format="json",
    )
    return client


class ProductApiTests(TestCase):
    def setUp(self):
        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")

    def _create(self, client, **payload):
        return client.post(PRODUCTS, payload, format="json")

    # 1 — Owner cria produto apenas com name e purpose
    def test_owner_creates_product_with_name_and_purpose_only(self):
        resp = self._create(self.client_a, name="Produto A", purpose="Propósito A")
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["name"], "Produto A")
        self.assertEqual(body["purpose"], "Propósito A")

    # 2 — defaults são aplicados no servidor
    def test_defaults_applied_on_server(self):
        body = self._create(
            self.client_a, name="P", purpose="Prop"
        ).json()
        self.assertEqual(body["status"], "active")
        self.assertEqual(body["version"], 1)
        self.assertEqual(body["responsible"], str(self.user_a.pk))
        self.assertEqual(body["organisation"], str(self.org_a.pk))
        self.assertIsNotNone(body["last_reviewed_at"])

    # 3 — organização não pode ser escolhida pelo cliente
    def test_client_cannot_choose_organisation(self):
        resp = self._create(
            self.client_a,
            name="P",
            purpose="Prop",
            organisation=str(self.org_b.pk),
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("organisation", resp.json())

    # 4 — listagem contém apenas produtos da empresa actual
    def test_list_only_contains_current_company_products(self):
        self._create(self.client_a, name="A1", purpose="p")
        self._create(self.client_b, name="B1", purpose="p")
        results = self.client_a.get(PRODUCTS).json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "A1")
        self.assertEqual(results[0]["organisation"], str(self.org_a.pk))

    # 5 — detalhe próprio funciona
    def test_own_detail_works(self):
        pid = self._create(self.client_a, name="A1", purpose="p").json()["id"]
        resp = self.client_a.get(f"{PRODUCTS}/{pid}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], pid)
        self.assertIn("version", resp.json())

    # 6 — produto alheio devolve 404 (indistinguível de inexistente)
    def test_foreign_product_returns_404(self):
        pid = self._create(self.client_b, name="B1", purpose="p").json()["id"]
        cross = self.client_a.get(f"{PRODUCTS}/{pid}")
        missing = self.client_a.get(f"{PRODUCTS}/{uuid.uuid4()}")
        self.assertEqual(cross.status_code, 404)
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(cross.json(), missing.json())  # respostas idênticas

    # 7 — tentativa cruzada é auditada
    def test_cross_attempt_is_audited(self):
        pid = self._create(self.client_b, name="B1", purpose="p").json()["id"]
        self.client_a.get(f"{PRODUCTS}/{pid}")
        event = AuditEvent.objects.filter(
            action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT, actor=self.user_a
        ).latest("created_at")
        self.assertEqual(event.organisation, self.org_a)  # contexto, não alvo
        self.assertEqual(event.entity_id, pid)
        self.assertEqual(event.entity_type, "product")
        self.assertIsNotNone(event.correlation_id)

    # 8 — edição válida incrementa version
    def test_valid_edit_increments_version(self):
        pid = self._create(self.client_a, name="A1", purpose="p").json()["id"]
        resp = self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "purpose": "novo propósito"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["version"], 2)
        self.assertEqual(resp.json()["purpose"], "novo propósito")

    # 9 — edição com versão obsoleta devolve 409
    def test_edit_with_stale_version_returns_409(self):
        pid = self._create(self.client_a, name="A1", purpose="p").json()["id"]
        self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "name": "v2"},
            format="json",
        )
        stale = self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "name": "v3"},  # versão já é 2
            format="json",
        )
        self.assertEqual(stale.status_code, 409)
        # Sem lost update: o nome permaneceu o da 1.ª edição.
        self.assertEqual(self.client_a.get(f"{PRODUCTS}/{pid}").json()["name"], "v2")

    # 10 — edição comum não altera last_reviewed_at
    def test_common_edit_does_not_change_last_reviewed_at(self):
        created = self._create(self.client_a, name="A1", purpose="p").json()
        pid, original = created["id"], created["last_reviewed_at"]
        edited = self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "notes": "nota"},
            format="json",
        ).json()
        self.assertEqual(edited["last_reviewed_at"], original)

    # 11 — produto archived não pode ser editado
    def test_archived_product_cannot_be_edited(self):
        pid = self._create(self.client_a, name="A1", purpose="p").json()["id"]
        Product.objects.filter(pk=pid).update(status=Product.Status.ARCHIVED)
        resp = self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "name": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 12 — responsável alheio é rejeitado
    def test_foreign_responsible_is_rejected(self):
        resp = self._create(
            self.client_a,
            name="A1",
            purpose="p",
            responsible=str(self.user_b.pk),  # utilizador da Empresa B
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("responsible", resp.json())

    # 13 — criação e edição são auditadas
    def test_create_and_edit_are_audited(self):
        pid = self._create(self.client_a, name="A1", purpose="p").json()["id"]
        self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "name": "A2"},
            format="json",
        )
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.PRODUCT_CREATED, entity_id=pid
            ).exists()
        )
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.PRODUCT_UPDATED, entity_id=pid
            ).exists()
        )

    # 14 — conteúdo integral da ficha não entra na auditoria
    def test_full_content_not_in_audit(self):
        secret_purpose = "PROPÓSITO SECRETO QUE NÃO DEVE SER AUDITADO"
        pid = self._create(
            self.client_a, name="A1", purpose=secret_purpose, notes="NOTA SECRETA"
        ).json()["id"]
        event = AuditEvent.objects.filter(
            action=AuditAction.PRODUCT_CREATED, entity_id=pid
        ).latest("created_at")
        serialized = str(event.metadata)
        self.assertNotIn(secret_purpose, serialized)
        self.assertNotIn("NOTA SECRETA", serialized)
        # Apenas operação e nomes de campos.
        self.assertEqual(event.metadata["operation"], "create")
        self.assertIn("purpose", event.metadata["fields"])  # nome, não valor

    # Extra — pedido sem Membership activa é rejeitado (403)
    def test_request_without_membership_is_rejected(self):
        get_user_model().objects.create_user(email="c@x.pt", password="senha-123")
        client_c = _client_for("c@x.pt")
        self.assertEqual(client_c.get(PRODUCTS).status_code, 403)
        self.assertEqual(
            self._create(client_c, name="X", purpose="p").status_code, 403
        )

    # Extra — edição de produto alheio devolve 404 (não expõe existência)
    def test_editing_foreign_product_returns_404(self):
        pid = self._create(self.client_b, name="B1", purpose="p").json()["id"]
        resp = self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "name": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    # Extra — status/version não são alteráveis pelo PATCH comum
    def test_status_and_version_are_not_patchable(self):
        pid = self._create(self.client_a, name="A1", purpose="p").json()["id"]
        resp = self.client_a.patch(
            f"{PRODUCTS}/{pid}",
            {"expected_version": 1, "status": "archived"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("status", resp.json())

    # Extra — nome vazio/só espaços é rejeitado na criação
    def test_blank_name_is_rejected(self):
        resp = self._create(self.client_a, name="   ", purpose="p")
        self.assertEqual(resp.status_code, 400)
