"""Concorrência da revisão de resultado (F1-P06-PR03, teste 19).

Duas revisões concorrentes sobre a **mesma** tentativa actual: exactamente uma
cria a `ResultReview` e transita a execução; a outra recebe conflito. Nunca
resultam duas revisões nem duas transições — o bloqueio da execução, a validação
de `expected_version` e a constraint única sobre `result_attempt` (defesa final)
garantem-no.
"""
from __future__ import annotations

import shutil
import tempfile
import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase, override_settings

from apps.documents.models import DocumentType
from apps.documents.service import create_document
from apps.executions import result_service, review_service
from apps.executions.models import AIExecution, ResultReview
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product


class ResultReviewConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

        self.user = get_user_model().objects.create_user(
            email="a@x.pt", password="senha-123"
        )
        self.org = Organisation.objects.create(
            name="Empresa", status=Organisation.Status.ACTIVE
        )
        self.membership = Membership.objects.create(
            user=self.user, organisation=self.org,
            role=Membership.Role.OWNER, is_active=True,
        )
        self.product = Product.objects.create(
            organisation=self.org, responsible=self.user, name="P", purpose="p"
        )
        self.function = create_function(
            organisation=self.org,
            data={"name": "F", "actor_type": "human", "purpose": "p",
                  "responsibilities": "r"},
        )
        _doc, v = create_document(
            actor=self.user, organisation=self.org, title="Ctx",
            document_type=DocumentType.COMPANY_CONTEXT, content="c",
        )
        self.execution = create_execution(
            actor=self.user, organisation=self.org,
            data={"product": self.product.pk, "function_profile": self.function.pk,
                  "title": "E", "objective": "o", "request_instructions": "i",
                  "expected_output_format": "md", "execution_mode": "manual_local",
                  "context": [{"document_version": str(v.pk)}]},
        )
        # Importa a tentativa 1 → result_pending_validation (versão 2).
        result_service.import_result(
            actor=self.user, organisation=self.org,
            execution_id=self.execution.pk, expected_version=1,
            content="resultado", source_tool="T",
        )
        self.execution.refresh_from_db()

    def test_two_concurrent_reviews_single_review(self):
        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()
        expected = self.execution.version  # ambos usam a mesma versão actual

        def worker(i):
            barrier.wait()
            try:
                review_service.approve_result(
                    actor=self.user, membership=self.membership,
                    organisation=self.org, execution_id=self.execution.pk,
                    attempt_number=1, expected_version=expected,
                )
                out = "ok"
            except (
                review_service.VersionConflict,
                review_service.ExecutionNotPendingValidation,
                review_service.AlreadyReviewed,
            ):
                out = "conflict"
            except Exception as exc:  # noqa: BLE001
                out = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(out)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(outcomes.count("ok"), 1, outcomes)
        self.assertIn("conflict", outcomes)
        self.assertEqual(
            ResultReview.objects.filter(execution=self.execution).count(), 1
        )
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "approved")
        self.assertEqual(self.execution.version, expected + 1)  # uma transição
