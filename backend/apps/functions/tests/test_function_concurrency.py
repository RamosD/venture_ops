"""Concorrência das mutações de funções sobre PostgreSQL (F1-P05-PR01).

Duas operações concorrentes sobre a **mesma** função na mesma versão (editar vs
inactivar): exactamente uma vence; a outra recebe conflito. A `version` avança
exactamente uma vez — sem lost update nem dupla transição.
"""
from __future__ import annotations

import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from apps.functions import service
from apps.functions.models import FunctionProfile
from apps.organisations.models import Membership, Organisation


class FunctionConcurrencyTests(TransactionTestCase):
    def test_concurrent_mutations_single_winner(self):
        user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-mvp-forte-1"
        )
        org = Organisation.objects.create(
            name="Empresa", status=Organisation.Status.ACTIVE
        )
        Membership.objects.create(
            user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
        )
        function = service.create_function(
            organisation=org,
            data={
                "name": "Base",
                "actor_type": "human",
                "purpose": "p",
                "responsibilities": "r",
            },
        )

        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()

        def worker(fn, label):
            barrier.wait()
            try:
                fn()
                result = f"ok:{label}"
            except (service.VersionConflict, service.InvalidTransition):
                result = "conflict"
            except Exception as exc:  # noqa: BLE001
                result = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(result)

        def edit():
            service.update_function(
                organisation=org,
                function_id=function.pk,
                expected_version=1,
                changes={"name": "Editada"},
            )

        def deactivate():
            service.deactivate_function(
                organisation=org, function_id=function.pk, expected_version=1
            )

        threads = [
            threading.Thread(target=worker, args=(edit, "edit")),
            threading.Thread(target=worker, args=(deactivate, "deactivate")),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(sum(o.startswith("ok:") for o in outcomes), 1, outcomes)
        self.assertIn("conflict", outcomes)
        function.refresh_from_db()
        self.assertEqual(function.version, 2)  # exactamente uma mutação aplicada
