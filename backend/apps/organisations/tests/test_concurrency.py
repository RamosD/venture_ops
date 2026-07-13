"""Concorrência real do onboarding sobre PostgreSQL (Parte E)."""
import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from apps.organisations import service
from apps.organisations.models import Membership, Organisation


class OnboardingConcurrencyTests(TransactionTestCase):
    def test_concurrent_onboarding_creates_exactly_one_company(self):
        user = get_user_model().objects.create_user(
            email="race@x.pt", password="senha-mvp-forte-1"
        )
        workers = 2
        barrier = threading.Barrier(workers)
        outcomes = []
        outcomes_lock = threading.Lock()

        def worker(name):
            barrier.wait()
            try:
                service.complete_onboarding(user, name)
                result = "created"
            except service.AlreadyHasOrganisationError:
                result = "blocked"
            except Exception as exc:  # noqa: BLE001 - registar qualquer outro erro
                result = f"error:{type(exc).__name__}"
            finally:
                connections.close_all()
            with outcomes_lock:
                outcomes.append(result)

        threads = [
            threading.Thread(target=worker, args=(f"Empresa {i}",))
            for i in range(workers)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactamente uma empresa e uma Membership activa; nenhuma órfã.
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertEqual(
            Membership.objects.filter(user=user, is_active=True).count(), 1
        )
        # Uma tentativa cria, a outra é bloqueada de forma controlada.
        self.assertEqual(sorted(outcomes), ["blocked", "created"])
