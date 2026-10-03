from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from app.models import User


@pytest.mark.django_db
def test_create_prod_admin_creates_real_django_admin():
    env = {
        "ADMIN_EMAIL": "owner@example.com",
        "ADMIN_PASSWORD": "A-strong-shared-password-123!",
        "ADMIN_FIRST_NAME": "Site",
        "ADMIN_LAST_NAME": "Owner",
    }

    with patch.dict("os.environ", env, clear=True):
        call_command("create_prod_admin", stdout=StringIO())

    user = User.objects.get(email="owner@example.com")
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password(env["ADMIN_PASSWORD"])


@pytest.mark.django_db
def test_create_prod_admin_updates_flags_and_password_idempotently():
    user = User.objects.create_user(
        email="owner@example.com",
        password="old-password",
        is_active=False,
        is_staff=False,
        is_superuser=False,
    )
    env = {
        "ADMIN_EMAIL": user.email,
        "ADMIN_PASSWORD": "A-new-shared-password-123!",
    }

    with patch.dict("os.environ", env, clear=True):
        call_command("create_prod_admin", stdout=StringIO())

    user.refresh_from_db()
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password(env["ADMIN_PASSWORD"])


@pytest.mark.django_db
def test_create_prod_admin_supports_previous_grafana_variable_names():
    env = {
        "GF_SECURITY_ADMIN_USER": "legacy@example.com",
        "GF_SECURITY_ADMIN_PASSWORD": "A-legacy-password-123!",
    }

    with patch.dict("os.environ", env, clear=True):
        call_command("create_prod_admin", stdout=StringIO())

    user = User.objects.get(email="legacy@example.com")
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password(env["GF_SECURITY_ADMIN_PASSWORD"])
