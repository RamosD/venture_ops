"""Concorrência optimista real de `Product` sobre PostgreSQL (F1-P03-PR04).

Duas actualizações concorrentes usando a **mesma** `version`: exactamente uma é
aceite (incrementa para 2) e a outra recebe conflito; sem lost update — o valor
final é o da actualização vencedora.
"""
from __future__ import annotations

import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from apps.organisations.models import Membership, Organisation
from apps.portfolio import service
from apps.portfolio.models import Product


class ProductConcurrencyTests(TransactionTestCase):
    def test_concurrent_edit_same_version_one_wins(self):
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
            organisation=org, responsible=user, name="Base", purpose="p"
        )

        workers = 2
        barrier = threading.Barrier(workers)
        outcomes: list[str] = []
        outcomes_lock = threading.Lock()

        def worker(new_name: str):
            barrier.wait()
            try:
                service.update_product(
                    organisation=org,
                    product_id=product.pk,
                    expected_version=1,  # ambos usam a versão original
                    changes={"name": new_name},
                )
                result = f"ok:{new_name}"
            except service.VersionConflict:
                result = "conflict"
            except Exception as exc:  # noqa: BLE001 - registar qualquer outro erro
                result = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with outcomes_lock:
                outcomes.append(result)

        threads = [
            threading.Thread(target=worker, args=(name,))
            for name in ("Vencedor A", "Vencedor B")
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        product.refresh_from_db()
        # Exactamente uma actualização aceite; a outra em conflito.
        self.assertEqual(sum(o.startswith("ok:") for o in outcomes), 1)
        self.assertIn("conflict", outcomes)
        # Incremento exactamente uma vez (sem lost update).
        self.assertEqual(product.version, 2)
        # O nome final corresponde à actualização vencedora.
        winner = next(o.split(":", 1)[1] for o in outcomes if o.startswith("ok:"))
        self.assertEqual(product.name, winner)
