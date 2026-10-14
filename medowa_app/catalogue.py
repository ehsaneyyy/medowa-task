from django.conf import settings
from django.utils.text import slugify

PRODUCT_IMAGE_DIR = 'img/products'
BANNER_IMAGE_DIR = 'img/banners'

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
        'link_url': '/?category=iphone',
        'is_active': True,
    },
    {
        'title': 'Apple Watch Series 12',
        'subtitle': 'The ultimate watch. Reimagined.',
        'link_url': '/?category=watch',
        'is_active': True,
    },
    {
        'title': 'Studio Display',
        'subtitle': 'A stunning 5K retina canvas for your desk.',
        'link_url': '/?category=mac',
        'is_active': True,
    },
]

PRODUCTS = [
    {
        'name': 'MacBook Air 13-inch M4',
        'description': 'Featuring the ultra-efficient M4 chip, a stunning Liquid Retina display, up to 18 hours of battery life, and a fanless silent design finished in Sky Blue.',
        'price': '99900.00',
        'category': 'mac',
        'is_active': True,
    },
    {
        'name': 'MacBook Pro 14-inch M4 Pro',
        'description': 'M4 Pro power with a breathtaking Liquid Retina XDR display, Thunderbolt 5 connectivity, and all-day battery life for pro workflows.',
        'price': '199900.00',
        'category': 'mac',
        'is_active': True,
    },
    {
        'name': 'iMac 24-inch M4',
        'description': 'Strikingly thin all-in-one design with a 4.5K Retina display, M4 performance, and a colour-matched accessories suite.',
        'price': '134900.00',
        'category': 'mac',
        'is_active': True,
    },
    {
        'name': 'iPhone 18 Pro',
        'description': 'Built in titanium with a revolutionary centre-stage camera system, A20 Pro chip, and a ProMotion display that adapts to everything you do.',
        'price': '134900.00',
        'category': 'iphone',
        'is_active': True,
    },
    {
        'name': 'iPhone 17',
        'description': 'A perfect balance of design and performance with the A19 chip, an advanced dual-camera system, and Ceramic Shield front and back.',
        'price': '89900.00',
        'category': 'iphone',
        'is_active': True,
    },
    {
        'name': 'iPhone 16',
        'description': 'A perfect balance of design and performance with the A18 chip, an advanced dual-camera system, and Ceramic Shield front and back.',
        'price': '69900.00',
        'category': 'iphone',
        'is_active': True,
    },
    {
        'name': 'iPad Pro 13-inch M4',
        'description': 'Ultra-thin, ridiculously powerful with the Ultra Retina XDR tandem OLED display, M4 chip, and support for Apple Pencil Pro.',
        'price': '149900.00',
        'category': 'ipad',
        'is_active': True,
    },
    {
        'name': 'iPad 11-inch A16',
        'description': 'Wonderfully capable, beautifully portable iPad with a gorgeous 11-inch Liquid Retina display and support for Apple Pencil and Magic Keyboard.',
        'price': '44900.00',
        'category': 'ipad',
        'is_active': True,
    },
    {
        'name': 'iPad Air 11-inch M3',
        'description': 'Performance that puts more ideas first with the M3 chip, landscape front camera, and a brilliant Liquid Retina display.',
        'price': '74900.00',
        'category': 'ipad',
        'is_active': True,
    },
    {
        'name': 'Apple Watch Series 12',
        'description': 'The ultimate watch for health, fitness, and safety with a brighter always-on display, sleep score insights, and 5G cellular options.',
        'price': '46900.00',
        'category': 'watch',
        'is_active': True,
    },
    {
        'name': 'Apple Watch Ultra 3',
        'description': 'The most rugged and capable Apple Watch with a 49mm titanium case, precision dual-frequency GPS, and up to 42 hours of battery life.',
        'price': '89900.00',
        'category': 'watch',
        'is_active': True,
    },
    {
        'name': 'Apple Watch SE 3',
        'description': 'All the essentials of Apple Watch at a remarkable value with the S10 chip, sleep apnea notifications, and fast charging.',
        'price': '29900.00',
        'category': 'watch',
        'is_active': True,
    },
]


def product_image(name):
    return '%s%s/%s.png' % (settings.STATIC_URL, 'img/products', slugify(name))


def banner_image(title):
    return '%s%s/%s.png' % (settings.STATIC_URL, 'img/banners', slugify(title))


def product_image_paths():
    return [product_image(item['name']) for item in PRODUCTS]


def banner_image_paths():
    return [banner_image(item['title']) for item in BANNERS]
