"""Limpeza dos registos de rate limiting anteriores ao limite de retenção.

Operacional e idempotente. Não introduz scheduler — a execução periódica será
configurada no ambiente do piloto (por exemplo, cron). Mostra apenas contagens e
datas; nunca chaves/hashes ou dados sensíveis.
"""
from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.accounts import rate_limit


class Command(BaseCommand):
    help = "Remove registos de rate limiting anteriores ao limite de retenção."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas conta; não remove nada.",
        )

    def handle(self, *args, **options):
        retention = int(settings.RATE_LIMIT_RETENTION_SECONDS)
        max_window = rate_limit.max_active_window_seconds()
        if retention <= max_window:
            raise CommandError(
                "Configuração inválida: RATE_LIMIT_RETENTION_SECONDS "
                f"({retention}s) tem de ser superior à maior janela activa "
                f"({max_window}s) para não afectar janelas em curso."
            )

        dry_run = options["dry_run"]
        count, oldest, newest = rate_limit.purge_expired(retention, dry_run=dry_run)

        prefix = "[dry-run] " if dry_run else ""
        if count == 0:
            self.stdout.write(f"{prefix}Nenhum registo expirado (retenção {retention}s).")
            return
        self.stdout.write(
            f"{prefix}{'A remover' if not dry_run else 'A remover (simulado)'} "
            f"{count} registo(s) anteriores a {retention}s; "
            f"mais antigo: {oldest}; mais recente abrangido: {newest}."
        )
