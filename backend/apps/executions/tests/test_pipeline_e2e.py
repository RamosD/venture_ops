"""Validação ponta a ponta do fluxo vertical F1-P06 (PR06, MVP-13/14/15; M1).

Exercita o ciclo completo pelos **endpoints reais**:
preparar → importar → rever → pedir correcção → importar → aprovar → aplicar →
concluir, mais os cenários A–E (documento/decisão/pendência/fecho/rejeição), as
provas negativas **importar ≠ aprovar ≠ aplicar** (contagens/checksums antes e
depois), o isolamento entre empresas e a autorização. É a evidência automatizada do
marco **M1** (fluxo vertical), sem chamar qualquer IA.
"""
from __future__ import annotations

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.decisions.models import Decision
from apps.documents.models import Document, DocumentType, DocumentVersion
from apps.documents.service import create_document, read_content
from apps.executions.models import (
    AIExecution,
    ResultApplication,
    ResultAttempt,
    ResultReview,
)
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.work_items.models import WorkItem

APPLY_DOC = "apply-document"
APPLY_DEC = "apply-decision"
APPLY_WI = "apply-work-item"
CLOSE = "close-without-application"


def _company(email, name):
    user = get_user_model().objects.create_user(email=email, password="senha-123")
    org = Organisation.objects.create(name=name, status=Organisation.Status.ACTIVE)
    m = Membership.objects.create(
        user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
    )
    return user, org, m


def _client(email):
    from rest_framework.test import APIClient

    c = APIClient()
    c.post("/api/v1/auth/login", {"email": email, "password": "senha-123"}, format="json")
    return c


@override_settings()
class PipelineE2ETests(TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user, self.org, self.membership = _company("owner@x.pt", "Empresa A")
        self.user_b, self.org_b, self.membership_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client("owner@x.pt")
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
    def _execution(self):
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

    def _target_doc(self):
        doc, _v = create_document(
            actor=self.user, organisation=self.org, title="Alvo",
            document_type=DocumentType.PRODUCT_VISION, content="v1 original",
            product_id=self.product.pk,
        )
        return doc

    def _u(self, execution, suffix):
        return f"/api/v1/executions/{execution.pk}/{suffix}"

    def _import_text(self, execution, content="# Resultado\nvalor"):
        execution.refresh_from_db()
        return self.client_a.post(
            self._u(execution, "result-attempts"),
            {"expected_version": execution.version, "content": content,
             "source_tool": "ChatGPT"},
            format="json",
        )

    def _import_file(self, execution, content="conteudo de ficheiro"):
        execution.refresh_from_db()
        f = SimpleUploadedFile("r.md", content.encode("utf-8"), content_type="text/markdown")
        return self.client_a.post(
            self._u(execution, "result-attempts"),
            {"expected_version": execution.version, "file": f, "source_tool": "Claude"},
            format="multipart",
        )

    def _approve(self, execution, n=1):
        execution.refresh_from_db()
        return self.client_a.post(
            self._u(execution, f"result-attempts/{n}/approve"),
            {"expected_version": execution.version}, format="json",
        )

    # ===================================================================== #
    # Cenário principal E1–E6 (fluxo vertical completo).                     #
    # ===================================================================== #
    def test_main_scenario_prepare_to_completed(self):
        e = self._execution()
        target = self._target_doc()
        base_version_id = target.current_version_id

        # Estado inicial: prepared.
        self.assertEqual(e.status, "prepared")

        # 9/10 importar tentativa 1 → result_pending_validation.
        r = self._import_text(e, "# T1\nprimeiro")
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        self.assertEqual(e.status, "result_pending_validation")

        # 11 nenhuma entidade oficial mudou (documento alvo intacto, sem aplicação).
        target.refresh_from_db()
        self.assertEqual(target.current_version_id, base_version_id)
        self.assertEqual(ResultApplication.objects.count(), 0)

        # 12/13 pedir correcção → prepared.
        e.refresh_from_db()
        r = self.client_a.post(
            self._u(e, "result-attempts/1/request-correction"),
            {"expected_version": e.version, "observations": "corrige X"}, format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        self.assertEqual(e.status, "prepared")

        # 14 tentativa 1 e revisão correction_requested preservadas.
        self.assertTrue(ResultAttempt.objects.filter(execution=e, attempt_number=1).exists())
        self.assertEqual(
            ResultReview.objects.get(execution=e).decision, "correction_requested"
        )

        # 15/16 importar tentativa 2 (por ficheiro) → attempt_number=2.
        r = self._import_file(e, "# T2\nsegundo exacto")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()["attempt_number"], 2)
        e.refresh_from_db()
        self.assertEqual(e.status, "result_pending_validation")
        self.assertEqual(e.current_result_attempt.attempt_number, 2)

        # 17/18 aprovar tentativa 2 → approved.
        r = self._approve(e, n=2)
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        self.assertEqual(e.status, "approved")

        # 19 aprovação não alterou o documento alvo.
        target.refresh_from_db()
        self.assertEqual(target.current_version_id, base_version_id)
        self.assertEqual(ResultApplication.objects.count(), 0)

        # 20 aplicar a um documento.
        r = self.client_a.post(
            self._u(e, "apply/document"),
            {"attempt_number": 2, "target_document": str(target.pk),
             "expected_execution_version": e.version,
             "expected_document_version": target.version,
             "content": "# Versão final revista", "change_summary": "aplica t2",
             "confirmation": APPLY_DOC},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)

        # 21/22/23 nova versão + ResultApplication + completed.
        target.refresh_from_db()
        e.refresh_from_db()
        self.assertEqual(e.status, "completed")
        self.assertNotEqual(target.current_version_id, base_version_id)
        self.assertEqual(target.current_version.version_number, 2)
        app = ResultApplication.objects.get(execution=e)
        self.assertEqual(app.created_document_version_id, target.current_version_id)
        self.assertEqual(app.base_document_version_id, base_version_id)
        # A versão base permanece.
        self.assertTrue(DocumentVersion.objects.filter(pk=base_version_id).exists())

        # 24 histórico completo + auditoria (eventos 13,16,13,14,17).
        self.assertEqual(ResultAttempt.objects.filter(execution=e).count(), 2)
        for action in (
            AuditAction.RESULT_IMPORTED, AuditAction.CORRECTION_REQUESTED,
            AuditAction.RESULT_APPROVED, AuditAction.CHANGE_APPLIED,
        ):
            self.assertTrue(
                AuditEvent.objects.filter(action=action, result=AuditResult.SUCCESS).exists(),
                action,
            )
        # Conteúdo exacto da tentativa 2 (nunca o current_version do Document).
        att2 = ResultAttempt.objects.get(execution=e, attempt_number=2)
        self.assertIn("segundo exacto", read_content(att2.result_document_version))

    # ===================================================================== #
    # Cenários adicionais A–E.                                               #
    # ===================================================================== #
    def _approved_execution(self):
        e = self._execution()
        self._import_text(e)
        self._approve(e, n=1)
        e.refresh_from_db()
        return e

    def test_scenario_A_document(self):
        e = self._approved_execution()
        doc = self._target_doc()
        r = self.client_a.post(
            self._u(e, "apply/document"),
            {"attempt_number": 1, "target_document": str(doc.pk),
             "expected_execution_version": e.version,
             "expected_document_version": doc.version,
             "content": "novo", "change_summary": "s", "confirmation": APPLY_DOC},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        self.assertEqual(e.status, "completed")
        self.assertEqual(ResultApplication.objects.get(execution=e).application_type, "document")

    def test_scenario_B_decision(self):
        e = self._approved_execution()
        dec = Decision.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="D0", context="c", decision_text="t",
        )
        r = self.client_a.post(
            self._u(e, "apply/decision"),
            {"attempt_number": 1, "target_decision": str(dec.pk),
             "expected_execution_version": e.version, "expected_decision_version": dec.version,
             "title": "Nova", "context": "ctx", "decision_text": "txt",
             "confirmation": APPLY_DEC},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        dec.refresh_from_db()
        app = ResultApplication.objects.get(execution=e)
        self.assertEqual(dec.status, "superseded")
        self.assertEqual(app.created_decision.status, "active")
        self.assertEqual(app.created_decision.supersedes_id, dec.pk)  # cadeia linear

    def test_scenario_C_work_item(self):
        e = self._approved_execution()
        wi = WorkItem.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="W0", work_type=WorkItem.WorkType.ACTION, status=WorkItem.Status.OPEN,
            notes="preservar",
        )
        r = self.client_a.post(
            self._u(e, "apply/work-item"),
            {"attempt_number": 1, "target_work_item": str(wi.pk),
             "expected_execution_version": e.version, "expected_work_item_version": wi.version,
             "confirmation": APPLY_WI},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        wi.refresh_from_db()
        self.assertEqual(wi.status, "completed")
        self.assertEqual(wi.notes, "preservar")  # restantes campos preservados

    def test_scenario_D_no_change(self):
        e = self._approved_execution()
        r = self.client_a.post(
            self._u(e, "close-without-application"),
            {"attempt_number": 1, "expected_execution_version": e.version,
             "rationale": "sem alteração necessária", "confirmation": CLOSE},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        self.assertEqual(e.status, "completed")
        self.assertEqual(ResultApplication.objects.get(execution=e).application_type, "no_change")

    def test_scenario_E_reject_terminal(self):
        e = self._execution()
        self._import_text(e)
        e.refresh_from_db()
        r = self.client_a.post(
            self._u(e, "result-attempts/1/reject"),
            {"expected_version": e.version, "observations": "não serve"}, format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        self.assertEqual(e.status, "rejected")
        # rejected é terminal: qualquer aplicação → 409.
        doc = self._target_doc()
        r = self.client_a.post(
            self._u(e, "apply/document"),
            {"attempt_number": 1, "target_document": str(doc.pk),
             "expected_execution_version": e.version,
             "expected_document_version": doc.version,
             "content": "x", "change_summary": "s", "confirmation": APPLY_DOC},
            format="json",
        )
        self.assertEqual(r.status_code, 409, r.content)

    # ===================================================================== #
    # Provas negativas: importar ≠ aprovar ≠ aplicar.                       #
    # ===================================================================== #
    def test_import_approve_apply_negative_proofs(self):
        doc = self._target_doc()
        dec = Decision.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="D", context="c", decision_text="t",
        )
        wi = WorkItem.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="W", work_type=WorkItem.WorkType.ACTION, status=WorkItem.Status.OPEN,
        )
        base_checksum = doc.current_version.checksum
        target_dv_count = doc.versions.count()  # versões do documento ALVO

        e = self._execution()

        # Após importar: nada oficial muda; sem aplicação; só pending.
        self._import_text(e)
        e.refresh_from_db()
        doc.refresh_from_db(); dec.refresh_from_db(); wi.refresh_from_db()
        self.assertEqual(e.status, "result_pending_validation")
        self.assertEqual(doc.current_version.checksum, base_checksum)
        self.assertEqual(dec.status, "active")
        self.assertEqual(wi.status, "open")
        self.assertEqual(ResultApplication.objects.count(), 0)

        # Após aprovar: mesmas entidades intactas; sem aplicação; só approved.
        self._approve(e, n=1)
        e.refresh_from_db()
        doc.refresh_from_db(); dec.refresh_from_db(); wi.refresh_from_db()
        self.assertEqual(e.status, "approved")
        self.assertEqual(doc.current_version.checksum, base_checksum)
        self.assertEqual(dec.status, "active")
        self.assertEqual(wi.status, "open")
        self.assertEqual(ResultApplication.objects.count(), 0)

        # Depois de aplicar (documento): exactamente o alvo muda; existe aplicação;
        # completed; alvos não seleccionados (decisão/pendência) intactos.
        r = self.client_a.post(
            self._u(e, "apply/document"),
            {"attempt_number": 1, "target_document": str(doc.pk),
             "expected_execution_version": e.version,
             "expected_document_version": doc.version,
             "content": "final", "change_summary": "s", "confirmation": APPLY_DOC},
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.content)
        e.refresh_from_db()
        doc.refresh_from_db(); dec.refresh_from_db(); wi.refresh_from_db()
        self.assertEqual(e.status, "completed")
        self.assertNotEqual(doc.current_version.checksum, base_checksum)
        # Exactamente UMA nova versão do documento alvo (versão anterior preservada).
        self.assertEqual(doc.versions.count(), target_dv_count + 1)
        self.assertEqual(dec.status, "active")  # não seleccionado → intacto
        self.assertEqual(wi.status, "open")

    # ===================================================================== #
    # Isolamento e autorização.                                             #
    # ===================================================================== #
    def test_isolation_cross_org(self):
        e = self._approved_execution()
        # Empresa B não pode ler tentativas nem aplicar sobre a execução de A.
        self.assertEqual(
            self.client_b.get(self._u(e, "result-attempts")).status_code, 404
        )
        self.assertEqual(
            self.client_b.get(self._u(e, "reviews")).status_code, 404
        )
        doc = self._target_doc()
        r = self.client_b.post(
            self._u(e, "apply/document"),
            {"attempt_number": 1, "target_document": str(doc.pk),
             "expected_execution_version": e.version,
             "expected_document_version": doc.version,
             "content": "x", "change_summary": "s", "confirmation": APPLY_DOC},
            format="json",
        )
        self.assertEqual(r.status_code, 404, r.content)
        self.assertTrue(
            AuditEvent.objects.filter(action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT).exists()
        )

    def test_authorization_non_owner_cannot_review_or_apply(self):
        e = self._execution()
        self._import_text(e)
        e.refresh_from_db()
        viewer = get_user_model().objects.create_user(email="v@x.pt", password="senha-123")
        Membership.objects.create(
            user=viewer, organisation=self.org, role="viewer", is_active=True
        )
        client_v = _client("v@x.pt")
        # não-Owner não pode rever.
        self.assertEqual(
            client_v.post(self._u(e, "result-attempts/1/approve"),
                          {"expected_version": e.version}, format="json").status_code, 403
        )
        # Owner aprova; depois não-Owner não pode aplicar.
        self._approve(e, n=1)
        e.refresh_from_db()
        doc = self._target_doc()
        self.assertEqual(
            client_v.post(self._u(e, "apply/document"),
                          {"attempt_number": 1, "target_document": str(doc.pk),
                           "expected_execution_version": e.version,
                           "expected_document_version": doc.version,
                           "content": "x", "change_summary": "s", "confirmation": APPLY_DOC},
                          format="json").status_code, 403
        )

    def test_reviewer_and_applied_by_derive_from_session(self):
        # O cliente não escolhe reviewer/applied_by: campos internos são rejeitados.
        e = self._execution()
        self._import_text(e)
        e.refresh_from_db()
        r = self.client_a.post(
            self._u(e, "result-attempts/1/approve"),
            {"expected_version": e.version, "reviewer": str(self.user_b.pk)},
            format="json",
        )
        self.assertEqual(r.status_code, 400, r.content)  # entrada estrita
        # aprovação legítima deriva o reviewer da sessão.
        self._approve(e, n=1)
        self.assertEqual(ResultReview.objects.get(execution=e).reviewer_id, self.user.pk)
