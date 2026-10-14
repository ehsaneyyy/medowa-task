from django.contrib.auth.models import User
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


class Order(models.Model):
    STATUS_PLACED = 'placed'
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLACED)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return 'ORD-%05d' % self.pk

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return '%s x%d' % (self.product.name if self.product else 'Item', self.quantity)

    @property
    def line_total(self):
        return self.price * self.quantity
