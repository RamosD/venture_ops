"""Testes do comando de criação controlada da conta inicial (Parte B)."""
import os
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.accounts.management.commands.createinitialuser import Command

STRONG = "V3ntureOps-Forte-2026"


class CreateInitialUserTests(TestCase):
    def test_help_has_no_password_option(self):
        parser = Command().create_parser("manage.py", "createinitialuser")
        options = [
            opt for action in parser._actions for opt in action.option_strings
        ]
        self.assertNotIn("--password", options)

    @mock.patch("getpass.getpass")
    def test_interactive_uses_hidden_input_with_confirmation(self, getpass_mock):
        getpass_mock.side_effect = [STRONG, STRONG]
        out = StringIO()
        call_command("createinitialuser", email="fundador@x.pt", stdout=out)
        self.assertEqual(getpass_mock.call_count, 2)  # entrada + confirmação
        self.assertTrue(
            get_user_model().objects.filter(email="fundador@x.pt").exists()
        )
        self.assertNotIn(STRONG, out.getvalue())  # nunca imprime a palavra-passe

    @mock.patch("getpass.getpass")
    def test_mismatched_confirmation_is_rejected(self, getpass_mock):
        getpass_mock.side_effect = [STRONG, "outra-coisa-diferente"]
        with self.assertRaises(CommandError):
            call_command("createinitialuser", email="fundador@x.pt", stdout=StringIO())
        self.assertFalse(
            get_user_model().objects.filter(email="fundador@x.pt").exists()
        )

    def test_noinput_without_env_fails_clearly(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CommandError):
                call_command(
                    "createinitialuser",
                    email="fundador@x.pt",
                    noinput=True,
                    stdout=StringIO(),
                )

    def test_noinput_with_env_creates_account(self):
        with mock.patch.dict(os.environ, {"INITIAL_USER_PASSWORD": STRONG}):
            call_command(
                "createinitialuser",
                email="fundador@x.pt",
                noinput=True,
                stdout=StringIO(),
            )
        self.assertTrue(
            get_user_model().objects.filter(email="fundador@x.pt").exists()
        )

    def test_weak_password_is_rejected_by_validators(self):
        with mock.patch.dict(os.environ, {"INITIAL_USER_PASSWORD": "12345678"}):
            with self.assertRaises(CommandError):
                call_command(
                    "createinitialuser",
                    email="fundador@x.pt",
                    noinput=True,
                    stdout=StringIO(),
                )

    def test_existing_account_is_not_changed(self):
        user = get_user_model().objects.create_user(
            email="fundador@x.pt", password="original-forte-2026"
        )
        with mock.patch.dict(os.environ, {"INITIAL_USER_PASSWORD": STRONG}):
            call_command(
                "createinitialuser",
                email="FUNDADOR@x.pt",  # mesmo email (case-insensitive)
                noinput=True,
                stdout=StringIO(),
            )
        user.refresh_from_db()
        self.assertTrue(user.check_password("original-forte-2026"))
        self.assertEqual(get_user_model().objects.count(), 1)
