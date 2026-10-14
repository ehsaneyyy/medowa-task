from django.contrib import admin

from .models import Banner, Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']
    list_per_page = 50


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    list_editable = ['price', 'is_active']
    search_fields = ['name', 'description', 'category__name']
    list_display_links = ['name', 'category']
    prepopulated_fields = {}
    date_hierarchy = 'created_at'
    list_per_page = 50
    ordering = ['-created_at']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'link_url', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_active', 'link_url']
    search_fields = ['title', 'subtitle', 'link_url']
    list_per_page = 50


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'price', 'quantity']
    readonly_fields = ['product', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'full_name', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['full_name', 'email', 'user__username']
    readonly_fields = ['user', 'total', 'created_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    list_per_page = 50
