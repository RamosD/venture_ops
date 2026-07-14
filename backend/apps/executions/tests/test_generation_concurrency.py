"""Concorrência e consistência da geração do pacote (F1-P05-PR06).

Valida que:
- duas gerações simultâneas da mesma execução, com as mesmas políticas e
  confirmações, produzem **checksums idênticos** e não alteram a execução;
- uma alteração de `export_policy` concorrente com a geração produz sempre um
  **estado coerente** (a geração vê o documento permitido e completo, ou é
  bloqueada) — nunca um pacote parcial ou inconsistente; as versões congeladas e
  os snapshots permanecem imutáveis.
"""
from __future__ import annotations

import shutil
import tempfile
import threading

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase, override_settings

from apps.documents.models import Document, DocumentType, ExportPolicy
from apps.documents.service import create_document
from apps.executions import context_package as cp
from apps.executions.service import create_execution
from apps.functions.service import create_function
from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product


class GenerationConcurrencyTests(TransactionTestCase):
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
        self.document, self.version = create_document(
            actor=self.user, organisation=self.org, title="Doc A",
            document_type=DocumentType.COMPANY_CONTEXT, content="conteudo A",
            export_policy=ExportPolicy.ALLOWED,
        )
        self.execution = create_execution(
            actor=self.user, organisation=self.org,
            data={
                "product": self.product.pk,
                "function_profile": self.function.pk,
                "title": "E", "objective": "o", "request_instructions": "i",
                "expected_output_format": "md", "execution_mode": "manual_local",
                "context": [{"document_version": str(self.version.pk)}],
            },
        )

    def _generate(self):
        return cp.generate_package(
            execution=self.execution, fmt=cp.SINGLE_MARKDOWN,
            confirmed_document_ids=[], max_bytes=settings.CONTEXT_PACKAGE_MAX_BYTES,
        )

    def test_two_concurrent_generations_identical_checksum(self):
        barrier = threading.Barrier(2)
        results: list = []
        lock = threading.Lock()

        def worker():
            barrier.wait()
            try:
                result = self._generate()
                out = ("ok", result.checksum, result.package_bytes)
            except Exception as exc:  # noqa: BLE001
                out = ("error", type(exc).__name__, b"")
            finally:
                connections.close_all()
            with lock:
                results.append(out)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertTrue(all(r[0] == "ok" for r in results), results)
        self.assertEqual(results[0][1], results[1][1])  # checksums idênticos
        self.assertEqual(results[0][2], results[1][2])  # bytes idênticos
        # A execução não muda (sem duplicação de estado).
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "prepared")
        self.assertEqual(self.execution.version, 1)
        self.assertEqual(self.execution.context_documents.count(), 1)

    def test_policy_flip_during_generation_is_consistent(self):
        barrier = threading.Barrier(2)
        gen_outcome: dict = {}
        lock = threading.Lock()

        def generator():
            barrier.wait()
            try:
                result = self._generate()
                out = ("ok", result)
            except cp.PackageBlocked:
                out = ("blocked", None)
            except Exception as exc:  # noqa: BLE001
                out = ("error", type(exc).__name__)
            finally:
                connections.close_all()
            with lock:
                gen_outcome["result"] = out

        def flipper():
            barrier.wait()
            try:
                # UPDATE espera pelo lock select_for_update da geração → serializa.
                Document.objects.filter(pk=self.document.pk).update(
                    export_policy=ExportPolicy.DENIED
                )
            finally:
                connections.close_all()

        threads = [threading.Thread(target=generator), threading.Thread(target=flipper)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        outcome = gen_outcome["result"]
        # Coerência: ou gerou um pacote completo (viu allowed), ou foi bloqueada.
        self.assertIn(outcome[0], ("ok", "blocked"), outcome)
        if outcome[0] == "ok":
            # Pacote completo: contém o conteúdo do documento (não parcial).
            self.assertIn("conteudo A", outcome[1].markdown)

        # Versões congeladas e execução imutáveis, independentemente da ordem.
        self.execution.refresh_from_db()
        self.assertEqual(self.execution.status, "prepared")
        self.assertEqual(self.execution.version, 1)
        self.assertEqual(
            self.execution.context_documents.first().document_version_id,
            self.version.pk,
        )

        # Estado final coerente: B ficou denied → nova geração bloqueia.
        self.document.refresh_from_db()
        self.assertEqual(self.document.export_policy, ExportPolicy.DENIED)
        with self.assertRaises(cp.PackageBlocked):
            self._generate()
