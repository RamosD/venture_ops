"""Concorrência optimista real da edição documental sobre PostgreSQL.

Duas edições concorrentes com a **mesma** `expected_version`: exactamente uma é
aceite (cria v2 e incrementa `Document.version`) e a outra recebe conflito; sem
lost update. O objecto escrito pela edição perdedora é removido (limpeza de
órfão), pelo que apenas a versão vencedora fica referenciada.
"""
from __future__ import annotations

import shutil
import tempfile
import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase, override_settings

from apps.documents import service
from apps.documents.models import Document, DocumentVersion
from apps.organisations.models import Membership, Organisation


class DocumentConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._override = override_settings(STORAGE_ROOT=self._tmp)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)

    def test_concurrent_edits_no_lost_update(self):
        user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-mvp-forte-1"
        )
        org = Organisation.objects.create(
            name="Empresa", status=Organisation.Status.ACTIVE
        )
        Membership.objects.create(
            user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
        )
        document, _v1 = service.create_document(
            actor=user,
            organisation=org,
            title="Base",
            document_type="contexto_da_empresa",
            content="v1",
        )

        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()

        def worker(marker: str):
            barrier.wait()
            try:
                service.update_document(
                    actor=user,
                    organisation=org,
                    document_id=document.pk,
                    expected_version=1,  # ambos usam a versão original
                    content=f"conteudo {marker}",
                )
                result = f"ok:{marker}"
            except service.VersionConflict:
                result = "conflict"
            except Exception as exc:  # noqa: BLE001
                result = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(result)

        threads = [
            threading.Thread(target=worker, args=(m,)) for m in ("A", "B")
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        document.refresh_from_db()
        self.assertEqual(sum(o.startswith("ok:") for o in outcomes), 1, outcomes)
        self.assertIn("conflict", outcomes)
        # Incremento exactamente uma vez (sem lost update).
        self.assertEqual(document.version, 2)
        # Apenas v1 e a v2 vencedora existem.
        self.assertEqual(
            DocumentVersion.objects.filter(document=document).count(), 2
        )
        winner = next(o.split(":", 1)[1] for o in outcomes if o.startswith("ok:"))
        content = service.read_content(document.current_version)
        self.assertEqual(content, f"conteudo {winner}")
