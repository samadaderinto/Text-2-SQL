"""
Create a production admin user from environment variables.

Designed for non-technical app owners: set a handful of env vars and the
command idempotently ensures the admin account exists with the right
credentials.  The same env vars feed Grafana's admin so there is one
source of truth.

Usage
-----
    python manage.py create_prod_admin          # reads from env
    python manage.py create_prod_admin --check  # exit 0 if exists, 1 if not
"""

import logging
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from app.models import User

logger = logging.getLogger(__name__)

# ── env var names (shared with Grafana via GF_SECURITY_ADMIN_*) ──────────
ENV_EMAIL = "ADMIN_EMAIL"
ENV_PASSWORD = "ADMIN_PASSWORD"
ENV_FIRST_NAME = "ADMIN_FIRST_NAME"
ENV_LAST_NAME = "ADMIN_LAST_NAME"


def _env(name: str, default: str = "") -> str:
    import os

    return os.getenv(name, default).strip()


class Command(BaseCommand):
    help = (
        "Create (or update) the production admin (superuser) from env vars. "
        "The same credentials are shared with Grafana."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Only check whether the admin account exists (exit code 0/1).",
        )
        parser.add_argument(
            "--email",
            help=f"Override ${ENV_EMAIL} env var.",
        )
        parser.add_argument(
            "--password",
            help=f"Override ${ENV_PASSWORD} env var.",
        )

    def handle(self, *args, **options):
        email = (options.get("email") or _env(ENV_EMAIL)).lower()
        password = options.get("password") or _env(ENV_PASSWORD)
        first_name = _env(ENV_FIRST_NAME, "Admin")
        last_name = _env(ENV_LAST_NAME, "")

        if options["check"]:
            return self._check(email)

        if not email:
            raise CommandError(
                f"Set ${ENV_EMAIL} (or pass --email) to create the admin."
            )
        if not password:
            raise CommandError(
                f"Set ${ENV_PASSWORD} (or pass --password) to create the admin."
            )

        user, created = self._get_or_create(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Admin created: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Admin updated: {email}"))

        logger.info(
            "prod_admin_ensured",
            extra={"email": email, "created": created},
        )

    # ── helpers ──────────────────────────────────────────────────────────

    def _check(self, email: str):
        if not email:
            raise CommandError(f"Set ${ENV_EMAIL} to use --check.")
        exists = User.objects.filter(email=email, is_staff=True).exists()
        if exists:
            self.stdout.write(self.style.SUCCESS(f"Admin exists: {email}"))
        else:
            self.stdout.write(self.style.WARNING(f"Admin missing: {email}"))
            sys.exit(1)

    def _get_or_create(self, *, email, password, first_name, last_name):
        """Idempotently ensure the admin account exists and is up-to-date."""
        defaults = {
            "first_name": first_name,
            "last_name": last_name,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        }
        try:
            user, created = User.objects.get_or_create(
                email=email,
                defaults=defaults,
            )
        except IntegrityError:
            # Race condition: another process created it first.
            user = User.objects.get(email=email)
            created = False

        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        else:
            # Update mutable fields so re-running the command applies changes.
            changed_fields = []
            for field, value in defaults.items():
                if getattr(user, field) != value:
                    setattr(user, field, value)
                    changed_fields.append(field)

            # Always reset the password to match the env var.
            user.set_password(password)
            changed_fields.append("password")

            if changed_fields:
                user.save(update_fields=changed_fields)

        return user, created
