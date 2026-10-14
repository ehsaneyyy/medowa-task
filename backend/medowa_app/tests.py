from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .credentials import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    TEST_PASSWORD,
    TEST_USERNAME,
    ensure_accounts,
)
from .models import Banner, Category, Product


class StoreFixturesMixin:

    @classmethod
    def setUpTestData(cls):
        cls.mac = Category.objects.create(name='Mac', slug='mac')
        cls.iphone = Category.objects.create(name='iPhone', slug='iphone')
        cls.macbook = Product.objects.create(
            name='MacBook Air 13-inch M4',
            description='Fanless M4 performance in Sky Blue.',
            price=Decimal('99900.00'),
            image='https://example.com/macbook.jpg',
            category=cls.mac,
            is_active=True,
        )
        cls.hidden_product = Product.objects.create(
            name='Discontinued Mac',
            description='Retired inventory.',
            price=Decimal('1000.00'),
            image='https://example.com/retired.jpg',
            category=cls.mac,
            is_active=False,
        )
        cls.iphone_product = Product.objects.create(
            name='iPhone 18 Pro',
            description='Titanium. So Pro.',
            price=Decimal('134900.00'),
            image='https://example.com/iphone.jpg',
            category=cls.iphone,
            is_active=True,
        )
        cls.banner = Banner.objects.create(
            title='iPhone 18 Pro',
            subtitle='Titanium. So strong. So light. So Pro.',
            image='https://example.com/banner.jpg',
            link_url='/?category=iphone',
            is_active=True,
        )
        cls.hidden_banner = Banner.objects.create(
            title='Archive banner',
            subtitle='Not live.',
            image='https://example.com/archive.jpg',
            link_url='/',
            is_active=False,
        )


class IndexViewTests(StoreFixturesMixin, TestCase):

    def test_index_renders_active_content(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertEqual(len(response.context['banners']), 1)
        self.assertEqual(response.context['products'].count(), 2)
        self.assertEqual(response.context['category_count'], 2)
        self.assertContains(response, 'iPhone 18 Pro')

    def test_index_filters_by_category(self):
        response = self.client.get(reverse('index'), {'category': 'mac'})
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.macbook)
        self.assertEqual(response.context['active_category'], 'mac')

    def test_index_ignores_unknown_category(self):
        response = self.client.get(reverse('index'), {'category': 'airpods'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products'].count(), 2)
        self.assertEqual(response.context['active_category'], '')


class ProductDetailViewTests(StoreFixturesMixin, TestCase):

    def test_detail_renders_product(self):
        response = self.client.get(reverse('product_detail', args=[self.macbook.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')
        self.assertEqual(response.context['product'], self.macbook)
        self.assertContains(response, '99,900')

    def test_detail_hides_inactive_products(self):
        response = self.client.get(reverse('product_detail', args=[self.hidden_product.pk]))
        self.assertEqual(response.status_code, 404)

    def test_detail_unknown_pk_returns_404(self):
        response = self.client.get(reverse('product_detail', args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_shows_related_products(self):
        response = self.client.get(reverse('product_detail', args=[self.macbook.pk]))
        self.assertEqual(list(response.context['related_products']), [])


class AuthFlowTests(StoreFixturesMixin, TestCase):

    def test_register_creates_and_authenticates_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'applefan',
            'email': 'fan@example.com',
            'password1': 'S3cureStorePass!',
            'password2': 'S3cureStorePass!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='applefan').exists())
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertContains(response, 'Welcome to Core Store')

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user('existing', 'used@example.com', 'pass12345A!')
        response = self.client.post(reverse('register'), {
            'username': 'newfan',
            'email': 'used@example.com',
            'password1': 'S3cureStorePass!',
            'password2': 'S3cureStorePass!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email already exists.')

    def test_login_and_profile_round_trip(self):
        User.objects.create_user('applefan', 'fan@example.com', 'S3cureStorePass!')
        response = self.client.post(reverse('login'), {
            'username': 'applefan',
            'password': 'S3cureStorePass!',
        })
        self.assertRedirects(response, reverse('index'))
        profile = self.client.get(reverse('profile'))
        self.assertEqual(profile.status_code, 200)
        self.assertTemplateUsed(profile, 'profile.html')
        self.assertContains(profile, 'applefan')
        self.assertContains(profile, 'Last login')

    def test_login_rejects_bad_credentials(self):
        User.objects.create_user('applefan', 'fan@example.com', 'S3cureStorePass!')
        response = self.client.post(reverse('login'), {
            'username': 'applefan',
            'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertFormError(response.context['form'], None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_logout_is_post_only_and_clears_session(self):
        User.objects.create_user('applefan', 'fan@example.com', 'S3cureStorePass!')
        self.client.login(username='applefan', password='S3cureStorePass!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '%s?next=%s' % (reverse('login'), reverse('profile')))


class SeedCommandTests(TestCase):

    def test_seed_store_is_idempotent(self):
        call_command('seed_store')
        call_command('seed_store')
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(Banner.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 12)
        self.assertEqual(
            set(Category.objects.values_list('slug', flat=True)),
            {'mac', 'iphone', 'ipad', 'watch'},
        )
        self.assertTrue(Product.objects.filter(is_active=True).count(), 12)


class UrlRoutingTests(StoreFixturesMixin, TestCase):

    def test_all_routes_resolve(self):
        self.assertEqual(reverse('index'), '/')
        self.assertEqual(reverse('product_detail', args=[1]), '/product/1/')
        self.assertEqual(reverse('register'), '/register/')
        self.assertEqual(reverse('login'), '/login/')
        self.assertEqual(reverse('logout'), '/logout/')
        self.assertEqual(reverse('profile'), '/profile/')

    def test_csrf_token_present_in_custom_forms(self):
        for name in ('register', 'login'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'csrfmiddlewaretoken')


class BrandingTests(StoreFixturesMixin, TestCase):

    def test_storefront_pages_use_core_store_branding(self):
        for name, args in (('index', []), ('register', []), ('login', [])):
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Core Store')

    def test_storefront_pages_drop_legacy_branding(self):
        for name, args in (('index', []), ('register', []), ('login', [])):
            response = self.client.get(reverse(name, args=args))
            self.assertNotContains(response, 'Medowa')

    def test_product_detail_uses_core_store_reference_prefix(self):
        response = self.client.get(reverse('product_detail', args=[self.macbook.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CS-')
        self.assertNotContains(response, 'MDW-')


class CredentialVerificationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_user, cls.test_user = ensure_accounts()

    def test_admin_route_resolves_to_admin_path(self):
        self.assertEqual(reverse('admin:index'), '/admin/')

    def test_admin_account_has_superuser_privileges(self):
        self.assertEqual(self.admin_user.username, ADMIN_USERNAME)
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.check_password(ADMIN_PASSWORD))

    def test_test_account_is_a_customer(self):
        self.assertEqual(self.test_user.username, TEST_USERNAME)
        self.assertFalse(self.test_user.is_staff)
        self.assertFalse(self.test_user.is_superuser)
        self.assertTrue(self.test_user.check_password(TEST_PASSWORD))

    def test_admin_user_can_reach_admin_console(self):
        self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_test_user_login_renders_profile_dashboard_with_stats(self):
        response = self.client.post(reverse('login'), {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD,
        })
        self.assertRedirects(response, reverse('index'))
        profile = self.client.get(reverse('profile'))
        self.assertEqual(profile.status_code, 200)
        self.assertTemplateUsed(profile, 'profile.html')
        self.assertContains(profile, TEST_USERNAME)
        for expected in ('Account details', 'Member for', 'Date joined', 'Store products', 'Session expiry'):
            self.assertContains(profile, expected)

    def test_wrong_password_is_rejected_for_test_user(self):
        response = self.client.post(reverse('login'), {
            'username': TEST_USERNAME,
            'password': 'definitely-wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_ensure_accounts_command_is_idempotent(self):
        call_command('ensure_accounts')
        call_command('ensure_accounts')
        self.assertEqual(User.objects.filter(username=ADMIN_USERNAME).count(), 1)
        self.assertEqual(User.objects.filter(username=TEST_USERNAME).count(), 1)

    def test_verify_accounts_command_passes(self):
        call_command('verify_accounts')
