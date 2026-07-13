"""Criação controlada da conta inicial (sem registo público).

Executado por um operador com acesso ao ambiente. A palavra-passe é indicada por
`--password` ou pela variável `INITIAL_USER_PASSWORD` (nunca fica em código).
"""
from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria a conta inicial de forma controlada (sem registo público)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", default=None)
        parser.add_argument("--name", default="")

    def handle(self, *args, **options):
        user_model = get_user_model()
        email = options["email"].strip().lower()
        password = options["password"] or os.environ.get("INITIAL_USER_PASSWORD")
        if not password:
            raise CommandError(
                "Indique --password ou a variável de ambiente INITIAL_USER_PASSWORD."
            )
        if user_model.objects.filter(email__iexact=email).exists():
            raise CommandError(f"Já existe um utilizador com o email {email}.")
        user_model.objects.create_user(
            email=email, password=password, name=options["name"]
        )
        self.stdout.write(self.style.SUCCESS(f"Conta inicial criada: {email}"))
