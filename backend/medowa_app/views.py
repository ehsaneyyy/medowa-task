from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_POST

from .forms import LoginForm, RegisterForm
from .models import Banner, Category, Product


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
            messages.success(request, 'Welcome to Core Store, %s. Your account is ready.' % user.username)
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
    stats = [
        {'label': 'Member for', 'value': '%d days' % account_age_days},
        {'label': 'Store products', 'value': Product.objects.filter(is_active=True).count()},
        {'label': 'Categories', 'value': Category.objects.count()},
        {'label': 'Live banners', 'value': Banner.objects.filter(is_active=True).count()},
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
        'image': product.image,
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
        'image': banner.image,
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
