from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_user, name='profile'),
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_cart_item, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:pk>/', views.order_success, name='order_success'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/<int:pk>/', views.api_product_detail, name='api_product_detail'),
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/banners/', views.api_banners, name='api_banners'),
]
