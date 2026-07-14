"""Concorrência entre tipos de aplicação (F1-P06-PR05, teste 24).

Duas aplicações de **tipos diferentes** (decisão vs pendência) concorrentes sobre a
mesma execução `approved`: exactamente uma vence (cria a `ResultApplication` e
conclui a execução); a outra recebe conflito. A execução produz **no máximo uma**
aplicação (unicidade por execução + bloqueio da execução).
"""
from __future__ import annotations

import shutil
import tempfile
import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase, override_settings

from apps.decisions.models import Decision
from apps.documents.models import DocumentType
from apps.documents.service import create_document
from apps.executions import (
    application_service,
    result_service,
    review_service,
)
from apps.executions.application_service import (
    DECISION_APPLY_CONFIRMATION,
    WORK_ITEM_APPLY_CONFIRMATION,
)
from apps.executions.models import ResultApplication
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.work_items.models import WorkItem


class ApplicationPathsConcurrencyTests(TransactionTestCase):
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
        self.decision = Decision.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="D0", context="c0", decision_text="t0",
        )
        self.work_item = WorkItem.objects.create(
            organisation=self.org, product=self.product, responsible=self.user,
            title="W0", work_type=WorkItem.WorkType.ACTION,
            status=WorkItem.Status.OPEN,
        )

    def test_two_types_single_winner(self):
        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()
        exec_version = self.execution.version

        def do_decision():
            barrier.wait()
            try:
                application_service.apply_decision(
                    actor=self.user, membership=self.membership, organisation=self.org,
                    execution_id=self.execution.pk, expected_execution_version=exec_version,
                    target_decision_id=self.decision.pk,
                    expected_decision_version=self.decision.version,
                    title="Nova", context="ctx", decision_text="txt",
                    confirmation=DECISION_APPLY_CONFIRMATION, attempt_number=1,
                )
                out = "decision"
            except application_service.ApplicationError as exc:
                out = f"conflict:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(out)

        def do_work_item():
            barrier.wait()
            try:
                application_service.apply_work_item(
                    actor=self.user, membership=self.membership, organisation=self.org,
                    execution_id=self.execution.pk, expected_execution_version=exec_version,
                    target_work_item_id=self.work_item.pk,
                    expected_work_item_version=self.work_item.version,
                    confirmation=WORK_ITEM_APPLY_CONFIRMATION, attempt_number=1,
                )
                out = "work_item"
            except application_service.ApplicationError as exc:
                out = f"conflict:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(out)

        threads = [threading.Thread(target=do_decision),
                   threading.Thread(target=do_work_item)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        winners = [o for o in outcomes if o in ("decision", "work_item")]
        conflicts = [o for o in outcomes if o.startswith("conflict")]
        self.assertEqual(len(winners), 1, outcomes)
        self.assertEqual(len(conflicts), 1, outcomes)
        self.assertEqual(
            ResultApplication.objects.filter(execution=self.execution).count(), 1
        )
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "completed")
