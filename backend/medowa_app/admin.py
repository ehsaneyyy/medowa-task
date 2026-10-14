from django.contrib import admin

from .models import Banner, Category, Product


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
