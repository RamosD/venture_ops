"""Concorrência das transições de pendências sobre PostgreSQL (F1-P04-PR05).

Duas transições concorrentes (concluir vs cancelar) da **mesma** pendência
`open`: exactamente uma vence; a outra recebe conflito. Nunca resultam duas
transições válidas — o estado final é único.
"""
from __future__ import annotations

import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from apps.organisations.models import Membership, Organisation
from apps.portfolio.models import Product
from apps.work_items import service
from apps.work_items.models import WorkItem


class WorkItemConcurrencyTests(TransactionTestCase):
    def test_concurrent_transitions_single_winner(self):
        user = get_user_model().objects.create_user(
            email="owner@x.pt", password="senha-mvp-forte-1"
        )
        org = Organisation.objects.create(
            name="Empresa", status=Organisation.Status.ACTIVE
        )
        Membership.objects.create(
            user=user, organisation=org, role=Membership.Role.OWNER, is_active=True
        )
        product = Product.objects.create(
            organisation=org, responsible=user, name="P", purpose="p"
        )
        item = service.create_work_item(
            actor=user,
            organisation=org,
            data={
                "product": product.pk,
                "title": "Base",
                "work_type": "action",
            },
        )

        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        lock = threading.Lock()

        def worker(fn, label):
            barrier.wait()
            try:
                fn(organisation=org, work_item_id=item.pk, expected_version=1)
                result = f"ok:{label}"
            except (service.VersionConflict, service.InvalidTransition):
                result = "conflict"
            except Exception as exc:  # noqa: BLE001
                result = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with lock:
                outcomes.append(result)

        threads = [
            threading.Thread(
                target=worker, args=(service.complete_work_item, "complete")
            ),
            threading.Thread(
                target=worker, args=(service.cancel_work_item, "cancel")
            ),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(sum(o.startswith("ok:") for o in outcomes), 1, outcomes)
        self.assertIn("conflict", outcomes)
        item.refresh_from_db()
        self.assertIn(
            item.status, (WorkItem.Status.COMPLETED, WorkItem.Status.CANCELLED)
        )
        self.assertEqual(item.version, 2)  # exactamente uma transição aplicada
