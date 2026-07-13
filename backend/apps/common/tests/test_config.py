"""Testes da validação de configuração obrigatória por ambiente."""
import os
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.env import get_bool, get_env, get_list


class ConfigValidationTests(SimpleTestCase):
    def test_missing_required_variable_raises_clear_error(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                get_env("VO_REQUIRED_VAR_TEST")
        # A mensagem identifica a variável em falta (clara e accionável).
        self.assertIn("VO_REQUIRED_VAR_TEST", str(ctx.exception))

    def test_default_is_used_when_variable_absent(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_env("VO_ABSENT", default="fallback"), "fallback")

    def test_get_bool_parses_truthy_values(self):
        with mock.patch.dict(os.environ, {"VO_FLAG": "true"}, clear=True):
            self.assertTrue(get_bool("VO_FLAG"))
        with mock.patch.dict(os.environ, {"VO_FLAG": "0"}, clear=True):
            self.assertFalse(get_bool("VO_FLAG"))

    def test_get_list_splits_and_trims(self):
        with mock.patch.dict(os.environ, {"VO_LIST": "a, b ,c"}, clear=True):
            self.assertEqual(get_list("VO_LIST"), ["a", "b", "c"])
