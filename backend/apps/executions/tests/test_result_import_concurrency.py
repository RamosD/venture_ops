"""Concorrência da importação de resultado (F1-P06-PR01, teste 19).

Duas importações concorrentes da **mesma** execução `prepared`: exactamente uma
cria a tentativa 1 e transita a execução; a outra recebe conflito. Nunca resultam
duas tentativas nem duas transições.
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
from apps.executions import result_service
from apps.executions.models import AIExecution, ResultAttempt
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product


class ResultImportConcurrencyTests(TransactionTestCase):
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
        Membership.objects.create(
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

    def test_two_concurrent_imports_single_attempt(self):
        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()

        def worker(i):
            barrier.wait()
            try:
                result_service.import_result(
                    actor=self.user, organisation=self.org,
                    execution_id=self.execution.pk, expected_version=1,
                    content=f"resultado {i}", source_tool="T",
                )
                out = "ok"
            except (result_service.VersionConflict, result_service.ExecutionNotPrepared):
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
        self.assertEqual(ResultAttempt.objects.filter(execution=self.execution).count(), 1)
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "result_pending_validation")
        self.assertEqual(self.execution.version, 2)  # exactamente uma transição
