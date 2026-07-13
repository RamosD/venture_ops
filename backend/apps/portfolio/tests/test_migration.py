"""Teste da migração inicial do módulo portfolio (aplica e reverte).

Confirma que `portfolio.0001_initial` cria a tabela `portfolio_product` e que é
reversível (voltar a `zero` remove a tabela sem afectar migrações históricas),
reaplicando-a em seguida para deixar a base de testes no estado corrente.
"""
from __future__ import annotations

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class PortfolioMigrationTests(TransactionTestCase):
    # A migração já está aplicada na base de testes; usamos o executor para
    # reverter e reaplicar de forma controlada.
    def _table_exists(self) -> bool:
        return "portfolio_product" in connection.introspection.table_names()

    def _migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.migrate(target)
        # Recarrega o estado do executor após a operação.
        executor.loader.build_graph()

    def test_migration_applies_and_reverts(self):
        # Estado inicial: aplicada.
        self.assertTrue(self._table_exists())

        # Reverter o módulo portfolio para "zero" — remove a tabela.
        self._migrate([("portfolio", None)])
        self.assertFalse(self._table_exists())

        # Reaplicar a migração inicial — recria a tabela.
        self._migrate([("portfolio", "0001_initial")])
        self.assertTrue(self._table_exists())
