"""Testes da API documental (F1-P04-PR02).

Cobrem criação (v1 + ficheiro privado), edição (nova versão, v1 preservada),
detalhe com conteúdo, ausência de conteúdo na BD, checksum, limite/UTF-8,
isolamento (produto/documento alheios), concorrência (409), histórico,
recuperação, marcadores, filtros e auditoria sem conteúdo integral.
"""
from __future__ import annotations

import hashlib
import shutil
import tempfile
import uuid

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.audit.models import AuditAction, AuditEvent
from apps.documents.models import Document, DocumentVersion
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.storage import get_storage

DOCS = "/api/v1/documents"
TOKEN = "ZZTOKENconteudoUNICO42"


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


class DocumentApiTests(TestCase):
    def setUp(self):
        # Raiz de armazenamento isolada por teste.
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user_a, self.org_a = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client_for("a@x.pt")
        self.client_b = _client_for("b@x.pt")

    def _create(self, client, **payload):
        payload.setdefault("title", "Documento")
        payload.setdefault("document_type", "contexto_da_empresa")
        payload.setdefault("content", f"# Título\n\n{TOKEN} corpo do documento.")
        return client.post(DOCS, payload, format="json")

    # 1 — criação gera v1 e ficheiro privado
    def test_create_generates_v1_and_private_object(self):
        resp = self._create(self.client_a)
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        self.assertEqual(body["current_version_number"], 1)
        version = DocumentVersion.objects.get(document_id=body["id"], version_number=1)
        self.assertTrue(get_storage().exists(version.storage_key))
        self.assertEqual(version.storage_key.count("/"), 1)  # chave do servidor

    # 2 — edição gera v2 e preserva v1
    def test_edit_generates_v2_and_preserves_v1(self):
        created = self._create(self.client_a).json()
        doc_id = created["id"]
        v1 = DocumentVersion.objects.get(document_id=doc_id, version_number=1)

        resp = self.client_a.patch(
            f"{DOCS}/{doc_id}",
            {"content": "# Novo\n\nconteúdo revisto.", "expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertEqual(body["current_version_number"], 2)
        # v1 continua a existir, imutável e com o conteúdo original.
        v1.refresh_from_db()
        self.assertTrue(get_storage().exists(v1.storage_key))
        self.assertEqual(DocumentVersion.objects.filter(document_id=doc_id).count(), 2)

    # 3 — conteúdo não aparece na BD
    def test_content_not_stored_in_database(self):
        self._create(self.client_a)
        with connection.cursor() as cursor:
            for table in ("documents_document", "documents_documentversion"):
                cursor.execute(f"SELECT * FROM {table}")  # noqa: S608 - nome fixo
                rows = cursor.fetchall()
                self.assertNotIn(TOKEN, str(rows))

    # 4 — checksum corresponde ao ficheiro
    def test_checksum_matches_stored_object(self):
        body = self._create(self.client_a).json()
        version = DocumentVersion.objects.get(document_id=body["id"], version_number=1)
        stored_bytes = get_storage().open(version.storage_key)
        self.assertEqual(
            version.checksum, hashlib.sha256(stored_bytes).hexdigest()
        )
        self.assertEqual(body["checksum"], version.checksum)

    # 5 — conteúdo acima do limite devolve 413
    @override_settings(DOCUMENT_MAX_BYTES=32)
    def test_content_over_limit_returns_413(self):
        resp = self._create(self.client_a, content="x" * 100)
        self.assertEqual(resp.status_code, 413, resp.content)
        self.assertEqual(Document.objects.count(), 0)

    # 6 — UTF-8 inválido é rejeitado
    def test_invalid_utf8_is_rejected(self):
        # Corpo com bytes que não são UTF-8 válido → o parser JSON recusa (400);
        # nada é persistido.
        body = (
            b'{"title":"t","document_type":"resultado","content":"\xff\xfe bad"}'
        )
        resp = self.client_a.post(
            DOCS, data=body, content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(Document.objects.count(), 0)

    # 6b — a validação de UTF-8 do conteúdo é aplicada ao nível do serviço
    def test_service_rejects_non_utf8_content(self):
        from apps.documents import service

        with self.assertRaises(service.InvalidContentEncoding):
            service.encode_content("\ud800")  # surrogate isolado não é UTF-8 válido

    # 7 — Product alheio é rejeitado
    def test_foreign_product_is_rejected(self):
        foreign = Product.objects.create(
            organisation=self.org_b,
            responsible=self.user_b,
            name="Produto B",
            purpose="p",
        )
        resp = self._create(self.client_a, product=str(foreign.pk))
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(Document.objects.count(), 0)

    # 7b — Product da mesma empresa é aceite e associado
    def test_same_org_product_is_accepted(self):
        product = Product.objects.create(
            organisation=self.org_a,
            responsible=self.user_a,
            name="Produto A",
            purpose="p",
        )
        resp = self._create(
            self.client_a, product=str(product.pk), document_type="visao_de_produto"
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["product"], str(product.pk))

    # 8 — documento alheio devolve 404 (e audita a tentativa cruzada)
    def test_foreign_document_returns_404(self):
        created = self._create(self.client_a).json()
        resp = self.client_b.get(f"{DOCS}/{created['id']}")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
                entity_type="document",
                entity_id=created["id"],
            ).exists()
        )

    # 8b — documento inexistente devolve 404 sem auditoria cruzada
    def test_unknown_document_returns_404(self):
        resp = self.client_a.get(f"{DOCS}/{uuid.uuid4()}")
        self.assertEqual(resp.status_code, 404)

    # 9 — conflito de versão devolve 409
    def test_version_conflict_returns_409(self):
        created = self._create(self.client_a).json()
        doc_id = created["id"]
        # Primeira edição leva a versão de 1 para 2.
        self.client_a.patch(
            f"{DOCS}/{doc_id}",
            {"content": "a", "expected_version": 1},
            format="json",
        )
        # Segunda edição com a versão obsoleta.
        resp = self.client_a.patch(
            f"{DOCS}/{doc_id}",
            {"content": "b", "expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 409, resp.content)

    # 11 — histórico mantém todas as versões
    def test_history_keeps_all_versions(self):
        created = self._create(self.client_a).json()
        doc_id = created["id"]
        for i in range(2):
            self.client_a.patch(
                f"{DOCS}/{doc_id}",
                {"content": f"rev {i}", "expected_version": i + 1},
                format="json",
            )
        resp = self.client_a.get(f"{DOCS}/{doc_id}/versions")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["count"], 3)
        numbers = [v["version_number"] for v in body["results"]]
        self.assertEqual(numbers, [3, 2, 1])

    # 12/13 — recuperação cria nova versão com o conteúdo histórico
    def test_restore_creates_new_version_with_historic_content(self):
        original = f"# Original\n\n{TOKEN}"
        created = self.client_a.post(
            DOCS,
            {
                "title": "Doc",
                "document_type": "contexto_da_empresa",
                "content": original,
            },
            format="json",
        ).json()
        doc_id = created["id"]
        # Edita para v2 (conteúdo diferente).
        self.client_a.patch(
            f"{DOCS}/{doc_id}",
            {"content": "conteúdo diferente", "expected_version": 1},
            format="json",
        )
        # Recupera a v1 → cria v3 com o conteúdo original.
        resp = self.client_a.post(
            f"{DOCS}/{doc_id}/restore",
            {"version_number": 1, "expected_version": 2},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertEqual(body["current_version_number"], 3)
        self.assertEqual(body["content"], original)
        # v1 e v2 continuam a existir.
        self.assertEqual(DocumentVersion.objects.filter(document_id=doc_id).count(), 3)
        # Consulta directa da versão exacta devolve o conteúdo daquela versão.
        v2 = self.client_a.get(f"{DOCS}/{doc_id}/versions/2").json()
        self.assertEqual(v2["content"], "conteúdo diferente")

    # recuperação de versão inexistente → 404
    def test_restore_unknown_version_returns_404(self):
        created = self._create(self.client_a).json()
        resp = self.client_a.post(
            f"{DOCS}/{created['id']}/restore",
            {"version_number": 99, "expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    # recuperação com versão actual obsoleta → 409
    def test_restore_version_conflict_returns_409(self):
        created = self._create(self.client_a).json()
        doc_id = created["id"]
        self.client_a.patch(
            f"{DOCS}/{doc_id}", {"content": "x", "expected_version": 1}, format="json"
        )
        resp = self.client_a.post(
            f"{DOCS}/{doc_id}/restore",
            {"version_number": 1, "expected_version": 1},  # obsoleta (já é 2)
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    # 14 — marcadores persistem na BD
    def test_markers_persist(self):
        created = self._create(
            self.client_a, is_outdated=True, export_policy="denied"
        ).json()
        doc = Document.objects.get(pk=created["id"])
        self.assertTrue(doc.is_outdated)
        self.assertEqual(doc.export_policy, "denied")
        # Edição de marcadores com concorrência coerente.
        resp = self.client_a.patch(
            f"{DOCS}/{created['id']}",
            {"is_outdated": False, "export_policy": "allowed", "expected_version": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        doc.refresh_from_db()
        self.assertFalse(doc.is_outdated)
        self.assertEqual(doc.export_policy, "allowed")
        self.assertEqual(doc.version, 2)

    # marcador export_policy inválido → 400
    def test_invalid_export_policy_returns_400(self):
        resp = self._create(self.client_a, export_policy="publico")
        self.assertEqual(resp.status_code, 400)

    # 15/16/17 — filtros por tipo, produto e política (isolados por empresa)
    def test_filters(self):
        product = Product.objects.create(
            organisation=self.org_a, responsible=self.user_a, name="P", purpose="p"
        )
        self._create(self.client_a, document_type="contexto_da_empresa")
        self._create(
            self.client_a, document_type="visao_de_produto", product=str(product.pk)
        )
        # `decisao_detalhada` (a API genérica já não cria `resultado`, que passa a
        # ser gerido pela importação de resultado — F1-P06-PR01).
        self._create(
            self.client_a, document_type="decisao_detalhada", export_policy="denied"
        )

        # tipo
        r = self.client_a.get(f"{DOCS}?document_type=visao_de_produto").json()
        self.assertEqual(r["count"], 1)
        self.assertEqual(r["results"][0]["document_type"], "visao_de_produto")
        # produto
        r = self.client_a.get(f"{DOCS}?product={product.pk}").json()
        self.assertEqual(r["count"], 1)
        self.assertEqual(r["results"][0]["product"], str(product.pk))
        # política
        r = self.client_a.get(f"{DOCS}?export_policy=denied").json()
        self.assertEqual(r["count"], 1)
        self.assertEqual(r["results"][0]["export_policy"], "denied")
        # listagem não devolve conteúdo integral
        self.assertNotIn("content", r["results"][0])

    # listagem nunca atravessa empresas
    def test_list_is_isolated(self):
        self._create(self.client_a)
        r = self.client_b.get(DOCS).json()
        self.assertEqual(r["count"], 0)

    # 22 — auditoria não contém conteúdo integral
    def test_audit_has_no_full_content(self):
        created = self._create(self.client_a).json()
        self.client_a.patch(
            f"{DOCS}/{created['id']}",
            {"content": f"{TOKEN} revisto", "expected_version": 1},
            format="json",
        )
        actions = set(
            AuditEvent.objects.filter(entity_type="document").values_list(
                "action", flat=True
            )
        )
        self.assertIn(AuditAction.DOCUMENT_CREATED, actions)
        self.assertIn(AuditAction.DOCUMENT_VERSION_CREATED, actions)
        self.assertIn(AuditAction.DOCUMENT_UPDATED, actions)
        for event in AuditEvent.objects.all():
            self.assertNotIn(TOKEN, str(event.metadata))

    # documento sem contexto de empresa → 403
    def test_requires_company_context(self):
        user = get_user_model().objects.create_user(
            email="solo@x.pt", password="senha-123"
        )  # sem Membership
        client = _client_for("solo@x.pt")
        self.assertEqual(client.get(DOCS).status_code, 403)
