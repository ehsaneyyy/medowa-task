from django.contrib.auth import authenticate, get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.test import Client, override_settings
from django.urls import reverse

from medowa_app.credentials import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    TEST_PASSWORD,
    TEST_USERNAME,
    ensure_accounts,
)

PROFILE_EXPECTATIONS = ['Account details', 'Member for', 'Date joined', 'Session expiry']


class Command(BaseCommand):
    help = 'Verifies the standard credentials against the login, profile, and admin routes'

    def handle(self, *args, **options):
        ensure_accounts()
        failures = []
        checks = []

        dashboard_url = reverse('dashboard_home')
        checks.append(('dashboard route resolves to /dashboard/', dashboard_url == '/dashboard/', dashboard_url))

        admin_account = authenticate(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        checks.append((
            'admin credentials authenticate as superuser',
            bool(admin_account and admin_account.is_superuser and admin_account.is_staff),
            ADMIN_USERNAME,
        ))

        test_account = authenticate(username=TEST_USERNAME, password=TEST_PASSWORD)
        checks.append((
            'test credentials authenticate as customer',
            bool(test_account and not test_account.is_superuser),
            TEST_USERNAME,
        ))

        bad_account = authenticate(username=TEST_USERNAME, password='definitely-wrong')
        checks.append(('invalid password is rejected', bad_account is None, TEST_USERNAME))

        with override_settings(ALLOWED_HOSTS=['testserver', 'localhost']):
            client = Client()
            login_response = client.post(
                reverse('login'),
                {'username': TEST_USERNAME, 'password': TEST_PASSWORD},
            )
            checks.append((
                'test user login redirects to the storefront',
                login_response.status_code == 302 and login_response['Location'] == reverse('index'),
                '%s -> %s' % (login_response.status_code, login_response.get('Location', '')),
            ))

            profile_response = client.get(reverse('profile'))
            body = profile_response.content.decode('utf-8')
            checks.append((
                'profile dashboard renders for the authenticated session',
                profile_response.status_code == 200,
                'HTTP %s' % profile_response.status_code,
            ))

            for label in PROFILE_EXPECTATIONS:
                checks.append((
                    'profile dashboard shows "%s"' % label,
                    label in body,
                    TEST_USERNAME,
                ))

            stats_present = body.count('Member for') == 1 and body.count('Store products') == 1
            checks.append(('profile dashboard shows database account stats', stats_present, TEST_USERNAME))

            admin_client = Client()
            admin_client.post(
                reverse('login'),
                {'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD},
            )
            admin_response = admin_client.get(dashboard_url)
            checks.append((
                'admin account opens the custom dashboard',
                admin_response.status_code == 200,
                'HTTP %s' % admin_response.status_code,
            ))

            bad_client = Client()
            bad_client.post(reverse('login'), {'username': TEST_USERNAME, 'password': 'definitely-wrong'})
            blocked = bad_client.get(reverse('profile'))
            checks.append((
                'profile dashboard blocks unauthenticated sessions',
                blocked.status_code == 302 and reverse('login') in blocked['Location'],
                'HTTP %s' % blocked.status_code,
            ))

        for description, passed, detail in checks:
            if passed:
                self.stdout.write(self.style.SUCCESS('[PASS] %s (%s)' % (description, detail)))
            else:
                failures.append(description)
                self.stdout.write(self.style.ERROR('[FAIL] %s (%s)' % (description, detail)))

        accounts = get_user_model().objects.filter(username__in=[ADMIN_USERNAME, TEST_USERNAME]).count()
        self.stdout.write('Verified accounts present in database: %d' % accounts)

        if failures:
            raise CommandError('Credential verification failed: %s' % '; '.join(failures))

        self.stdout.write(self.style.SUCCESS('All credential verification checks passed'))
