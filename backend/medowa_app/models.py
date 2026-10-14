from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('index') + '?category=' + self.slug


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(
        blank=True,
        help_text='External image URL. Used when no uploaded file is provided.',
    )
    image_file = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text='Upload an image file. Takes precedence over the external URL.',
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image or ''


class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255)
    image = models.URLField(
        blank=True,
        help_text='External image URL. Used when no uploaded file is provided.',
    )
    image_file = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        help_text='Upload an image file. Takes precedence over the external URL.',
    )
    link_url = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image or ''
