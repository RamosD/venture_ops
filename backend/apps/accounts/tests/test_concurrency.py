"""Concorrência real do rate limiting sobre PostgreSQL (Parte D)."""
import threading

from django.db import connections
from django.test import TransactionTestCase

from apps.accounts import rate_limit
from apps.accounts.models import RateLimitAttempt


class RateLimitConcurrencyTests(TransactionTestCase):
    def _run_concurrent_allow(self, key, limit, window, workers):
        barrier = threading.Barrier(workers)
        results = []
        results_lock = threading.Lock()

        def worker():
            barrier.wait()  # sincroniza o disparo (sem sleeps)
            try:
                allowed = rate_limit.allow(key, limit, window)
                with results_lock:
                    results.append(allowed)
            finally:
                connections.close_all()

        threads = [threading.Thread(target=worker) for _ in range(workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return results

    def test_limit_not_exceeded_under_concurrency(self):
        key = rate_limit.make_key("login", "conc@x.pt")
        limit, window, workers = 5, 300, 20

        results = self._run_concurrent_allow(key, limit, window, workers)

        # Exactamente `limit` pedidos permitidos, apesar da corrida.
        self.assertEqual(sum(1 for r in results if r), limit)
        self.assertEqual(RateLimitAttempt.objects.filter(key=key).count(), limit)

    def test_requests_after_limit_are_blocked(self):
        key = rate_limit.make_key("login", "conc2@x.pt")
        limit, window = 5, 300
        self._run_concurrent_allow(key, limit, window, 20)
        # Pedidos subsequentes continuam bloqueados.
        self.assertFalse(rate_limit.allow(key, limit, window))
