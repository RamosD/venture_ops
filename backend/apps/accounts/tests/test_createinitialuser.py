"""Testes do comando de criação controlada da conta inicial."""
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class CreateInitialUserTests(TestCase):
    def test_creates_initial_account(self):
        call_command(
            "createinitialuser",
            email="fundador@x.pt",
            password="uma-pw-forte-123",
            stdout=StringIO(),
        )
        user = get_user_model().objects.get(email="fundador@x.pt")
        self.assertTrue(user.check_password("uma-pw-forte-123"))

    def test_requires_password(self):
        with self.assertRaises(CommandError):
            call_command("createinitialuser", email="fundador@x.pt", stdout=StringIO())

    def test_rejects_duplicate_email(self):
        call_command(
            "createinitialuser",
            email="fundador@x.pt",
            password="uma-pw-forte-123",
            stdout=StringIO(),
        )
        with self.assertRaises(CommandError):
            call_command(
                "createinitialuser",
                email="fundador@x.pt",
                password="outra-pw-123",
                stdout=StringIO(),
            )
