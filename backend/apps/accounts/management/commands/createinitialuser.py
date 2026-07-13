"""Criação controlada da conta inicial (sem registo público).

A palavra-passe **nunca** é aceite por argumento CLI (evita exposição no
histórico da shell ou na lista de processos):
- modo interactivo (por defeito): pede a palavra-passe por entrada oculta, com
  confirmação;
- modo `--noinput`: lê a variável de ambiente `INITIAL_USER_PASSWORD`.

A palavra-passe é validada pelos validadores do Django e nunca é impressa nem
registada. Idempotente: uma conta já existente não é alterada.
"""
from __future__ import annotations

import getpass
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.normalization import normalize_email


class Command(BaseCommand):
    help = "Cria a conta inicial de forma controlada (sem registo público)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--name", default="")
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            dest="noinput",
            help="Lê a palavra-passe de INITIAL_USER_PASSWORD (automação controlada).",
        )

    def handle(self, *args, **options):
        user_model = get_user_model()
        email = normalize_email(options["email"])
        if not email:
            raise CommandError("Indique um email válido em --email.")

        if user_model.objects.filter(email__iexact=email).exists():
            # Idempotência segura: não altera a conta existente.
            self.stdout.write(
                self.style.WARNING(f"Conta já existente ({email}); não alterada.")
            )
            return

        password = self._obtain_password(options["noinput"])
        try:
            validate_password(password)
        except ValidationError as exc:
            raise CommandError("Palavra-passe fraca: " + " ".join(exc.messages))

        user_model.objects.create_user(
            email=email, password=password, name=options["name"]
        )
        self.stdout.write(self.style.SUCCESS(f"Conta inicial criada: {email}"))

    def _obtain_password(self, noinput: bool) -> str:
        if noinput:
            password = os.environ.get("INITIAL_USER_PASSWORD")
            if not password:
                raise CommandError(
                    "Modo --noinput: defina a variável de ambiente "
                    "INITIAL_USER_PASSWORD."
                )
            return password

        password = getpass.getpass("Palavra-passe: ")
        confirmation = getpass.getpass("Confirme a palavra-passe: ")
        if password != confirmation:
            raise CommandError("As palavras-passe não coincidem.")
        if not password:
            raise CommandError("A palavra-passe não pode ser vazia.")
        return password
