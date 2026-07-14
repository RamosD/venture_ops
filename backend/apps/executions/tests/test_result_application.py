"""Testes da aplicação documental controlada (F1-P06-PR04, MVP-15.C1).

Cobrem: aplicação só a partir de `approved`; nenhuma aplicação sem aprovação;
conteúdo/confirmação/resumo obrigatórios; elegibilidade do documento alvo; nova
versão criada e ligada pela `ResultApplication` (versão anterior preservada);
transição `approved → completed` só após sucesso; conflitos de versão (409);
idempotência por `request_fingerprint` (repetição idêntica) e 409 para comando
diferente; atomicidade BD↔storage (falha de storage deixa `approved`; falha de BD
não deixa aplicação parcial); imutabilidade; auditoria sem conteúdo.
"""
from __future__ import annotations

import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.db.models import F
from django.test import TestCase, override_settings

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.documents.models import Document, DocumentType, DocumentVersion
from apps.documents.service import create_document
from apps.executions import result_service, review_service
from apps.executions.application_service import DOCUMENT_APPLY_CONFIRMATION
from apps.executions.exceptions import ResultApplicationImmutableError
from apps.executions.models import AIExecution, ResultApplication
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.storage.exceptions import StorageError

CONTENT_TOKEN = "CONTEUDOxAPLICADO4242"
SUMMARY_TOKEN = "RESUMOxSECRETO7788"


def _company(email, name):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=name, status=Organisation.Status.ACTIVE)
    membership = Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org, membership


def _client(email):
    from rest_framework.test import APIClient

    c = APIClient()
    c.post("/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json")
    return c


@override_settings()
class ResultApplicationTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user, self.org, self.membership = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b, self.membership_b = _company("b@x.pt", "Empresa B")
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

    # --- Fábricas -----------------------------------------------------------
    def _make_execution(self):
        _doc, v = create_document(
            actor=self.user, organisation=self.org, title="Ctx",
            document_type=DocumentType.COMPANY_CONTEXT, content="contexto",
            product_id=self.product.pk,
        )
        return create_execution(
            actor=self.user, organisation=self.org,
            data={"product": self.product.pk, "function_profile": self.function.pk,
                  "title": "Exec", "objective": "o", "request_instructions": "i",
                  "expected_output_format": "md", "execution_mode": "manual_local",
                  "context": [{"document_version": str(v.pk)}]},
        )

    def _import(self, execution):
        result_service.import_result(
            actor=self.user, organisation=self.org, execution_id=execution.pk,
            expected_version=execution.version, content="resultado externo",
            source_tool="ChatGPT",
        )
        execution.refresh_from_db()
        return execution

    def _approve(self, execution):
        review_service.approve_result(
            actor=self.user, membership=self.membership, organisation=self.org,
            execution_id=execution.pk, attempt_number=1,
            expected_version=execution.version,
        )
        execution.refresh_from_db()
        return execution

    def _approved_execution(self):
        execution = self._make_execution()
        self._import(execution)
        self._approve(execution)
        return execution

    def _target_doc(self, org=None, product=None, user=None, doc_type=None):
        doc, _v = create_document(
            actor=user or self.user, organisation=org or self.org,
            title="Alvo", document_type=doc_type or DocumentType.PRODUCT_VISION,
            content="v1 original",
            product_id=product.pk if product else (
                self.product.pk if product is not False else None
            ),
        )
        return doc

    def _url(self, execution):
        return f"/api/v1/executions/{execution.pk}/apply/document"

    def _body(self, execution, doc, **over):
        body = {
            "attempt_number": 1,
            "target_document": str(doc.pk),
            "expected_execution_version": execution.version,
            "expected_document_version": doc.version,
            "content": f"# Final revisto\n{CONTENT_TOKEN}",
            "change_summary": f"Aplica {SUMMARY_TOKEN}",
            "confirmation": DOCUMENT_APPLY_CONFIRMATION,
        }
        body.update(over)
        return body

    def _apply(self, execution, doc, client=None, **over):
        return (client or self.client_a).post(
            self._url(execution), self._body(execution, doc, **over), format="json"
        )

    # --- 1/10/16/18/19 aplicação bem-sucedida -------------------------------
    def test_apply_on_approved_creates_version_and_completes(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 201, resp.content)
        execution.refresh_from_db()
        doc.refresh_from_db()
        self.assertEqual(execution.status, "completed")
        self.assertEqual(ResultApplication.objects.count(), 1)
        app = ResultApplication.objects.get()
        self.assertEqual(app.application_type, "document")
        self.assertEqual(app.target_document_id, doc.pk)
        self.assertEqual(app.created_document_version_id, doc.current_version_id)
        self.assertEqual(doc.current_version.version_number, 2)

    # --- 2 prepared não aplica ----------------------------------------------
    def test_prepared_cannot_apply(self):
        execution = self._make_execution()  # prepared, sem import
        doc = self._target_doc()
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 3 result_pending_validation não aplica -----------------------------
    def test_pending_cannot_apply(self):
        execution = self._make_execution()
        self._import(execution)  # pending
        doc = self._target_doc()
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 409, resp.content)

    # --- 4 rejected não aplica ----------------------------------------------
    def test_rejected_cannot_apply(self):
        execution = self._make_execution()
        self._import(execution)
        review_service.reject_result(
            actor=self.user, membership=self.membership, organisation=self.org,
            execution_id=execution.pk, attempt_number=1,
            expected_version=execution.version, observations="não",
        )
        execution.refresh_from_db()
        doc = self._target_doc()
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 409, resp.content)

    # --- 5 completed não reaplica com comando diferente ---------------------
    def test_completed_cannot_apply_different(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        self.assertEqual(self._apply(execution, doc).status_code, 201)
        execution.refresh_from_db()
        doc.refresh_from_db()
        # Novo comando diferente (outro conteúdo/versões) → 409.
        resp = self.client_a.post(
            self._url(execution),
            self._body(execution, doc, content="OUTRO", change_summary="dif"),
            format="json",
        )
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 1)

    # --- 6 tentativa tem de estar aprovada ----------------------------------
    def test_attempt_must_be_approved(self):
        execution = self._make_execution()
        self._import(execution)  # pending, tentativa 1, sem revisão
        # Força approved SEM revisão (estado inconsistente artificial).
        AIExecution.objects.filter(pk=execution.pk).update(
            status="approved", version=F("version") + 1
        )
        execution.refresh_from_db()
        doc = self._target_doc()
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CHANGE_APPLIED, result=AuditResult.DENIED
            ).exists()
        )

    # --- 7 aprovação sem aplicação não altera documento ---------------------
    def test_approval_without_application_leaves_document(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        before_version = doc.version
        before_count = doc.versions.count()
        # Não aplicar; o documento permanece intacto.
        doc.refresh_from_db()
        self.assertEqual(doc.version, before_version)
        self.assertEqual(doc.versions.count(), before_count)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 8 conteúdo explícito obrigatório -----------------------------------
    def test_content_required(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        body = self._body(execution, doc)
        del body["content"]
        resp = self.client_a.post(self._url(execution), body, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 9 confirmation obrigatória -----------------------------------------
    def test_confirmation_required(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        resp = self._apply(execution, doc, confirmation="errado")
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 11 documento empresarial rejeitado ---------------------------------
    def test_enterprise_document_rejected(self):
        execution = self._approved_execution()
        doc, _v = create_document(
            actor=self.user, organisation=self.org, title="Empresarial",
            document_type=DocumentType.COMPANY_CONTEXT, content="x",
        )  # product=None
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 422, resp.content)

    # --- 12 documento de outro Product rejeitado ----------------------------
    def test_other_product_document_rejected(self):
        execution = self._approved_execution()
        other = Product.objects.create(
            organisation=self.org, responsible=self.user, name="P2", purpose="p"
        )
        doc = self._target_doc(product=other)
        resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 422, resp.content)

    # --- 13 documento alheio rejeitado (404 auditado) -----------------------
    def test_foreign_document_rejected(self):
        execution = self._approved_execution()
        prod_b = Product.objects.create(
            organisation=self.org_b, responsible=self.user_b, name="PB", purpose="p"
        )
        doc_b = self._target_doc(org=self.org_b, product=prod_b, user=self.user_b)
        resp = self._apply(execution, doc_b)
        self.assertEqual(resp.status_code, 404, resp.content)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT
            ).exists()
        )

    # --- 14 documento resultado rejeitado -----------------------------------
    def test_result_document_rejected(self):
        execution = self._approved_execution()
        # O documento de resultado da tentativa é gerido por ResultAttempt.
        result_doc = Document.objects.filter(
            document_type=DocumentType.RESULT
        ).first()
        self.assertIsNotNone(result_doc)
        resp = self._apply(execution, result_doc)
        self.assertEqual(resp.status_code, 422, resp.content)

    # --- 15/17 versão base guardada; versão anterior permanece --------------
    def test_base_version_stored_and_previous_preserved(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        base = doc.current_version
        self._apply(execution, doc)
        doc.refresh_from_db()
        app = ResultApplication.objects.get()
        self.assertEqual(app.base_document_version_id, base.pk)
        # Versão anterior permanece.
        self.assertTrue(doc.versions.filter(pk=base.pk).exists())
        self.assertEqual(doc.versions.count(), 2)

    # --- 20 versão obsoleta do documento → 409 ------------------------------
    def test_stale_document_version_conflict(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        resp = self._apply(execution, doc, expected_document_version=999)
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 21 versão obsoleta da execução → 409 -------------------------------
    def test_stale_execution_version_conflict(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        resp = self._apply(execution, doc, expected_execution_version=999)
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 22 falha de storage deixa execution approved -----------------------
    def test_storage_failure_leaves_approved(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        with patch(
            "apps.executions.application_service._write_object",
            side_effect=StorageError("boom"),
        ):
            resp = self._apply(execution, doc)
        self.assertEqual(resp.status_code, 503, resp.content)
        execution.refresh_from_db()
        doc.refresh_from_db()
        self.assertEqual(execution.status, "approved")
        self.assertEqual(ResultApplication.objects.count(), 0)
        self.assertEqual(doc.versions.count(), 1)
        self.assertTrue(
            AuditEvent.objects.filter(action=AuditAction.STORAGE_FAILURE).exists()
        )

    # --- 23 falha de BD não deixa aplicação parcial -------------------------
    def test_db_failure_no_partial_application(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        with patch.object(
            ResultApplication, "save", side_effect=DatabaseError("boom")
        ):
            with self.assertRaises(DatabaseError):
                self.client_a.post(
                    self._url(execution), self._body(execution, doc), format="json"
                )
        execution.refresh_from_db()
        doc.refresh_from_db()
        self.assertEqual(execution.status, "approved")
        self.assertEqual(ResultApplication.objects.count(), 0)
        self.assertEqual(doc.versions.count(), 1)  # versão revertida

    # --- 24 repetição idêntica é idempotente --------------------------------
    def test_idempotent_identical_repeat(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        body = self._body(execution, doc)
        r1 = self.client_a.post(self._url(execution), body, format="json")
        self.assertEqual(r1.status_code, 201, r1.content)
        app_id = r1.json()["application"]["id"]
        # Repetir o MESMO comando (mesmas versões esperadas) → idempotente (200).
        r2 = self.client_a.post(self._url(execution), body, format="json")
        self.assertEqual(r2.status_code, 200, r2.content)
        self.assertEqual(r2.json()["application"]["id"], app_id)
        self.assertEqual(ResultApplication.objects.count(), 1)
        doc.refresh_from_db()
        self.assertEqual(doc.versions.count(), 2)  # sem nova versão na repetição

    # --- 25 repetição diferente → 409 ---------------------------------------
    def test_different_repeat_conflict(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        self.client_a.post(self._url(execution), self._body(execution, doc), format="json")
        # Mesmo alvo, conteúdo diferente → 409 (aplicação já existe, fingerprint difere).
        resp = self.client_a.post(
            self._url(execution),
            self._body(execution, doc, content="conteúdo diferente"),
            format="json",
        )
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 1)

    # --- 27 ResultApplication imutável --------------------------------------
    def test_application_immutable(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        self._apply(execution, doc)
        app = ResultApplication.objects.get()
        app.change_summary = "alterado"
        with self.assertRaises(ResultApplicationImmutableError):
            app.save()
        with self.assertRaises(ResultApplicationImmutableError):
            app.delete()
        with self.assertRaises(ResultApplicationImmutableError):
            ResultApplication.objects.filter(pk=app.pk).update(change_summary="x")
        with self.assertRaises(ResultApplicationImmutableError):
            ResultApplication.objects.all().delete()

    # --- 28/29 aplicação auditada; auditoria sem conteúdo -------------------
    def test_application_audited_without_content(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        self._apply(execution, doc)
        event = AuditEvent.objects.get(
            action=AuditAction.CHANGE_APPLIED, result=AuditResult.SUCCESS
        )
        blob = str(event.metadata)
        self.assertNotIn(CONTENT_TOKEN, blob)
        self.assertNotIn(SUMMARY_TOKEN, blob)
        self.assertEqual(event.metadata["application_type"], "document")
        self.assertEqual(event.metadata["created_version"], 2)
        self.assertEqual(event.metadata["transition"], "approved->completed")
        self.assertIn("review_id", event.metadata)

    # --- Extra: não-Owner é rejeitado ---------------------------------------
    def test_non_owner_rejected(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        viewer = get_user_model().objects.create_user(
            email="v@x.pt", password="senha-123"
        )
        Membership.objects.create(
            user=viewer, organisation=self.org, role="viewer", is_active=True
        )
        resp = self._apply(execution, doc, client=_client("v@x.pt"))
        self.assertEqual(resp.status_code, 403, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- Extra: GET /application --------------------------------------------
    def test_get_application(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        # Antes de aplicar → 404.
        r0 = self.client_a.get(f"/api/v1/executions/{execution.pk}/application")
        self.assertEqual(r0.status_code, 404)
        self._apply(execution, doc)
        r1 = self.client_a.get(f"/api/v1/executions/{execution.pk}/application")
        self.assertEqual(r1.status_code, 200, r1.content)
        self.assertEqual(r1.json()["application"]["application_type"], "document")

    # --- Extra: entrada estrita rejeita campos internos ---------------------
    def test_strict_input_rejects_internal_fields(self):
        execution = self._approved_execution()
        doc = self._target_doc()
        resp = self._apply(
            execution, doc, application_type="decision", review=str(doc.pk),
        )
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)
