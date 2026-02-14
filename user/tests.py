from django.db import IntegrityError
from django.test import TestCase

from django.contrib.auth import get_user_model


class UserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="user@user.com",
            password="user123",
        )

        self.assertEqual(user.email, "user@user.com")
        self.assertTrue(user.check_password("user123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            email="admin@admin.com",
            password="admin123",
        )

        self.assertEqual(user.email, "admin@admin.com")
        self.assertTrue(user.check_password("admin123"))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_email(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="password123")

    def test_email_unique(self):
        User = get_user_model()
        User.objects.create_user("user1@user.com", "password")

        with self.assertRaises(IntegrityError):
            User.objects.create_user("user1@user.com", "password123")
