from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from medowa_app.catalogue import BANNERS, CATEGORIES, PRODUCTS, banner_image, product_image
from medowa_app.models import Banner, Category, Product


class Command(BaseCommand):
    help = 'Seeds categories, banners, and premium Apple inventory into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Verify every local product and banner image exists before seeding',
        )

    def handle(self, *args, **options):
        if options['validate']:
            self.validate_images()
        for category_data in CATEGORIES:
            Category.objects.update_or_create(
                slug=category_data['slug'],
                defaults={'name': category_data['name']},
            )
        for banner_data in BANNERS:
            defaults = dict(banner_data)
            defaults['image'] = banner_image(banner_data['title'])
            Banner.objects.update_or_create(title=banner_data['title'], defaults=defaults)
        for product_data in PRODUCTS:
            category = Category.objects.get(slug=product_data['category'])
            defaults = {
                'description': product_data['description'],
                'price': product_data['price'],
                'image': product_image(product_data['name']),
                'category': category,
                'is_active': product_data['is_active'],
            }
            Product.objects.update_or_create(name=product_data['name'], defaults=defaults)
        self.stdout.write(self.style.SUCCESS(
            'Seeded %d categories, %d banners, %d products' % (
                Category.objects.count(), Banner.objects.count(), Product.objects.count()
            )
        ))

    def image_paths(self):
        return (
            [banner_image(banner['title']) for banner in BANNERS]
            + [product_image(product['name']) for product in PRODUCTS]
        )

    def validate_images(self):
        missing = [
            path for path in self.image_paths()
            if not Path(settings.BASE_DIR, path.lstrip('/')).exists()
        ]
        if missing:
            raise CommandError(
                'Missing local image files: %s. Run "python manage.py make_placeholder_images".'
                % ', '.join(missing)
            )
        self.stdout.write(self.style.SUCCESS('Validated %d local image files' % len(self.image_paths())))
