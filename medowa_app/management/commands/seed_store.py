import ssl
import urllib.request

from django.core.management.base import BaseCommand

from medowa_app.models import Banner, Category, Product

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'}

CATEGORIES = [
    {'name': 'Mac', 'slug': 'mac'},
    {'name': 'iPhone', 'slug': 'iphone'},
    {'name': 'iPad', 'slug': 'ipad'},
    {'name': 'Watch', 'slug': 'watch'},
]

BANNERS = [
    {
        'title': 'iPhone 18 Pro',
        'subtitle': 'Titanium. So strong. So light. So Pro.',
        'image': 'https://www.apple.com/v/iphone/home/ck/images/overview/priority-router/hero_iphone_18_pro__cybfx8phkvu6_large.jpg',
        'link_url': '/?category=iphone',
        'is_active': True,
    },
    {
        'title': 'Apple Watch Series 12',
        'subtitle': 'The ultimate watch. Reimagined.',
        'image': 'https://www.apple.com/assets-www/en_WW/watch/01_banner_card_1up/large/essentials_d0579d0bd.jpg',
        'link_url': '/?category=watch',
        'is_active': True,
    },
    {
        'title': 'Studio Display',
        'subtitle': 'A stunning 5K retina canvas for your desk.',
        'image': 'https://www.apple.com/assets-www/en_WW/mac/03_banner_card_2up/large/display_7ed4bbd25.png',
        'link_url': '/?category=mac',
        'is_active': True,
    },
]

PRODUCTS = [
    {
        'name': 'MacBook Air 13-inch M4',
        'description': 'Featuring the ultra-efficient M4 chip, a stunning Liquid Retina display, up to 18 hours of battery life, and a fanless silent design finished in Sky Blue.',
        'price': '99900.00',
        'image': 'https://www.apple.com/assets-www/en_WW/mac/04_product_tile/large/mba_13_15_286f55670_2x.jpg',
        'category': 'mac',
        'is_active': True,
    },
    {
        'name': 'MacBook Pro 14-inch M4 Pro',
        'description': 'M4 Pro power with a breathtaking Liquid Retina XDR display, Thunderbolt 5 connectivity, and all-day battery life for pro workflows.',
        'price': '199900.00',
        'image': 'https://www.apple.com/assets-www/en_WW/mac/04_product_tile/large/mbp_14_16_028335cc2_2x.jpg',
        'category': 'mac',
        'is_active': True,
    },
    {
        'name': 'iMac 24-inch M4',
        'description': 'Strikingly thin all-in-one design with a 4.5K Retina display, M4 performance, and a colour-matched accessories suite.',
        'price': '134900.00',
        'image': 'https://www.apple.com/assets-www/en_WW/mac/04_product_tile/large/imac_24_664024e20_2x.jpg',
        'category': 'mac',
        'is_active': True,
    },
    {
        'name': 'iPhone 18 Pro',
        'description': 'Built in titanium with a revolutionary centre-stage camera system, A20 Pro chip, and a ProMotion display that adapts to everything you do.',
        'price': '134900.00',
        'image': 'https://www.apple.com/in/iphone/home/images/overview/select/iphone_18_pro__dj48ysc0yagm_large.jpg',
        'category': 'iphone',
        'is_active': True,
    },
    {
        'name': 'iPhone 17',
        'description': 'A perfect balance of design and performance with the A19 chip, an advanced dual-camera system, and Ceramic Shield front and back.',
        'price': '89900.00',
        'image': 'https://www.apple.com/in/iphone/home/images/overview/select/iphone_17__fb1277oq3eaa_large.jpg',
        'category': 'iphone',
        'is_active': True,
    },
    {
        'name': 'iPhone 16',
        'description': 'A perfect balance of design and performance with the A18 chip, an advanced dual-camera system, and Ceramic Shield front and back.',
        'price': '69900.00',
        'image': 'https://www.apple.com/in/iphone/home/images/overview/select/iphone_16__b6tkv86m2gc2_large.jpg',
        'category': 'iphone',
        'is_active': True,
    },
    {
        'name': 'iPad Pro 13-inch M4',
        'description': 'Ultra-thin, ridiculously powerful with the Ultra Retina XDR tandem OLED display, M4 chip, and support for Apple Pencil Pro.',
        'price': '149900.00',
        'image': 'https://www.apple.com/assets-www/en_WW/ipad/03_product_tile/medium/ipad_pro_81ecf8e96.png',
        'category': 'ipad',
        'is_active': True,
    },
    {
        'name': 'iPad 11-inch A16',
        'description': 'Wonderfully capable, beautifully portable iPad with a gorgeous 11-inch Liquid Retina display and support for Apple Pencil and Magic Keyboard.',
        'price': '44900.00',
        'image': 'https://www.apple.com/assets-www/en_WW/ipad/03_product_tile/large/ipad_07e11a653.png',
        'category': 'ipad',
        'is_active': True,
    },
    {
        'name': 'iPad Air 11-inch M3',
        'description': 'Performance that puts more ideas first with the M3 chip, landscape front camera, and a brilliant Liquid Retina display.',
        'price': '74900.00',
        'image': 'https://www.apple.com/assets-www/en_WW/ipad/03_product_tile/small/ipad_air_4db1b7772.png',
        'category': 'ipad',
        'is_active': True,
    },
    {
        'name': 'Apple Watch Series 12',
        'description': 'The ultimate watch for health, fitness, and safety with a brighter always-on display, sleep score insights, and 5G cellular options.',
        'price': '46900.00',
        'image': 'https://www.apple.com/assets-www/en_IN/watch/01_product_tile/large/s12_f529dba46.png',
        'category': 'watch',
        'is_active': True,
    },
    {
        'name': 'Apple Watch Ultra 3',
        'description': 'The most rugged and capable Apple Watch with a 49mm titanium case, precision dual-frequency GPS, and up to 42 hours of battery life.',
        'price': '89900.00',
        'image': 'https://www.apple.com/assets-www/en_IN/watch/01_product_tile/large/u4_5133b59ee.png',
        'category': 'watch',
        'is_active': True,
    },
    {
        'name': 'Apple Watch SE 3',
        'description': 'All the essentials of Apple Watch at a remarkable value with the S10 chip, sleep apnea notifications, and fast charging.',
        'price': '29900.00',
        'image': 'https://www.apple.com/assets-www/en_IN/watch/01_product_tile/medium/se3_211620bbd.png',
        'category': 'watch',
        'is_active': True,
    },
]


class Command(BaseCommand):
    help = 'Seeds categories, banners, and premium Apple inventory into the database'

    def add_arguments(self, parser):
        parser.add_argument('--validate', action='store_true', help='Validate every image URL over HTTP before seeding')

    def handle(self, *args, **options):
        validate = options['validate']
        urls = [banner['image'] for banner in BANNERS] + [product['image'] for product in PRODUCTS]
        if validate:
            self.validate_urls(urls)
        for category_data in CATEGORIES:
            Category.objects.update_or_create(slug=category_data['slug'], defaults={'name': category_data['name']})
        for banner_data in BANNERS:
            Banner.objects.update_or_create(title=banner_data['title'], defaults=banner_data)
        for product_data in PRODUCTS:
            category = Category.objects.get(slug=product_data['category'])
            defaults = {
                'description': product_data['description'],
                'price': product_data['price'],
                'image': product_data['image'],
                'category': category,
                'is_active': product_data['is_active'],
            }
            Product.objects.update_or_create(name=product_data['name'], defaults=defaults)
        self.stdout.write(self.style.SUCCESS(
            'Seeded %d categories, %d banners, %d products' % (
                Category.objects.count(), Banner.objects.count(), Product.objects.count()
            )
        ))

    def validate_urls(self, urls):
        failures = []
        for url in urls:
            if not self.url_is_reachable(url):
                failures.append(url)
        if failures:
            raise RuntimeError('Unreachable image URLs: %s' % ', '.join(failures))
        self.stdout.write(self.style.SUCCESS('Validated %d image URLs' % len(urls)))

    def url_is_reachable(self, url):
        request = urllib.request.Request(url, headers=REQUEST_HEADERS, method='GET')
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=8, context=SSL_CONTEXT) as response:
                    if response.status == 200:
                        return True
            except Exception:
                if attempt == 2:
                    return False
        return False
