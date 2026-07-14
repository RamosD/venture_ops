"""Concorrência da aplicação documental (F1-P06-PR04, teste 26).

Duas aplicações **idênticas** concorrentes sobre a mesma execução `approved`:
exactamente uma cria a `DocumentVersion` + `ResultApplication` e conclui a
execução; a outra é idempotente (devolve a existente). Nunca resultam duas
versões, duas aplicações nem duas transições — o bloqueio da execução e a
unicidade por execução (defesa final) garantem-no.
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
from apps.executions import application_service, result_service, review_service
from apps.executions.application_service import DOCUMENT_APPLY_CONFIRMATION
from apps.executions.models import AIExecution, ResultApplication
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product


class ResultApplicationConcurrencyTests(TransactionTestCase):
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
            product_id=self.product.pk,
        )
        self.execution = create_execution(
            actor=self.user, organisation=self.org,
            data={"product": self.product.pk, "function_profile": self.function.pk,
                  "title": "E", "objective": "o", "request_instructions": "i",
                  "expected_output_format": "md", "execution_mode": "manual_local",
                  "context": [{"document_version": str(v.pk)}]},
        )
        result_service.import_result(
            actor=self.user, organisation=self.org, execution_id=self.execution.pk,
            expected_version=1, content="resultado", source_tool="T",
        )
        self.execution.refresh_from_db()
        review_service.approve_result(
            actor=self.user, membership=self.membership, organisation=self.org,
            execution_id=self.execution.pk, attempt_number=1,
            expected_version=self.execution.version,
        )
        self.execution.refresh_from_db()
        self.target, self.target_v = create_document(
            actor=self.user, organisation=self.org, title="Alvo",
            document_type=DocumentType.PRODUCT_VISION, content="v1",
            product_id=self.product.pk,
        )

    def test_two_concurrent_identical_applications_single_version(self):
        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()
        exec_version = self.execution.version
        doc_version = self.target.version

        def worker(i):
            barrier.wait()
            try:
                _app, created = application_service.apply_document(
                    actor=self.user, membership=self.membership,
                    organisation=self.org, execution_id=self.execution.pk,
                    expected_execution_version=exec_version,
                    target_document_id=self.target.pk,
                    expected_document_version=doc_version,
                    content="conteúdo final revisto",
                    change_summary="Aplica",
                    confirmation=DOCUMENT_APPLY_CONFIRMATION,
                    attempt_number=1,
                )
                out = "created" if created else "idempotent"
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

        # Exactamente uma criação; a outra idempotente, nunca duas criações.
        self.assertEqual(outcomes.count("created"), 1, outcomes)
        self.assertIn("idempotent", outcomes, outcomes)
        self.assertEqual(
            ResultApplication.objects.filter(execution=self.execution).count(), 1
        )
        self.target.refresh_from_db()
        self.assertEqual(self.target.versions.count(), 2)  # exactamente uma nova versão
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "completed")
