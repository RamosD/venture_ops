"""Testes da revisão humana de resultados (F1-P06-PR03, MVP-14).

Cobrem a criação de revisões imutáveis (aprovar/rejeitar/pedir correcção), a
autorização (só Owner activo), as transições pela política central, a preservação
do histórico (tentativas e revisões), a exigência de observações, a dupla revisão,
a versão obsoleta, o isolamento cross-org, a imutabilidade e a auditoria sem
conteúdo. **Aprovar ≠ aplicar**: aprovar não cria versões, não altera
Product/Decision/WorkItem, não cria aplicação e não conclui a execução.
"""
from __future__ import annotations

import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.audit.models import AuditAction, AuditEvent, AuditResult
from apps.decisions.models import Decision
from apps.documents.models import DocumentType, DocumentVersion
from apps.documents.service import create_document
from apps.executions.exceptions import ResultReviewImmutableError
from apps.executions.models import AIExecution, ResultAttempt, ResultReview
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.work_items.models import WorkItem

RESULT_TOKEN = "RESULTADOxSECRETO1234"
OBS_TOKEN = "OBSERVACAOxSECRETA9876"


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
class ResultReviewTests(TestCase):
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
        self.execution = self._make_execution()

    # --- Fábricas -----------------------------------------------------------
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

    def _import(self, client=None, execution=None, content=None):
        execution = execution or self.execution
        body = {
            "expected_version": execution.version,
            "content": content or f"# Resultado\n{RESULT_TOKEN}",
            "source_tool": "ChatGPT",
        }
        resp = (client or self.client_a).post(
            f"/api/v1/executions/{execution.pk}/result-attempts", body, format="json"
        )
        assert resp.status_code == 201, resp.content
        execution.refresh_from_db()
        return resp.json()

    def _pending(self):
        """Importa um resultado e devolve a execução em result_pending_validation."""
        self._import()
        self.execution.refresh_from_db()
        return self.execution

    def _url(self, op, execution=None, attempt_number=1):
        execution = execution or self.execution
        return (
            f"/api/v1/executions/{execution.pk}/result-attempts/"
            f"{attempt_number}/{op}"
        )

    def _make_decision(self):
        return Decision.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="D", context="c", decision_text="d",
        )

    def _make_work_item(self):
        return WorkItem.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="W", work_type=WorkItem.WorkType.ACTION,
            status=WorkItem.Status.OPEN,
        )

    # --- 1. Owner aprova tentativa actual -----------------------------------
    def test_owner_approves_current_attempt(self):
        exec_ = self._pending()
        resp = self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        body = resp.json()
        self.assertEqual(body["review"]["decision"], "approved")
        self.assertEqual(body["review"]["attempt_number"], 1)
        self.assertEqual(body["execution"]["status"], "approved")
        self.assertEqual(ResultReview.objects.count(), 1)
        review = ResultReview.objects.get()
        self.assertEqual(review.reviewer_id, self.user.pk)  # deriva do autenticado

    # --- 2. não-Owner é rejeitado -------------------------------------------
    def test_non_owner_rejected(self):
        exec_ = self._pending()
        # Simula um utilizador SEM papel Owner (o MVP só tem Owner na enum, mas a
        # coluna aceita outro valor — autorização é imposta pelo serviço/view).
        viewer = get_user_model().objects.create_user(
            email="v@x.pt", password="senha-123"
        )
        Membership.objects.create(
            user=viewer, organisation=self.org, role="viewer", is_active=True
        )
        client_v = _client("v@x.pt")
        resp = client_v.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(resp.status_code, 403, resp.content)
        self.assertEqual(ResultReview.objects.count(), 0)
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "result_pending_validation")

    # --- 3. aprovação muda apenas para approved -----------------------------
    def test_approval_transitions_only_to_approved(self):
        exec_ = self._pending()
        v0 = exec_.version
        self.client_a.post(
            self._url("approve"), {"expected_version": v0}, format="json"
        )
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "approved")
        self.assertEqual(exec_.version, v0 + 1)  # exactamente uma transição
        self.assertNotEqual(exec_.status, "completed")

    # --- 4. aprovação não cria versões documentais --------------------------
    def test_approval_creates_no_document_version(self):
        exec_ = self._pending()
        before = DocumentVersion.objects.count()
        self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(DocumentVersion.objects.count(), before)

    # --- 5/6/7. aprovação não altera Product/Decision/WorkItem --------------
    def test_approval_does_not_touch_official_entities(self):
        decision = self._make_decision()
        work_item = self._make_work_item()
        exec_ = self._pending()
        prod_updated = self.product.updated_at
        dec_updated = decision.updated_at
        wi_updated = work_item.updated_at
        decisions_before = Decision.objects.count()
        work_items_before = WorkItem.objects.count()

        self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )

        self.product.refresh_from_db()
        decision.refresh_from_db()
        work_item.refresh_from_db()
        self.assertEqual(self.product.updated_at, prod_updated)
        self.assertEqual(decision.updated_at, dec_updated)
        self.assertEqual(decision.status, "active")
        self.assertEqual(work_item.updated_at, wi_updated)
        self.assertEqual(work_item.status, "open")
        self.assertEqual(Decision.objects.count(), decisions_before)
        self.assertEqual(WorkItem.objects.count(), work_items_before)

    # --- 8. aprovação não cria aplicação ------------------------------------
    def test_approval_creates_no_application(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        exec_.refresh_from_db()
        # Aprovar não aplica: a execução fica em `approved` (nunca `completed`) e
        # **nenhuma** `ResultApplication` é criada (o modelo existe desde PR04; a
        # aplicação é uma operação posterior e explícita).
        self.assertEqual(exec_.status, "approved")
        from apps.executions.models import ResultApplication

        self.assertEqual(
            ResultApplication.objects.filter(execution=exec_).count(), 0
        )

    # --- 9. rejeição exige observações --------------------------------------
    def test_rejection_requires_observations(self):
        exec_ = self._pending()
        resp = self.client_a.post(
            self._url("reject"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultReview.objects.count(), 0)
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "result_pending_validation")

    # --- 10. rejeição muda para rejected ------------------------------------
    def test_rejection_transitions_to_rejected(self):
        exec_ = self._pending()
        resp = self.client_a.post(
            self._url("reject"),
            {"expected_version": exec_.version, "observations": "Não serve."},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "rejected")
        self.assertEqual(ResultReview.objects.get().decision, "rejected")

    # --- 11. rejected é terminal --------------------------------------------
    def test_rejected_is_terminal(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("reject"),
            {"expected_version": exec_.version, "observations": "Não serve."},
            format="json",
        )
        exec_.refresh_from_db()
        # Qualquer comando posterior é recusado (execução não está por validar).
        for op, extra in (
            ("approve", {}),
            ("reject", {"observations": "x"}),
            ("request-correction", {"observations": "x"}),
        ):
            resp = self.client_a.post(
                self._url(op),
                {"expected_version": exec_.version, **extra},
                format="json",
            )
            self.assertEqual(resp.status_code, 409, (op, resp.content))
        self.assertEqual(ResultReview.objects.count(), 1)

    # --- 12. correcção exige observações ------------------------------------
    def test_correction_requires_observations(self):
        exec_ = self._pending()
        resp = self.client_a.post(
            self._url("request-correction"),
            {"expected_version": exec_.version},
            format="json",
        )
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultReview.objects.count(), 0)

    # --- 13/14/15. correcção volta a prepared; preserva tentativa e revisão --
    def test_correction_returns_to_prepared_preserving_history(self):
        exec_ = self._pending()
        attempt = ResultAttempt.objects.get()
        resp = self.client_a.post(
            self._url("request-correction"),
            {"expected_version": exec_.version, "observations": "Corrige X."},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "prepared")
        # Tentativa preservada + current_result_attempt preservado.
        self.assertTrue(ResultAttempt.objects.filter(pk=attempt.pk).exists())
        self.assertEqual(exec_.current_result_attempt_id, attempt.pk)
        # Revisão preservada.
        review = ResultReview.objects.get()
        self.assertEqual(review.decision, "correction_requested")
        self.assertEqual(review.result_attempt_id, attempt.pk)

    # --- 16. nova importação após correcção cria tentativa seguinte ---------
    def test_new_import_after_correction_creates_next_attempt(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("request-correction"),
            {"expected_version": exec_.version, "observations": "Corrige X."},
            format="json",
        )
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "prepared")
        body = self._import(content="# Segunda\nOUTRO")
        self.assertEqual(body["attempt_number"], 2)
        self.assertEqual(ResultAttempt.objects.filter(execution=exec_).count(), 2)
        exec_.refresh_from_db()
        self.assertEqual(exec_.status, "result_pending_validation")

    # --- 17. tentativa histórica não pode ser revista novamente -------------
    def test_historical_attempt_cannot_be_reviewed_again(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("request-correction"),
            {"expected_version": exec_.version, "observations": "Corrige X."},
            format="json",
        )
        exec_.refresh_from_db()
        self._import(content="# Segunda\nOUTRO")  # tentativa 2 = actual
        exec_.refresh_from_db()
        # Tentar aprovar a tentativa 1 (histórica) devolve 409.
        resp = self.client_a.post(
            self._url("approve", attempt_number=1),
            {"expected_version": exec_.version},
            format="json",
        )
        self.assertEqual(resp.status_code, 409, resp.content)

    # --- 18. dupla revisão devolve 409 --------------------------------------
    def test_double_review_returns_409(self):
        exec_ = self._pending()
        r1 = self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(r1.status_code, 201, r1.content)
        exec_.refresh_from_db()  # agora `approved`, versão incrementada
        # Segunda revisão da mesma tentativa (com a versão actual) → 409: a execução
        # já não está por validar. Nunca cria uma segunda revisão. (O caminho da
        # constraint única sobre `result_attempt` — `AlreadyReviewed` auditada como
        # `denied` — é a defesa final de concorrência; ver teste de concorrência.)
        r2 = self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(r2.status_code, 409, r2.content)
        self.assertEqual(ResultReview.objects.count(), 1)

    # --- 18b. dupla revisão pela constraint única é auditada como denied -----
    def test_already_reviewed_path_audited_denied(self):
        # Exercita directamente o serviço no cenário em que a tentativa já tem uma
        # revisão mas a execução ainda estaria por validar (defesa final de BD): a
        # view audita como `denied`. Simula-se recolocando o estado por validar.
        exec_ = self._pending()
        attempt = ResultAttempt.objects.get()
        # Primeira revisão (aprovação) — cria a ResultReview.
        self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        # Recoloca artificialmente o estado por validar (sem passar pela política)
        # para forçar o caminho AlreadyReviewed na segunda revisão.
        exec_.refresh_from_db()
        AIExecution.objects.filter(pk=exec_.pk).update(
            status="result_pending_validation"
        )
        exec_.refresh_from_db()
        r2 = self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(r2.status_code, 409, r2.content)
        self.assertEqual(ResultReview.objects.filter(result_attempt=attempt).count(), 1)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.RESULT_APPROVED, result=AuditResult.DENIED
            ).exists()
        )

    # --- 20. versão obsoleta devolve 409 ------------------------------------
    def test_stale_version_returns_409(self):
        exec_ = self._pending()
        resp = self.client_a.post(
            self._url("approve"),
            {"expected_version": exec_.version - 1},
            format="json",
        )
        self.assertEqual(resp.status_code, 409, resp.content)
        self.assertEqual(ResultReview.objects.count(), 0)

    # --- 21. revisão alheia devolve 404 e é auditada ------------------------
    def test_cross_org_review_404_and_audited(self):
        exec_ = self._pending()
        resp = self.client_b.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        self.assertEqual(resp.status_code, 404, resp.content)
        self.assertEqual(ResultReview.objects.count(), 0)
        self.assertTrue(
            AuditEvent.objects.filter(
                action=AuditAction.CROSS_ORG_ACCESS_ATTEMPT,
                result=AuditResult.DENIED,
            ).exists()
        )

    # --- 22. revisões são imutáveis -----------------------------------------
    def test_reviews_are_immutable(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        review = ResultReview.objects.get()
        review.observations = "alterado"
        with self.assertRaises(ResultReviewImmutableError):
            review.save()
        with self.assertRaises(ResultReviewImmutableError):
            review.delete()
        with self.assertRaises(ResultReviewImmutableError):
            ResultReview.objects.filter(pk=review.pk).update(observations="x")
        with self.assertRaises(ResultReviewImmutableError):
            ResultReview.objects.all().delete()

    # --- 23. eventos de aprovação, rejeição e correcção são emitidos --------
    def test_events_emitted_for_each_decision(self):
        # aprovação
        exec_ = self._pending()
        self.client_a.post(
            self._url("approve"), {"expected_version": exec_.version}, format="json"
        )
        # rejeição (nova execução)
        self.execution = self._make_execution()
        exec_r = self._pending()
        self.client_a.post(
            self._url("reject"),
            {"expected_version": exec_r.version, "observations": "não"},
            format="json",
        )
        # correcção (nova execução)
        self.execution = self._make_execution()
        exec_c = self._pending()
        self.client_a.post(
            self._url("request-correction"),
            {"expected_version": exec_c.version, "observations": "corrige"},
            format="json",
        )
        for action in (
            AuditAction.RESULT_APPROVED,
            AuditAction.RESULT_REJECTED,
            AuditAction.CORRECTION_REQUESTED,
        ):
            self.assertTrue(
                AuditEvent.objects.filter(
                    action=action, result=AuditResult.SUCCESS
                ).exists(),
                action,
            )

    # --- 24. auditoria não contém resultado ou observações integrais --------
    def test_audit_has_no_result_or_observations(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("reject"),
            {"expected_version": exec_.version, "observations": OBS_TOKEN},
            format="json",
        )
        event = AuditEvent.objects.get(action=AuditAction.RESULT_REJECTED)
        blob = str(event.metadata)
        self.assertNotIn(OBS_TOKEN, blob)
        self.assertNotIn(RESULT_TOKEN, blob)
        # Metadados esperados presentes.
        self.assertEqual(event.metadata["operation"], "reject")
        self.assertEqual(event.metadata["attempt_number"], 1)
        self.assertIn("review_id", event.metadata)
        self.assertEqual(
            event.metadata["transition"], "result_pending_validation->rejected"
        )
        self.assertIn("execution_version", event.metadata)

    # --- Extra: entrada estrita (rejeita decision/reviewer/status) ----------
    def test_strict_input_rejects_internal_fields(self):
        exec_ = self._pending()
        resp = self.client_a.post(
            self._url("approve"),
            {"expected_version": exec_.version, "decision": "rejected",
             "reviewer": str(self.user_b.pk), "status": "completed"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400, resp.content)
        self.assertEqual(ResultReview.objects.count(), 0)

    # --- Extra: aprovar exige tentativa actual (número errado) --------------
    def test_reviews_listing_minimal(self):
        exec_ = self._pending()
        self.client_a.post(
            self._url("reject"),
            {"expected_version": exec_.version, "observations": "não " + RESULT_TOKEN},
            format="json",
        )
        resp = self.client_a.get(f"/api/v1/executions/{exec_.pk}/reviews")
        self.assertEqual(resp.status_code, 200, resp.content)
        results = resp.json()["results"]
        self.assertEqual(len(results), 1)
        # Sem chaves de conteúdo do resultado (só metadados + observações próprias).
        self.assertNotIn("content", results[0])
        self.assertEqual(results[0]["decision"], "rejected")
