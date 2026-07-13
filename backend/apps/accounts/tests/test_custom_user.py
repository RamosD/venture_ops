"""Testes estruturais do modelo de utilizador próprio."""
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import SimpleTestCase, TestCase


class AuthUserModelConfigTests(SimpleTestCase):
    def test_auth_user_model_points_to_custom_user(self):
        self.assertEqual(settings.AUTH_USER_MODEL, "accounts.CustomUser")

    def test_username_field_is_email(self):
        self.assertEqual(get_user_model().USERNAME_FIELD, "email")


class CustomUserTests(TestCase):
    def test_create_user_with_email(self):
        user = get_user_model().objects.create_user(email="a@x.pt", password="pw-123")
        self.assertEqual(user.email, "a@x.pt")
        self.assertTrue(user.check_password("pw-123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_primary_key_is_uuid(self):
        user = get_user_model().objects.create_user(email="b@x.pt", password="pw")
        self.assertIsInstance(user.pk, uuid.UUID)

    def test_email_is_unique(self):
        get_user_model().objects.create_user(email="dup@x.pt", password="pw")
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(email="dup@x.pt", password="pw2")

    def test_email_required(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="pw")
