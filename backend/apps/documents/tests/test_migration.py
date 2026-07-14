"""Teste da migração inicial do módulo documents (aplica e reverte).

Confirma que `documents.0001_initial` cria as tabelas `documents_document` e
`documents_documentversion` e que é reversível (voltar a `zero` remove as
tabelas sem afectar migrações históricas), reaplicando-a em seguida para deixar
a base de testes no estado corrente. Confirma também a ausência de drift
(`makemigrations --check`).
"""
from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

TABLES = ("documents_document", "documents_documentversion")


class DocumentsMigrationTests(TransactionTestCase):
    # As migrações já estão aplicadas na base de testes; usamos o executor para
    # reverter e reaplicar de forma controlada. Restauramos o esquema completo
    # antes/depois (o revert cascata para apps dependentes; independência de ordem).
    def setUp(self):
        call_command("migrate", verbosity=0)

    def tearDown(self):
        call_command("migrate", verbosity=0)

    def _tables_exist(self) -> bool:
        existing = set(connection.introspection.table_names())
        return all(table in existing for table in TABLES)

    def _migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.migrate(target)
        # Recarrega o estado do executor após a operação.
        executor.loader.build_graph()

    # 15a — migração aplica e é estruturalmente reversível
    def test_migration_applies_and_reverts(self):
        # Estado inicial: aplicada.
        self.assertTrue(self._tables_exist())

        # Reverter o módulo documents para "zero" — remove as tabelas.
        self._migrate([("documents", None)])
        self.assertFalse(self._tables_exist())

        # Reaplicar a migração inicial — recria as tabelas.
        self._migrate([("documents", "0001_initial")])
        self.assertTrue(self._tables_exist())

    # 15b — sem drift entre modelos e migrações
    def test_no_migration_drift(self):
        out = StringIO()
        # Lança SystemExit(1) se houver alterações de modelo sem migração.
        call_command(
            "makemigrations", "--check", "--dry-run", stdout=out, stderr=out
        )
