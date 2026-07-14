"""Testes da API de decisões (F1-P04-PR04).

Cobrem criação (empresarial e associada), isolamento (responsável/produto/
documento alheios, tipo errado, listagem/detalhe isolados), substituição (nova
decisão active, anterior superseded, cadeia navegável, não substituir duas
vezes, histórico preservado) e auditoria (evento 8 sem conteúdo integral).
"""
from __future__ import annotations

import shutil
import tempfile
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.decisions.models import Decision
from apps.documents.models import Document, DocumentType, DocumentVersion
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product

DECISIONS = "/api/v1/decisions"
CONTEXT_TOKEN = "ZZctxUNICO4242"
DECISION_TOKEN = "ZZdecUNICO4242"


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


def _document(org, product=None, *, doc_type=DocumentType.DETAILED_DECISION):
    """Cria um Document real (com versão 1) directamente na BD."""
    doc = Document.objects.create(
        organisation=org, product=product, title="Detalhe", document_type=doc_type
    )
    version = DocumentVersion.objects.create(
        document=doc,
        version_number=1,
        storage_key="ab/0123456789abcdef0123456789ab",
        checksum="a" * 64,
        byte_size=10,
        author=org.memberships.first().user,
    )
    doc.current_version = version
    doc.save(update_fields=["current_version"])
    return doc


class DecisionApiTests(TestCase):
    def setUp(self):
        # Isola o armazenamento (não é usado aqui, mas mantém consistência).
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")

    def _payload(self, **over):
        data = {
            "title": "Adoptar PostgreSQL",
            "context": f"Contexto {CONTEXT_TOKEN}",
            "decision_text": f"Decisão {DECISION_TOKEN}",
        }
        data.update(over)
        return data

    def _create(self, client, **over):
        return client.post(DECISIONS, self._payload(**over), format="json")

    # 1 — criação empresarial sem Product
    def test_create_company_level(self):
        resp = self._create(self.client_a)
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        self.assertEqual(body["status"], "active")
        self.assertIsNone(body["product"])
        self.assertEqual(body["responsible"], str(self.user_a.pk))
        self.assertEqual(body["version"], 1)

    # 2 — criação associada a Product
    def test_create_with_product(self):
        product = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="P", purpose="p"
        )
        resp = self._create(self.client_a, product=str(product.pk))
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["product"], str(product.pk))

    # 2b — criação com documento decisao_detalhada da mesma empresa
    def test_create_with_detail_document(self):
        doc = _document(self.org_a)
        resp = self._create(self.client_a, detail_document=str(doc.pk))
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["detail_document"], str(doc.pk))

    # 3 — responsável alheio rejeitado
    def test_foreign_responsible_rejected(self):
        resp = self._create(self.client_a, responsible=str(self.user_b.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(Decision.objects.count(), 0)

    # 4 — Product alheio rejeitado
    def test_foreign_product_rejected(self):
        foreign = Product.objects.create(
            organisation=self.org_b, responsible=self.user_b, name="B", purpose="p"
        )
        resp = self._create(self.client_a, product=str(foreign.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(Decision.objects.count(), 0)

    # 5 — documento alheio rejeitado
    def test_foreign_detail_document_rejected(self):
        foreign_doc = _document(self.org_b)
        resp = self._create(self.client_a, detail_document=str(foreign_doc.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(Decision.objects.count(), 0)

    # 6 — documento com tipo diferente é rejeitado
    def test_detail_document_wrong_type_rejected(self):
        wrong = _document(self.org_a, doc_type=DocumentType.RESULT)
        resp = self._create(self.client_a, detail_document=str(wrong.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(Decision.objects.count(), 0)

    # 6b — documento de outro produto é incoerente (rejeitado)
    def test_detail_document_of_other_product_rejected(self):
        product_x = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="X", purpose="p"
        )
        product_y = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="Y", purpose="p"
        )
        doc_y = _document(self.org_a, product=product_y)
        resp = self._create(
            self.client_a,
            product=str(product_x.pk),
            detail_document=str(doc_y.pk),
        )
        self.assertEqual(resp.status_code, 400, resp.content)

    # 7 — listagem isolada
    def test_list_is_isolated(self):
        self._create(self.client_a)
        self.assertEqual(self.client_b.get(DECISIONS).json()["count"], 0)
        self.assertEqual(self.client_a.get(DECISIONS).json()["count"], 1)

    # 7b — filtros por product e status
    def test_filters(self):
        product = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="P", purpose="p"
        )
        self._create(self.client_a, product=str(product.pk))
        self._create(self.client_a)  # empresarial
        by_product = self.client_a.get(f"{DECISIONS}?product={product.pk}").json()
        self.assertEqual(by_product["count"], 1)
        by_status = self.client_a.get(f"{DECISIONS}?status=active").json()
        self.assertEqual(by_status["count"], 2)

    # 8 — detalhe alheio devolve 404 (auditado)
    def test_foreign_detail_returns_404(self):
        created = self._create(self.client_a).json()
        resp = self.client_b.get(f"{DECISIONS}/{created['id']}")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
                entity_type="decision",
                entity_id=created["id"],
            ).exists()
        )

    # 8b — inexistente devolve 404
    def test_unknown_returns_404(self):
        self.assertEqual(
            self.client_a.get(f"{DECISIONS}/{uuid.uuid4()}").status_code, 404
        )

    # 9/10/11 — substituição cria nova active; anterior superseded; cadeia navegável
    def test_supersede_creates_chain(self):
        original = self._create(self.client_a).json()
        resp = self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(
                title="Adoptar PostgreSQL 16", expected_version=original["version"]
            ),
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        new = resp.json()
        self.assertEqual(new["status"], "active")
        self.assertEqual(new["supersedes"], original["id"])

        # Anterior ficou superseded e aponta para a nova (replaced_by).
        prev = self.client_a.get(f"{DECISIONS}/{original['id']}").json()
        self.assertEqual(prev["status"], "superseded")
        self.assertEqual(prev["replaced_by"], new["id"])
        self.assertIsNone(prev["supersedes"])
        # Cadeia navegável a partir da nova.
        self.assertEqual(new["replaced_by"], None)

    # 12 — decisão superseded não é substituída de novo
    def test_cannot_supersede_twice(self):
        original = self._create(self.client_a).json()
        self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="v2", expected_version=1),
            format="json",
        )
        resp = self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="v3", expected_version=1),
            format="json",
        )
        self.assertEqual(resp.status_code, 409, resp.content)

    # 12b — versão obsoleta devolve 409
    def test_supersede_version_conflict(self):
        original = self._create(self.client_a).json()
        resp = self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="v2", expected_version=999),
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 12c — substituir decisão alheia devolve 404
    def test_supersede_foreign_returns_404(self):
        original = self._create(self.client_a).json()
        resp = self.client_b.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="x"),
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    # 14 — histórico não é apagado (a decisão anterior continua a existir)
    def test_history_preserved(self):
        original = self._create(self.client_a).json()
        self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="v2", expected_version=1),
            format="json",
        )
        self.assertEqual(Decision.objects.count(), 2)
        self.assertTrue(Decision.objects.filter(pk=original["id"]).exists())

    # 15 — criação e substituição auditadas (evento 8)
    def test_audit_events(self):
        original = self._create(self.client_a).json()
        self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="v2", expected_version=1),
            format="json",
        )
        actions = list(
            AuditEvent.objects.filter(entity_type="decision").values_list(
                "action", flat=True
            )
        )
        self.assertEqual(actions.count(AuditAction.DECISION_CREATED), 2)  # criação + nova
        self.assertEqual(actions.count(AuditAction.DECISION_UPDATED), 1)  # transição

    # 16 — conteúdo integral não entra na auditoria
    def test_audit_has_no_full_content(self):
        original = self._create(self.client_a).json()
        self.client_a.post(
            f"{DECISIONS}/{original['id']}/supersede",
            self._payload(title="v2", expected_version=1),
            format="json",
        )
        for event in AuditEvent.objects.all():
            self.assertNotIn(CONTEXT_TOKEN, str(event.metadata))
            self.assertNotIn(DECISION_TOKEN, str(event.metadata))

    # sem DELETE nem PATCH (a decisão não é reescrita)
    def test_no_delete_no_patch(self):
        created = self._create(self.client_a).json()
        self.assertEqual(
            self.client_a.delete(f"{DECISIONS}/{created['id']}").status_code, 405
        )
        self.assertEqual(
            self.client_a.patch(
                f"{DECISIONS}/{created['id']}", {"title": "x"}, format="json"
            ).status_code,
            405,
        )

    # sem contexto de empresa → 403
    def test_requires_company_context(self):
        get_user_model().objects.create_user(email="solo@x.pt", password="senha-123")
        client = _client_for("solo@x.pt")
        self.assertEqual(client.get(DECISIONS).status_code, 403)
