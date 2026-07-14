"""Teste da migração inicial do módulo work_items (aplica, reverte, sem drift)."""
from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

TABLE = "work_items_workitem"


class WorkItemsMigrationTests(TransactionTestCase):
    # Restaura o esquema completo antes/depois (o revert cascata para apps
    # dependentes; independência de ordem entre TransactionTestCase).
    def setUp(self):
        call_command("migrate", verbosity=0)

    def tearDown(self):
        call_command("migrate", verbosity=0)

    def _table_exists(self) -> bool:
        return TABLE in connection.introspection.table_names()

    def _migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.migrate(target)
        executor.loader.build_graph()

    def test_migration_applies_and_reverts(self):
        self.assertTrue(self._table_exists())
        self._migrate([("work_items", None)])
        self.assertFalse(self._table_exists())
        self._migrate([("work_items", "0001_initial")])
        self.assertTrue(self._table_exists())

    def test_no_migration_drift(self):
        out = StringIO()
        call_command("makemigrations", "--check", "--dry-run", stdout=out, stderr=out)
