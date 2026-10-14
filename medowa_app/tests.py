import io
import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .credentials import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    TEST_PASSWORD,
    TEST_USERNAME,
    ensure_accounts,
)
from .models import Banner, Category, Order, OrderItem, Product


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
        self.assertContains(response, 'Welcome to medowa-task')

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

    def test_storefront_pages_use_medowa_task_branding(self):
        for name, args in (('index', []), ('register', []), ('login', [])):
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'medowa-task')

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


class ApiEndpointTests(StoreFixturesMixin, TestCase):

    def test_products_endpoint_returns_active_products(self):
        response = self.client.get(reverse('api_products'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['count'], 2)
        names = {item['name'] for item in data['results']}
        self.assertEqual(names, {'MacBook Air 13-inch M4', 'iPhone 18 Pro'})

    def test_products_endpoint_filters_by_category(self):
        response = self.client.get(reverse('api_products'), {'category': 'mac'})
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], 'MacBook Air 13-inch M4')
        self.assertEqual(data['results'][0]['category']['slug'], 'mac')

    def test_product_detail_endpoint_returns_payload(self):
        response = self.client.get(reverse('api_product_detail', args=[self.macbook.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.macbook.pk)

    def test_categories_endpoint_reports_active_product_counts(self):
        response = self.client.get(reverse('api_categories'))
        data = response.json()
        self.assertEqual(data['count'], 2)
        by_slug = {item['slug']: item for item in data['results']}
        self.assertEqual(by_slug['mac']['product_count'], 1)
        self.assertEqual(by_slug['iphone']['product_count'], 1)

    def test_banners_endpoint_returns_only_active_banners(self):
        response = self.client.get(reverse('api_banners'))
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'iPhone 18 Pro')

    def test_api_allows_cross_origin_requests(self):
        response = self.client.get(reverse('api_products'), HTTP_ORIGIN='https://medowa-task.vercel.app')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')

    def test_api_routes_resolve(self):
        self.assertEqual(reverse('api_products'), '/api/products/')
        self.assertEqual(reverse('api_product_detail', args=[1]), '/api/products/1/')
        self.assertEqual(reverse('api_categories'), '/api/categories/')
        self.assertEqual(reverse('api_banners'), '/api/banners/')


class ProductImageUploadTests(StoreFixturesMixin, TestCase):

    def setUp(self):
        self.temp_media = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.temp_media, ignore_errors=True)

    def _png(self):
        buffer = io.BytesIO()
        Image.new('RGB', (2, 2), 'white').save(buffer, format='PNG')
        return buffer.getvalue()

    def test_image_url_falls_back_to_external_url(self):
        self.assertEqual(self.macbook.image_url, 'https://example.com/macbook.jpg')

    def test_uploaded_file_takes_precedence_over_url(self):
        self.macbook.image_file = SimpleUploadedFile(
            'macbook.png', self._png(), content_type='image/png'
        )
        self.macbook.save()
        self.macbook.refresh_from_db()
        self.assertIn('/media/products/', self.macbook.image_url)
        self.assertTrue(self.macbook.image_url.endswith('.png'))

    def test_api_serializes_uploaded_image_url(self):
        self.macbook.image_file = SimpleUploadedFile(
            'macbook.png', self._png(), content_type='image/png'
        )
        self.macbook.save()
        response = self.client.get(reverse('api_product_detail', args=[self.macbook.pk]))
        self.assertIn('/media/products/', response.json()['image'])


class CartAndCheckoutTests(StoreFixturesMixin, TestCase):

    def setUp(self):
        self.customer = User.objects.create_user('shopper', 'shopper@example.com', 'Sh0pSecure!')

    def test_cart_routes_resolve(self):
        self.assertEqual(reverse('cart'), '/cart/')
        self.assertEqual(reverse('add_to_cart', args=[1]), '/cart/add/1/')
        self.assertEqual(reverse('update_cart', args=[1]), '/cart/update/1/')
        self.assertEqual(reverse('remove_from_cart', args=[1]), '/cart/remove/1/')
        self.assertEqual(reverse('checkout'), '/checkout/')
        self.assertEqual(reverse('order_success', args=[1]), '/orders/1/')

    def test_add_to_cart_stores_item_in_session(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse('add_to_cart', args=[self.macbook.pk]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['cart'][str(self.macbook.pk)], 2)

    def test_anonymous_add_to_cart_redirects_to_login(self):
        response = self.client.post(reverse('add_to_cart', args=[self.macbook.pk]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        self.assertNotIn('cart', self.client.session)

    def test_add_to_cart_rejects_get(self):
        response = self.client.get(reverse('add_to_cart', args=[self.macbook.pk]))
        self.assertEqual(response.status_code, 405)

    def test_add_to_cart_hides_inactive_product(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse('add_to_cart', args=[self.hidden_product.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cart_page_lists_items_and_total(self):
        self.client.force_login(self.customer)
        self.client.post(reverse('add_to_cart', args=[self.macbook.pk]), {'quantity': 2})
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')
        self.assertContains(response, 'MacBook Air 13-inch M4')
        self.assertEqual(response.context['total'], Decimal('199800.00'))

    def test_update_and_remove_cart_item(self):
        self.client.force_login(self.customer)
        self.client.post(reverse('add_to_cart', args=[self.macbook.pk]))
        self.client.post(reverse('update_cart', args=[self.macbook.pk]), {'quantity': 3})
        self.assertEqual(self.client.session['cart'][str(self.macbook.pk)], 3)
        self.client.post(reverse('remove_from_cart', args=[self.macbook.pk]))
        self.assertNotIn(str(self.macbook.pk), self.client.session['cart'])

    def test_cart_update_returns_json_for_ajax(self):
        self.client.force_login(self.customer)
        self.client.post(reverse('add_to_cart', args=[self.macbook.pk]), {'quantity': 1})
        response = self.client.post(
            reverse('update_cart', args=[self.macbook.pk]),
            {'quantity': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['count'], 3)
        self.assertEqual(data['items'][str(self.macbook.pk)]['quantity'], 3)
        self.assertEqual(data['total_display'], '\u20b9299,700')

    def test_checkout_requires_login(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_checkout_redirects_when_bag_empty(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

    def test_checkout_creates_order_and_clears_bag(self):
        self.client.force_login(self.customer)
        self.client.post(reverse('add_to_cart', args=[self.macbook.pk]), {'quantity': 2})
        response = self.client.post(reverse('checkout'), {
            'full_name': 'Shopper One',
            'email': 'shopper@example.com',
            'address': '1 Infinite Loop',
            'city': 'Bengaluru',
            'postal_code': '560001',
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal('199800.00'))
        self.assertEqual(order.items.first().price, Decimal('99900.00'))
        self.assertEqual(self.client.session['cart'], {})
        self.assertEqual(order.reference, 'ORD-%05d' % order.pk)

    def test_order_success_is_scoped_to_owner(self):
        other = User.objects.create_user('intruder', 'intruder@example.com', 'N0tYours!')
        order = Order.objects.create(
            user=self.customer,
            full_name='Shopper One',
            email='shopper@example.com',
            address='Street',
            city='City',
            postal_code='560001',
            total=Decimal('1000.00'),
        )
        self.client.force_login(other)
        response = self.client.get(reverse('order_success', args=[order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_profile_lists_order_history(self):
        self.client.force_login(self.customer)
        Order.objects.create(
            user=self.customer,
            full_name='Shopper One',
            email='shopper@example.com',
            address='Street',
            city='City',
            postal_code='560001',
            total=Decimal('1000.00'),
        )
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'Order history')
        self.assertContains(response, Order.objects.first().reference)


class StaffAccountTests(StoreFixturesMixin, TestCase):

    def setUp(self):
        self.admin = User.objects.create_user('boss', 'boss@example.com', 'AdminPass!23', is_staff=True)

    def test_staff_add_to_cart_is_blocked(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('add_to_cart', args=[self.macbook.pk]), {'quantity': 1})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('cart', self.client.session)

    def test_staff_checkout_is_blocked(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('index'))

    def test_staff_homepage_shows_admin_notice(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'admin account')

    def test_anonymous_homepage_prompts_sign_in(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Sign in to buy')


class DashboardTests(StoreFixturesMixin, TestCase):

    def setUp(self):
        self.admin = User.objects.create_user('boss', 'boss@example.com', 'AdminPass!23', is_staff=True)
        self.customer = User.objects.create_user('shopper', 'shopper@example.com', 'Sh0pSecure!')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_dashboard_blocks_customers(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('dashboard_home'))
        self.assertRedirects(response, reverse('index'))

    def test_staff_can_open_every_dashboard_section(self):
        self.client.force_login(self.admin)
        for name in (
            'dashboard_home',
            'dashboard_products',
            'dashboard_categories',
            'dashboard_banners',
            'dashboard_orders',
            'dashboard_users',
        ):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_product_create_edit_toggle_delete(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('dashboard_product_create'), {
            'name': 'iPad Air M3',
            'category': self.mac.pk,
            'price': '69900.00',
            'description': 'Thin and fast.',
            'image': 'https://example.com/ipad.jpg',
            'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name='iPad Air M3')
        self.assertEqual(product.category, self.mac)

        self.client.post(reverse('dashboard_product_toggle', args=[product.pk]))
        product.refresh_from_db()
        self.assertFalse(product.is_active)

        self.client.post(reverse('dashboard_product_edit', args=[product.pk]), {
            'name': 'iPad Air M3',
            'category': self.mac.pk,
            'price': '74900.00',
            'description': 'Thin and fast.',
            'image': 'https://example.com/ipad.jpg',
            'is_active': 'on',
        })
        product.refresh_from_db()
        self.assertEqual(product.price, Decimal('74900.00'))

        self.client.post(reverse('dashboard_product_delete', args=[product.pk]))
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_category_and_banner_lifecycle(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('dashboard_category_create'), {'name': 'AirPods', 'slug': 'airpods'})
        self.assertTrue(Category.objects.filter(slug='airpods').exists())
        self.client.post(reverse('dashboard_banner_create'), {
            'title': 'Summer',
            'subtitle': 'Hot deals',
            'link_url': '/',
            'image': 'https://example.com/summer.jpg',
            'is_active': 'on',
        })
        banner = Banner.objects.get(title='Summer')
        self.client.post(reverse('dashboard_banner_toggle', args=[banner.pk]))
        banner.refresh_from_db()
        self.assertFalse(banner.is_active)

    def test_order_status_update(self):
        self.client.force_login(self.admin)
        order = Order.objects.create(
            user=self.customer,
            full_name='Shopper',
            email='s@example.com',
            address='Street',
            city='City',
            postal_code='560001',
            total=Decimal('10.00'),
        )
        response = self.client.post(reverse('dashboard_order_status', args=[order.pk]), {'status': 'shipped'})
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'shipped')
