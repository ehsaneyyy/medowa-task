from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_POST

from .cart import add_to_cart as cart_add, clear_cart, get_cart_items, get_cart_total, set_quantity
from .forms import CheckoutForm, LoginForm, RegisterForm
from .models import Banner, Category, Order, OrderItem, Product


def index(request):
    active_category = request.GET.get('category', '')
    categories = Category.objects.all()
    category_slugs = list(categories.values_list('slug', flat=True))
    banners = Banner.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    if active_category in category_slugs:
        products = products.filter(category__slug=active_category)
    elif active_category:
        active_category = ''
    context = {
        'banners': banners,
        'categories': categories,
        'products': products,
        'active_category': active_category,
        'featured_product': products.first(),
        'category_count': categories.count(),
        'product_count': products.count(),
    }
    return render(request, 'index.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register_user(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to medowa-task, %s. Your account is ready.' % user.username)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@never_cache
def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')
    redirect_to = request.POST.get('next') or request.GET.get('next') or ''
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Signed in successfully.')
            if redirect_to and url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
                return redirect(redirect_to)
            return redirect('index')
    else:
        form = LoginForm(request)
        redirect_to = request.GET.get('next', '')
    context = {
        'form': form,
        'next': redirect_to,
    }
    return render(request, 'login.html', context)


@require_POST
@never_cache
def logout_user(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('index')


@login_required
@never_cache
def profile_user(request):
    account_age_days = (timezone.now().date() - request.user.date_joined.date()).days
    orders = request.user.orders.prefetch_related('items').all()
    stats = [
        {'label': 'Member for', 'value': '%d days' % account_age_days},
        {'label': 'Store products', 'value': Product.objects.filter(is_active=True).count()},
        {'label': 'Categories', 'value': Category.objects.count()},
        {'label': 'Orders placed', 'value': orders.count()},
    ]
    metadata = [
        {'label': 'Username', 'value': request.user.username},
        {'label': 'Email', 'value': request.user.email or 'Not provided'},
        {'label': 'Date joined', 'value': request.user.date_joined.strftime('%d %B %Y, %H:%M')},
        {'label': 'Last login', 'value': request.user.last_login.strftime('%d %B %Y, %H:%M') if request.user.last_login else 'First session'},
        {'label': 'Account status', 'value': 'Active'},
        {'label': 'Privileges', 'value': 'Store administrator' if request.user.is_staff else 'Customer'},
        {'label': 'Session expiry', 'value': request.session.get_expiry_date().strftime('%d %B %Y, %H:%M')},
        {'label': 'Active sessions', 'value': 'Current browser only' if request.session.get_expire_at_browser_close() else 'Persistent'},
    ]
    context = {
        'stats': stats,
        'metadata': metadata,
        'account_age_days': account_age_days,
        'orders': orders,
        'order_count': orders.count(),
        'initials': (request.user.username[:2] or 'U').upper(),
        'next': reverse('profile'),
    }
    return render(request, 'profile.html', context)


def serialize_product(product):
    return {
        'id': product.pk,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'image': product.image_url,
        'category': {
            'id': product.category.pk,
            'name': product.category.name,
            'slug': product.category.slug,
        },
        'url': product.get_absolute_url(),
    }


def serialize_category(category):
    return {
        'id': category.pk,
        'name': category.name,
        'slug': category.slug,
        'url': category.get_absolute_url(),
        'product_count': category.product_count,
    }


def serialize_banner(banner):
    return {
        'id': banner.pk,
        'title': banner.title,
        'subtitle': banner.subtitle,
        'image': banner.image_url,
        'link_url': banner.link_url,
    }


@require_GET
def api_products(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    payload = [serialize_product(product) for product in products]
    return JsonResponse({'count': len(payload), 'results': payload})


@require_GET
def api_categories(request):
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    )
    payload = [serialize_category(category) for category in categories]
    return JsonResponse({'count': len(payload), 'results': payload})


@require_GET
def api_banners(request):
    banners = Banner.objects.filter(is_active=True)
    payload = [serialize_banner(banner) for banner in banners]
    return JsonResponse({'count': len(payload), 'results': payload})


@require_GET
def api_product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return JsonResponse(serialize_product(product))


def _safe_redirect(request, fallback):
    target = request.POST.get('next') or request.GET.get('next')
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return redirect(target)
    return redirect(fallback)


@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        quantity = 1
    cart_add(request, product.pk, quantity)
    messages.success(request, '%s was added to your bag.' % product.name)
    return redirect('cart')


@require_GET
def cart_detail(request):
    context = {
        'items': get_cart_items(request),
        'total': get_cart_total(request),
    }
    return render(request, 'cart.html', context)


@require_POST
def update_cart_item(request, pk):
    set_quantity(request, pk, request.POST.get('quantity', 1))
    return redirect('cart')


@require_POST
def remove_cart_item(request, pk):
    set_quantity(request, pk, 0)
    messages.info(request, 'Item removed from your bag.')
    return redirect('cart')


@login_required
@never_cache
def checkout(request):
    items = get_cart_items(request)
    if not items:
        messages.info(request, 'Your bag is empty. Add a product before checking out.')
        return redirect('index')
    total = get_cart_total(request)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    postal_code=form.cleaned_data['postal_code'],
                    total=total,
                )
                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product=item['product'],
                        price=item['product'].price,
                        quantity=item['quantity'],
                    )
                    for item in items
                ])
            clear_cart(request)
            messages.success(request, 'Order %s placed successfully.' % order.reference)
            return redirect('order_success', pk=order.pk)
    else:
        form = CheckoutForm(initial={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        })
    context = {
        'form': form,
        'items': items,
        'total': total,
    }
    return render(request, 'checkout.html', context)


@login_required
@never_cache
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'order_success.html', {'order': order})
