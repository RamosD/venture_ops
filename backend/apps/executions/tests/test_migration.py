"""Teste da migração inicial do módulo executions (aplica, reverte, sem drift)."""
from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

TABLES = (
    "executions_aiexecution",
    "executions_executioncontextdocument",
    "executions_resultattempt",
)


class ExecutionsMigrationTests(TransactionTestCase):
    def setUp(self):
        call_command("migrate", verbosity=0)

    def tearDown(self):
        call_command("migrate", verbosity=0)

    def _tables_exist(self) -> bool:
        names = connection.introspection.table_names()
        return all(t in names for t in TABLES)

    def _migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.migrate(target)
        executor.loader.build_graph()

    def test_migration_applies_and_reverts(self):
        self.assertTrue(self._tables_exist())
        # Reverte todas as migrações do módulo (remove as três tabelas).
        self._migrate([("executions", None)])
        names = connection.introspection.table_names()
        self.assertFalse(any(t in names for t in TABLES))
        # Reaplica na íntegra (0001 + 0002) e confirma as três tabelas.
        call_command("migrate", "executions", verbosity=0)
        self.assertTrue(self._tables_exist())

    def test_no_migration_drift(self):
        out = StringIO()
        call_command("makemigrations", "--check", "--dry-run", stdout=out, stderr=out)
