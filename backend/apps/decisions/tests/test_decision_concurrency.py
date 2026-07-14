"""Concorrência da substituição de decisões sobre PostgreSQL (F1-P04-PR04).

Duas substituições concorrentes da **mesma** decisão activa: exactamente uma é
aceite (cria a nova e marca a anterior `superseded`) e a outra recebe conflito;
nunca resultam duas substituições válidas — sem cadeia ramificada.
"""
from __future__ import annotations

import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from apps.decisions import service
from apps.decisions.models import Decision
from apps.organisations.models import Membership, Organisation


class DecisionConcurrencyTests(TransactionTestCase):
    def test_concurrent_supersede_only_one_wins(self):
        user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-mvp-forte-1"
        )
        org = Organisation.objects.create(
            name="Empresa", status=Organisation.Status.ACTIVE
        )
        Membership.objects.create(
            user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
        )
        original = service.create_decision(
            actor=user,
            organisation=org,
            data={"title": "Base", "context": "c", "decision_text": "d"},
        )

        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()

        def worker(marker: str):
            barrier.wait()
            try:
                service.supersede_decision(
                    actor=user,
                    organisation=org,
                    decision_id=original.pk,
                    expected_version=1,  # ambos usam a versão original
                    data={"title": marker, "context": "c", "decision_text": "d"},
                )
                result = f"ok:{marker}"
            except (service.VersionConflict, service.AlreadySuperseded):
                result = "conflict"
            except Exception as exc:  # noqa: BLE001
                result = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(result)

        threads = [threading.Thread(target=worker, args=(m,)) for m in ("A", "B")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactamente uma substituição válida.
        self.assertEqual(sum(o.startswith("ok:") for o in outcomes), 1, outcomes)
        self.assertIn("conflict", outcomes)
        original.refresh_from_db()
        self.assertEqual(original.status, Decision.Status.SUPERSEDED)
        # Apenas uma decisão substituiu a original (cadeia linear).
        self.assertEqual(Decision.objects.filter(supersedes=original).count(), 1)
        # Total: original + uma nova.
        self.assertEqual(Decision.objects.count(), 2)
