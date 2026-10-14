from django.core.management.base import BaseCommand

from medowa_app.credentials import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    TEST_PASSWORD,
    TEST_USERNAME,
    ensure_accounts,
)


class Command(BaseCommand):
    help = 'Creates or refreshes the standard admin and test user accounts'

    def handle(self, *args, **options):
        admin_user, test_user = ensure_accounts()
        self.stdout.write(self.style.SUCCESS(
            'Ready: %s (superuser) and %s (customer) accounts are provisioned' % (
                admin_user.username, test_user.username
            )
        ))
        self.stdout.write('Admin credentials: %s / %s' % (ADMIN_USERNAME, ADMIN_PASSWORD))
        self.stdout.write('Test credentials: %s / %s' % (TEST_USERNAME, TEST_PASSWORD))
