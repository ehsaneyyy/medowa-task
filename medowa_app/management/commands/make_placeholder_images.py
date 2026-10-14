import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from medowa_app.catalogue import BANNERS, PRODUCTS

CANVAS = 1200
BANNER_SIZE = (2000, 1125)

FONT_FILES = {
    'bold': ['segoeuib.ttf', 'seguisb.ttf', 'arialbd.ttf'],
    'regular': ['segoeui.ttf', 'arial.ttf'],
}

CATEGORY_BACKGROUNDS = {
    'mac': ((241, 244, 249), (226, 232, 241)),
    'iphone': ((244, 242, 247), (231, 228, 238)),
    'ipad': ((239, 245, 246), (226, 236, 238)),
    'watch': ((247, 242, 237), (239, 229, 221)),
}

CATEGORY_DEVICE = {
    'mac': ((60, 62, 68), (28, 30, 36)),
    'iphone': ((50, 52, 58), (20, 22, 26)),
    'ipad': ((64, 66, 72), (34, 36, 42)),
    'watch': ((72, 74, 80), (38, 40, 46)),
}

DEVICE_GEOMETRY = {
    'mac': (300, 320, 900, 780),
    'iphone': (420, 240, 780, 880),
    'ipad': (350, 250, 850, 860),
    'watch': (400, 300, 800, 780),
}

DEVICE_RADIUS = {'mac': 28, 'iphone': 76, 'ipad': 46, 'watch': 120}

DEVICE_INSET = {'mac': 20, 'iphone': 22, 'ipad': 24, 'watch': 28}

BANNER_PALETTES = {
    'iPhone 18 Pro': ((22, 28, 58), (98, 68, 152)),
    'Apple Watch Series 12': ((96, 26, 26), (210, 98, 44)),
    'Studio Display': ((28, 34, 46), (88, 108, 138)),
}


def linear_gradient(size, top, bottom):
    width, height = size
    column = Image.new('RGB', (1, height))
    pixels = column.load()
    for y in range(height):
        ratio = y / max(height - 1, 1)
        pixels[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
    return column.resize(size)


def rounded_mask(size, box, radius):
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    return mask


def load_font(kind, size):
    font_dir = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    for name in FONT_FILES[kind]:
        candidate = font_dir / name
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ''
    for word in text.split():
        candidate = word if not current else current + ' ' + word
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render_product(product, path):
    background = linear_gradient((CANVAS, CANVAS), *CATEGORY_BACKGROUNDS[product['category']]).convert('RGBA')
    box = DEVICE_GEOMETRY[product['category']]
    radius = DEVICE_RADIUS[product['category']]

    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (box[0] + 8, box[1] + 40, box[2] + 26, box[3] + 46),
        radius=radius,
        fill=(18, 22, 30, 38),
    )
    image = Image.alpha_composite(background, shadow)

    body = linear_gradient(image.size, *CATEGORY_DEVICE[product['category']]).convert('RGBA')
    image.paste(body, (0, 0), rounded_mask(image.size, box, radius))

    inset = DEVICE_INSET[product['category']]
    screen_box = (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset)
    screen = linear_gradient(image.size, (212, 227, 244), (238, 244, 252)).convert('RGBA')
    image.paste(screen, (0, 0), rounded_mask(image.size, screen_box, max(radius - inset, 8)))

    if product['category'] == 'iphone':
        center_x = (box[0] + box[2]) // 2
        notch_top = box[1] + inset + 16
        ImageDraw.Draw(image).rounded_rectangle(
            (center_x - 78, notch_top, center_x + 78, notch_top + 36),
            radius=18,
            fill=(18, 20, 24, 255),
        )

    draw = ImageDraw.Draw(image)
    draw.text((CANVAS // 2, 110), product['category'].upper(), font=load_font('regular', 38), fill=(126, 130, 138), anchor='ma')
    title_font = load_font('bold', 60)
    lines = wrap_text(draw, product['name'], title_font, 1010)[:2]
    y = 1004
    for line in lines:
        draw.text((CANVAS // 2, y), line, font=title_font, fill=(29, 29, 31), anchor='ma')
        y += 72

    image.convert('RGB').save(path, format='PNG', optimize=True)


def render_banner(banner, path):
    width, height = BANNER_SIZE
    image = linear_gradient((width, height), *BANNER_PALETTES[banner['title']]).convert('RGBA')

    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    painter = ImageDraw.Draw(overlay)
    painter.ellipse((-260, -320, 900, 640), fill=(255, 255, 255, 26))
    painter.ellipse((1180, 520, 2260, 1400), fill=(255, 255, 255, 20))
    painter.ellipse((1420, 120, 1860, 560), fill=(255, 255, 255, 16))
    image = Image.alpha_composite(image, overlay)

    draw = ImageDraw.Draw(image)
    draw.text((150, 470), banner['title'], font=load_font('bold', 118), fill=(255, 255, 255, 255), anchor='lm')
    draw.text((154, 604), banner['subtitle'], font=load_font('regular', 46), fill=(255, 255, 255, 214), anchor='lm')

    image.convert('RGB').save(path, format='PNG', optimize=True)


class Command(BaseCommand):
    help = 'Generates branded PNG placeholder images for every product and banner'

    def handle(self, *args, **options):
        products_dir = Path(settings.BASE_DIR, 'static', 'img', 'products')
        banners_dir = Path(settings.BASE_DIR, 'static', 'img', 'banners')
        products_dir.mkdir(parents=True, exist_ok=True)
        banners_dir.mkdir(parents=True, exist_ok=True)

        for product in PRODUCTS:
            render_product(product, products_dir / ('%s.png' % slugify(product['name'])))
        for banner in BANNERS:
            render_banner(banner, banners_dir / ('%s.png' % slugify(banner['title'])))

        self.stdout.write(self.style.SUCCESS(
            'Generated %d product PNGs and %d banner PNGs' % (len(PRODUCTS), len(BANNERS))
        ))
