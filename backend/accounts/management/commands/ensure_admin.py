import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Ensure an initial superuser exists."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        display_name = os.getenv("DJANGO_SUPERUSER_DISPLAY_NAME", "Admin")

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Superuser already exists; skipped.")
            return

        if not password:
            self.stdout.write(self.style.WARNING("DJANGO_SUPERUSER_PASSWORD is not set; skipped."))
            return

        User.objects.create_superuser(
            username=username,
            password=password,
            display_name=display_name,
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser: {username}"))
