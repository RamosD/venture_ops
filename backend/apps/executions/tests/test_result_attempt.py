"""Testes da importação manual de resultados (F1-P06-PR01, MVP-13).

Cobrem a criação de tentativas numeradas e imutáveis, a materialização como
documento `resultado` no armazenamento privado, a transição única
`prepared → result_pending_validation`, a coordenação BD↔storage, o isolamento, a
auditoria sem conteúdo e as restrições da API documental genérica.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.decisions.models import Decision
from apps.documents.models import Document, DocumentType
from apps.documents.service import create_document
from apps.executions.exceptions import ResultAttemptImmutableError
from apps.executions.models import AIExecution, ResultAttempt
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.storage.exceptions import StorageError
from apps.work_items.models import WorkItem

CONTENT_TOKEN = "RESULTADOxUNICO5566"
NOTES_TOKEN = "NOTASxUNICO8899"


def _company(email, name):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=name, status=Organisation.Status.ACTIVE)
    Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org


def _client(email):
    from rest_framework.test import APIClient

    c = APIClient()
    c.post("/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json")
    return c


def _count_objects(root) -> int:
    total = 0
    for _dir, _sub, files in os.walk(root):
        total += len(files)
    return total


class ResultAttemptTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user, self.org = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client("a@x.pt")
        self.client_b = _client("b@x.pt")
        self.product = Product.objects.create(
            organisation=self.org, responsible=self.user, name="Produto A", purpose="p"
        )
        self.function = create_function(
            organisation=self.org,
            data={"name": "F", "actor_type": "human", "purpose": "p",
                  "responsibilities": "r"},
        )
        self.execution = self._make_execution()

    def _make_execution(self):
        _doc, v = create_document(
            actor=self.user, organisation=self.org, title="Ctx",
            document_type=DocumentType.COMPANY_CONTEXT, content="contexto",
        )
        return create_execution(
            actor=self.user, organisation=self.org,
            data={"product": self.product.pk, "function_profile": self.function.pk,
                  "title": "Exec", "objective": "o", "request_instructions": "i",
                  "expected_output_format": "md", "execution_mode": "manual_local",
                  "context": [{"document_version": str(v.pk)}]},
        )

    def _url(self, execution=None):
        return f"/api/v1/executions/{(execution or self.execution).pk}/result-attempts"

    def _import_content(self, client=None, execution=None, **over):
        body = {
            "expected_version": (execution or self.execution).version,
            "content": f"# Resultado\n{CONTENT_TOKEN}",
            "source_tool": "ChatGPT",
        }
        body.update(over)
        return (client or self.client_a).post(
            self._url(execution), body, format="json"
        )

    # 1 — content → tentativa 1
    def test_import_content_creates_attempt_1(self):
        resp = self._import_content()
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        self.assertEqual(body["attempt_number"], 1)
        self.assertEqual(body["source_mode"], "pasted")
        self.assertEqual(ResultAttempt.objects.count(), 1)

    # 2 — file → tentativa
    def test_import_file_creates_attempt(self):
        upload = SimpleUploadedFile("r.md", f"# R\n{CONTENT_TOKEN}".encode("utf-8"),
                                    content_type="text/markdown")
        resp = self.client_a.post(
            self._url(),
            {"expected_version": self.execution.version, "source_tool": "Claude",
             "file": upload},
            format="multipart",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()["source_mode"], "file")

    # 3 — ambas as entradas rejeitadas
    def test_both_inputs_rejected(self):
        upload = SimpleUploadedFile("r.md", b"x", content_type="text/markdown")
        resp = self.client_a.post(
            self._url(),
            {"expected_version": self.execution.version, "source_tool": "T",
             "content": "texto", "file": upload},
            format="multipart",
        )
        self.assertEqual(resp.status_code, 400, resp.content)

    # 4 — ausência de conteúdo rejeitada
    def test_no_input_rejected(self):
        resp = self.client_a.post(
            self._url(),
            {"expected_version": self.execution.version, "source_tool": "T"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    # 5 — conteúdo acima do limite → 413
    def test_content_too_large(self):
        with override_settings(DOCUMENT_MAX_BYTES=32):
            resp = self._import_content(content="x" * 100)
        self.assertEqual(resp.status_code, 413)

    # 6 — UTF-8 inválido (ficheiro binário) rejeitado
    def test_invalid_utf8_file_rejected(self):
        upload = SimpleUploadedFile("r.bin", b"\xff\xfe\x00bad", content_type="application/octet-stream")
        resp = self.client_a.post(
            self._url(),
            {"expected_version": self.execution.version, "source_tool": "T",
             "file": upload},
            format="multipart",
        )
        self.assertEqual(resp.status_code, 400)

    # 7 — source_tool obrigatório
    def test_source_tool_required(self):
        resp = self._import_content(source_tool="")
        self.assertEqual(resp.status_code, 400)

    # 8/9/10 — nasce prepared; importa → result_pending_validation; não aprova
    def test_transition_prepared_to_pending(self):
        self.assertEqual(self.execution.status, "prepared")
        resp = self._import_content()
        self.assertEqual(resp.status_code, 201)
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "result_pending_validation")
        self.assertNotEqual(self.execution.status, "approved")
        self.assertEqual(resp.json()["execution"]["status"], "result_pending_validation")

    # 11 — importação não altera Product, documentos existentes, decisões, pendências
    def test_import_does_not_alter_other_entities(self):
        docs_before = Document.objects.count()
        product_version = self.product.version
        self._import_content()
        # Apenas +1 documento (o resultado); Product intacto; sem decisões/pendências.
        self.assertEqual(Document.objects.count(), docs_before + 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.version, product_version)
        self.assertEqual(Decision.objects.count(), 0)
        self.assertEqual(WorkItem.objects.count(), 0)

    # 12 — tentativa referencia versão exacta / documento é `resultado` do Product
    def test_attempt_references_exact_result_version(self):
        self._import_content()
        attempt = ResultAttempt.objects.get()
        version = attempt.result_document_version
        self.assertEqual(version.document.document_type, DocumentType.RESULT)
        self.assertEqual(version.document.product_id, self.product.pk)
        self.assertEqual(version.version_number, 1)

    # 13 — conteúdo não fica na BD (só no armazenamento)
    def test_content_not_in_db(self):
        self._import_content()
        attempt = ResultAttempt.objects.get()
        self.execution.refresh_from_db()
        # Nenhuma coluna de ResultAttempt/AIExecution contém o token do conteúdo.
        self.assertNotIn(CONTENT_TOKEN, str(list(ResultAttempt.objects.values())))
        self.assertNotIn(CONTENT_TOKEN, str(list(AIExecution.objects.values())))
        # Mas é legível a partir do armazenamento.
        from apps.documents.service import read_content
        self.assertIn(CONTENT_TOKEN, read_content(attempt.result_document_version))

    # 14 — checksum corresponde ao ficheiro
    def test_checksum_matches_content(self):
        self._import_content()
        version = ResultAttempt.objects.get().result_document_version
        expected = hashlib.sha256(f"# Resultado\n{CONTENT_TOKEN}".encode("utf-8")).hexdigest()
        self.assertEqual(version.checksum, expected)

    # 15 — tentativa é imutável
    def test_attempt_immutable(self):
        self._import_content()
        attempt = ResultAttempt.objects.get()
        attempt.source_tool = "OUTRO"
        with self.assertRaises(ResultAttemptImmutableError):
            attempt.save()
        with self.assertRaises(ResultAttemptImmutableError):
            attempt.delete()
        with self.assertRaises(ResultAttemptImmutableError):
            ResultAttempt.objects.filter(pk=attempt.pk).update(source_tool="X")

    # 16 — attempt_number atribuído no servidor (cliente não escolhe)
    def test_attempt_number_server_assigned(self):
        resp = self._import_content(attempt_number=99)
        self.assertEqual(resp.status_code, 400)  # campo não permitido

    # 17 — segunda importação enquanto result_pending_validation → 409
    def test_second_import_while_pending_409(self):
        self._import_content()
        self.execution.refresh_from_db()
        resp = self._import_content(expected_version=self.execution.version)
        self.assertEqual(resp.status_code, 409)

    # 18 — versão obsoleta da execução → 409
    def test_stale_execution_version_409(self):
        resp = self._import_content(expected_version=999)
        self.assertEqual(resp.status_code, 409)

    # 20 — falha de storage não altera a execução
    def test_storage_failure_leaves_execution_unchanged(self):
        with patch(
            "apps.storage.filesystem.FilesystemStorageAdapter.save",
            side_effect=StorageError("boom"),
        ):
            try:
                self._import_content()
            except StorageError:
                pass
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "prepared")
        self.assertEqual(ResultAttempt.objects.count(), 0)

    # 21 — falha de BD depois da escrita tenta limpar o objecto órfão
    def test_db_failure_cleans_orphan_object(self):
        before = _count_objects(self._tmp)
        with patch.object(ResultAttempt, "save", side_effect=Exception("db boom")):
            with self.assertRaises(Exception):
                self._import_content()
        # O objecto de resultado escrito foi removido → contagem inalterada.
        self.assertEqual(_count_objects(self._tmp), before)
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "prepared")

    # 22 — documento resultado não pode ser criado pela API genérica
    def test_generic_api_cannot_create_result_document(self):
        resp = self.client_a.post(
            "/api/v1/documents",
            {"title": "R", "document_type": "resultado", "content": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    # 23 — documento ligado a tentativa não pode ser alterado/recuperado
    def test_result_document_not_editable_by_generic_api(self):
        self._import_content()
        version = ResultAttempt.objects.get().result_document_version
        doc_id = version.document_id
        patch_resp = self.client_a.patch(
            f"/api/v1/documents/{doc_id}",
            {"expected_version": version.document.version, "title": "novo"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, 409)
        restore_resp = self.client_a.post(
            f"/api/v1/documents/{doc_id}/restore",
            {"version_number": 1, "expected_version": version.document.version},
            format="json",
        )
        self.assertEqual(restore_resp.status_code, 409)
        # Leitura continua permitida.
        self.assertEqual(
            self.client_a.get(f"/api/v1/documents/{doc_id}").status_code, 200
        )

    # 24 — listagem não devolve conteúdo
    def test_list_has_no_content(self):
        self._import_content()
        resp = self.client_a.get(self._url())
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertNotIn("content", results[0])
        self.assertNotIn(CONTENT_TOKEN, str(results))
        self.assertEqual(results[0]["attempt_number"], 1)

    # 25 — detalhe devolve a versão exacta com conteúdo
    def test_detail_returns_exact_version(self):
        self._import_content()
        resp = self.client_a.get(f"{self._url()}/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["version_number"], 1)
        self.assertIn(CONTENT_TOKEN, body["content"])
        self.assertEqual(body["execution_context"]["status"], "result_pending_validation")

    # 26 — execução alheia → 404 indistinguível e auditada
    def test_foreign_execution_404_audited(self):
        resp = self.client_b.get(self._url())
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
                entity_type="execution",
                entity_id=str(self.execution.pk),
            ).exists()
        )

    # 27 — auditoria não contém resultado integral
    def test_audit_no_full_content(self):
        self._import_content(source_notes=f"nota {NOTES_TOKEN}")
        event = AuditEvent.objects.filter(action=AuditAction.RESULT_IMPORTED).first()
        self.assertIsNotNone(event)
        blob = str(event.metadata)
        self.assertNotIn(CONTENT_TOKEN, blob)
        self.assertNotIn(NOTES_TOKEN, blob)
        self.assertEqual(event.metadata["operation"], "import")
        self.assertEqual(event.metadata["attempt_number"], 1)
        self.assertEqual(event.metadata["source_mode"], "pasted")
        self.assertIn("checksum", event.metadata)
        self.assertEqual(event.result, AuditResult.SUCCESS)

    # entrada estrita: rejeita organisation/status/document
    def test_rejects_internal_fields(self):
        for field in ("organisation", "status", "document", "document_version"):
            resp = self._import_content(**{field: "x"})
            self.assertEqual(resp.status_code, 400, field)

    # detalhe/listagem alheios → 404
    def test_foreign_detail_404(self):
        self._import_content()
        self.assertEqual(self.client_b.get(f"{self._url()}/1").status_code, 404)

    def test_unauthenticated_rejected(self):
        from rest_framework.test import APIClient
        anon = APIClient()
        self.assertIn(anon.get(self._url()).status_code, (401, 403))
