"""Testes dos caminhos de aplicação decisão/pendência/fecho (F1-P06-PR05, MVP-15.C2).

Cobrem: substituição de decisão (cadeia preservada, ligação pela aplicação),
conclusão de pendência (preserva outros campos), fecho `no_change` (rationale
obrigatório, nenhuma fonte oficial alterada); a regra de **uma aplicação por
execução** (segundo caminho → 409); todos os caminhos exigem aprovação e
confirmação; idempotência e 409; auditoria sem conteúdo. Inclui provas negativas
(importar/aprovar não alteram Decision/WorkItem).
"""
from __future__ import annotations

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.decisions.models import Decision
from apps.documents.models import DocumentType
from apps.documents.service import create_document
from apps.executions import result_service, review_service
from apps.executions.application_service import (
    DECISION_APPLY_CONFIRMATION,
    NO_CHANGE_CONFIRMATION,
    WORK_ITEM_APPLY_CONFIRMATION,
)
from apps.executions.models import ResultApplication
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.work_items.models import WorkItem

DECISION_TOKEN = "DECISAOxSECRETA5150"
NOTES_TOKEN = "NOTASxSECRETAS3141"
RATIONALE_TOKEN = "JUSTIFICACAOxSECRETA2718"


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
class ResultApplicationPathsTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user, self.org, self.membership = _company("a@x.pt", "Empresa A")
        self.user_b, self.org_b, self.membership_b = _company("b@x.pt", "Empresa B")
        self.client_a = _client("a@x.pt")
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
        e = self._make_execution()
        self._import(e)
        self._approve(e)
        return e

    def _pending_execution(self):
        e = self._make_execution()
        self._import(e)
        return e

    def _decision(self, org=None, product=None, user=None):
        return Decision.objects.create(
            organisation=org or self.org, product=product or self.product,
            responsible=user or self.user, title="D0", context="c0",
            decision_text="texto0",
        )

    def _work_item(self, org=None, product=None, user=None, notes=""):
        return WorkItem.objects.create(
            organisation=org or self.org, product=product or self.product,
            responsible=user or self.user, title="W0",
            work_type=WorkItem.WorkType.ACTION, status=WorkItem.Status.OPEN,
            notes=notes,
        )

    # --- Bodies -------------------------------------------------------------
    def _decision_body(self, execution, dec, **over):
        body = {
            "attempt_number": 1, "target_decision": str(dec.pk),
            "expected_execution_version": execution.version,
            "expected_decision_version": dec.version,
            "title": "Nova decisão", "context": "novo contexto",
            "decision_text": f"decisão {DECISION_TOKEN}",
            "confirmation": DECISION_APPLY_CONFIRMATION,
        }
        body.update(over)
        return body

    def _wi_body(self, execution, wi, **over):
        body = {
            "attempt_number": 1, "target_work_item": str(wi.pk),
            "expected_execution_version": execution.version,
            "expected_work_item_version": wi.version,
            "confirmation": WORK_ITEM_APPLY_CONFIRMATION,
        }
        body.update(over)
        return body

    def _close_body(self, execution, **over):
        body = {
            "attempt_number": 1, "expected_execution_version": execution.version,
            "rationale": f"fecho {RATIONALE_TOKEN}",
            "confirmation": NO_CHANGE_CONFIRMATION,
        }
        body.update(over)
        return body

    def _post(self, path, execution, body):
        return self.client_a.post(
            f"/api/v1/executions/{execution.pk}/{path}", body, format="json"
        )

    # --- 1/5/6/7/8 substituição de decisão ----------------------------------
    def test_decision_substitution(self):
        e = self._approved_execution()
        dec = self._decision()
        resp = self._post("apply/decision", e, self._decision_body(e, dec))
        self.assertEqual(resp.status_code, 201, resp.content)
        e.refresh_from_db()
        dec.refresh_from_db()
        self.assertEqual(e.status, "completed")
        app = ResultApplication.objects.get()
        self.assertEqual(app.application_type, "decision")
        # anterior superseded; nova active; cadeia preservada; ligação.
        self.assertEqual(dec.status, "superseded")
        new = app.created_decision
        self.assertEqual(new.status, "active")
        self.assertEqual(new.supersedes_id, dec.pk)
        self.assertEqual(app.target_decision_id, dec.pk)

    # --- 2 decisão superseded não pode ser alvo -----------------------------
    def test_superseded_decision_rejected(self):
        e = self._approved_execution()
        dec = self._decision()
        dec.status = Decision.Status.SUPERSEDED
        dec.save(update_fields=["status"])
        resp = self._post("apply/decision", e, self._decision_body(e, dec))
        self.assertEqual(resp.status_code, 422, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 3 decisão de outro Product é rejeitada -----------------------------
    def test_decision_other_product_rejected(self):
        e = self._approved_execution()
        other = Product.objects.create(
            organisation=self.org, responsible=self.user, name="P2", purpose="p"
        )
        dec = self._decision(product=other)
        resp = self._post("apply/decision", e, self._decision_body(e, dec))
        self.assertEqual(resp.status_code, 422, resp.content)

    # --- 4 decisão alheia é rejeitada ---------------------------------------
    def test_decision_foreign_rejected(self):
        e = self._approved_execution()
        prod_b = Product.objects.create(
            organisation=self.org_b, responsible=self.user_b, name="PB", purpose="p"
        )
        dec_b = self._decision(org=self.org_b, product=prod_b, user=self.user_b)
        resp = self._post("apply/decision", e, self._decision_body(e, dec_b))
        self.assertEqual(resp.status_code, 404, resp.content)
        self.assertTrue(
            AuditEvent.objects.filter(action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT).exists()
        )

    # --- 9/13 conclusão de pendência preservando campos ---------------------
    def test_work_item_completion_preserves_fields(self):
        e = self._approved_execution()
        wi = self._work_item(notes=NOTES_TOKEN)
        resp = self._post("apply/work-item", e, self._wi_body(e, wi))
        self.assertEqual(resp.status_code, 201, resp.content)
        e.refresh_from_db()
        wi.refresh_from_db()
        self.assertEqual(e.status, "completed")
        self.assertEqual(wi.status, "completed")
        # Outros campos preservados.
        self.assertEqual(wi.title, "W0")
        self.assertEqual(wi.notes, NOTES_TOKEN)
        self.assertEqual(wi.work_type, "action")
        app = ResultApplication.objects.get()
        self.assertEqual(app.application_type, "work_item")
        self.assertEqual(app.target_work_item_id, wi.pk)

    # --- 10 WorkItem final não pode ser aplicado ----------------------------
    def test_final_work_item_rejected(self):
        e = self._approved_execution()
        wi = self._work_item()
        wi.status = WorkItem.Status.COMPLETED
        wi.save(update_fields=["status"])
        resp = self._post("apply/work-item", e, self._wi_body(e, wi))
        self.assertEqual(resp.status_code, 422, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 11 WorkItem de outro Product é rejeitado ---------------------------
    def test_work_item_other_product_rejected(self):
        e = self._approved_execution()
        other = Product.objects.create(
            organisation=self.org, responsible=self.user, name="P2", purpose="p"
        )
        wi = self._work_item(product=other)
        resp = self._post("apply/work-item", e, self._wi_body(e, wi))
        self.assertEqual(resp.status_code, 422, resp.content)

    # --- 12 WorkItem alheio é rejeitado -------------------------------------
    def test_work_item_foreign_rejected(self):
        e = self._approved_execution()
        prod_b = Product.objects.create(
            organisation=self.org_b, responsible=self.user_b, name="PB", purpose="p"
        )
        wi_b = self._work_item(org=self.org_b, product=prod_b, user=self.user_b)
        resp = self._post("apply/work-item", e, self._wi_body(e, wi_b))
        self.assertEqual(resp.status_code, 404, resp.content)

    # --- 14/15/16 fecho no_change -------------------------------------------
    def test_no_change_requires_rationale(self):
        e = self._approved_execution()
        body = self._close_body(e)
        del body["rationale"]
        resp = self._post("close-without-application", e, body)
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultApplication.objects.count(), 0)

    def test_no_change_closes_without_touching_entities(self):
        e = self._approved_execution()
        dec = self._decision()
        wi = self._work_item()
        decisions_before = Decision.objects.count()
        work_items_before = WorkItem.objects.count()
        resp = self._post("close-without-application", e, self._close_body(e))
        self.assertEqual(resp.status_code, 201, resp.content)
        e.refresh_from_db()
        dec.refresh_from_db()
        wi.refresh_from_db()
        self.assertEqual(e.status, "completed")
        self.assertEqual(Decision.objects.count(), decisions_before)
        self.assertEqual(WorkItem.objects.count(), work_items_before)
        self.assertEqual(dec.status, "active")
        self.assertEqual(wi.status, "open")
        app = ResultApplication.objects.get()
        self.assertEqual(app.application_type, "no_change")
        self.assertTrue(app.rationale)

    # --- 17 todos os caminhos exigem aprovação ------------------------------
    def test_all_paths_require_approval(self):
        # execução pending (não approved)
        e = self._pending_execution()
        dec = self._decision()
        wi = self._work_item()
        self.assertEqual(
            self._post("apply/decision", e, self._decision_body(e, dec)).status_code, 409
        )
        self.assertEqual(
            self._post("apply/work-item", e, self._wi_body(e, wi)).status_code, 409
        )
        self.assertEqual(
            self._post("close-without-application", e, self._close_body(e)).status_code, 409
        )
        self.assertEqual(ResultApplication.objects.count(), 0)

    # --- 18 todos os caminhos exigem confirmação ----------------------------
    def test_all_paths_require_confirmation(self):
        e = self._approved_execution()
        dec = self._decision()
        wi = self._work_item()
        self.assertEqual(
            self._post("apply/decision", e,
                       self._decision_body(e, dec, confirmation="x")).status_code, 400
        )
        self.assertEqual(
            self._post("apply/work-item", e,
                       self._wi_body(e, wi, confirmation="x")).status_code, 400
        )
        self.assertEqual(
            self._post("close-without-application", e,
                       self._close_body(e, confirmation="x")).status_code, 400
        )

    # --- 19/20/21 uma aplicação por execução (segundo caminho → 409) --------
    def test_only_one_application_per_execution(self):
        e = self._approved_execution()
        # 1.º caminho: fecho no_change → completed.
        self.assertEqual(
            self._post("close-without-application", e, self._close_body(e)).status_code, 201
        )
        e.refresh_from_db()
        dec = self._decision()
        wi = self._work_item()
        # Qualquer segundo caminho → 409.
        self.assertEqual(
            self._post("apply/decision", e, self._decision_body(e, dec)).status_code, 409
        )
        self.assertEqual(
            self._post("apply/work-item", e, self._wi_body(e, wi)).status_code, 409
        )
        self.assertEqual(ResultApplication.objects.count(), 1)

    def test_document_then_decision_rejected(self):
        e = self._approved_execution()
        dec = self._decision()
        # aplica a decisão (completed)
        self.assertEqual(
            self._post("apply/decision", e, self._decision_body(e, dec)).status_code, 201
        )
        e.refresh_from_db()
        wi = self._work_item()
        # decisão seguida de pendência → 409
        self.assertEqual(
            self._post("apply/work-item", e, self._wi_body(e, wi)).status_code, 409
        )

    # --- 22/23 idempotência ------------------------------------------------
    def test_idempotent_and_conflict(self):
        e = self._approved_execution()
        dec = self._decision()
        body = self._decision_body(e, dec)
        r1 = self._post("apply/decision", e, body)
        self.assertEqual(r1.status_code, 201, r1.content)
        app_id = r1.json()["application"]["id"]
        # repetição idêntica → idempotente (200)
        r2 = self._post("apply/decision", e, body)
        self.assertEqual(r2.status_code, 200, r2.content)
        self.assertEqual(r2.json()["application"]["id"], app_id)
        # repetição diferente (outro título) → 409
        r3 = self._post("apply/decision", e, self._decision_body(e, dec, title="Outro"))
        self.assertEqual(r3.status_code, 409, r3.content)
        self.assertEqual(ResultApplication.objects.count(), 1)

    # --- 26/27 auditoria: um evento, sem conteúdo integral ------------------
    def test_audit_single_event_without_content(self):
        e = self._approved_execution()
        wi = self._work_item(notes=NOTES_TOKEN)
        self._post("apply/work-item", e, self._wi_body(e, wi))
        events = AuditEvent.objects.filter(
            action=AuditAction.CHANGE_APPLIED, result=AuditResult.SUCCESS
        )
        self.assertEqual(events.count(), 1)
        blob = str(events.first().metadata)
        self.assertNotIn(NOTES_TOKEN, blob)
        self.assertEqual(events.first().metadata["application_type"], "work_item")
        self.assertEqual(
            events.first().metadata["transition"], "approved->completed"
        )

    def test_no_change_audit_no_rationale(self):
        e = self._approved_execution()
        self._post("close-without-application", e, self._close_body(e))
        event = AuditEvent.objects.get(
            action=AuditAction.CHANGE_APPLIED, result=AuditResult.SUCCESS
        )
        self.assertNotIn(RATIONALE_TOKEN, str(event.metadata))

    # --- Provas negativas: importar/aprovar não alteram Decision/WorkItem ---
    def test_import_and_approve_do_not_touch_official_entities(self):
        dec = self._decision()
        wi = self._work_item()
        dec_updated, wi_updated = dec.updated_at, wi.updated_at
        e = self._make_execution()
        self._import(e)  # importar
        self._approve(e)  # aprovar
        dec.refresh_from_db()
        wi.refresh_from_db()
        self.assertEqual(dec.updated_at, dec_updated)
        self.assertEqual(dec.status, "active")
        self.assertEqual(wi.updated_at, wi_updated)
        self.assertEqual(wi.status, "open")
        self.assertEqual(ResultApplication.objects.count(), 0)
