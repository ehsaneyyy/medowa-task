from functools import wraps

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import BannerForm, CategoryForm, ProductForm, StaffUserForm
from .models import Banner, Category, Order, Product


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Please sign in with an administrator account.')
            return redirect('/login/?next=%s' % request.path)
        if not request.user.is_staff:
            messages.error(request, 'Administrator access is required to open the dashboard.')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped


def _next(request, fallback):
    target = request.POST.get('next')
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return redirect(target)
    return redirect(fallback)


@staff_required
def home(request):
    orders = Order.objects.all()
    revenue = orders.exclude(status='cancelled').aggregate(total=Sum('total'))['total'] or 0
    context = {
        'dash_section': 'home',
        'stats': [
            {'label': 'Products', 'value': Product.objects.count(), 'sub': '%d active' % Product.objects.filter(is_active=True).count(), 'url': 'dashboard_products'},
            {'label': 'Categories', 'value': Category.objects.count(), 'sub': 'collections', 'url': 'dashboard_categories'},
            {'label': 'Banners', 'value': Banner.objects.count(), 'sub': '%d live' % Banner.objects.filter(is_active=True).count(), 'url': 'dashboard_banners'},
            {'label': 'Orders', 'value': orders.count(), 'sub': '\u20b9%s revenue' % format(revenue, ',.0f'), 'url': 'dashboard_orders'},
        ],
        'recent_orders': orders.select_related('user')[:6],
        'recent_products': Product.objects.select_related('category')[:6],
        'customer_count': User.objects.filter(is_staff=False).count(),
    }
    return render(request, 'dashboard/home.html', context)


@staff_required
def product_list(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.select_related('category')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    return render(request, 'dashboard/product_list.html', {
        'dash_section': 'products',
        'products': products,
        'query': query,
    })


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product "%s" was created.' % product.name)
            return redirect('dashboard_products')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {
        'dash_section': 'products',
        'form': form,
        'mode': 'create',
        'title': 'New product',
    })


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product "%s" was updated.' % product.name)
            return redirect('dashboard_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {
        'dash_section': 'products',
        'form': form,
        'product': product,
        'mode': 'edit',
        'title': 'Edit product',
    })


@staff_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.info(request, 'Product "%s" was deleted.' % name)
    return _next(request, 'dashboard_products')


@staff_required
@require_POST
def product_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active'])
    messages.success(request, 'Product "%s" is now %s.' % (product.name, 'active' if product.is_active else 'hidden'))
    return _next(request, 'dashboard_products')


@staff_required
def category_list(request):
    categories = Category.objects.annotate(product_total=Count('products'))
    return render(request, 'dashboard/category_list.html', {
        'dash_section': 'categories',
        'categories': categories,
    })


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Category "%s" was created.' % category.name)
            return redirect('dashboard_categories')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/category_form.html', {
        'dash_section': 'categories',
        'form': form,
        'mode': 'create',
        'title': 'New category',
    })


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category "%s" was updated.' % category.name)
            return redirect('dashboard_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'dashboard/category_form.html', {
        'dash_section': 'categories',
        'form': form,
        'category': category,
        'mode': 'edit',
        'title': 'Edit category',
    })


@staff_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.info(request, 'Category "%s" and its products were deleted.' % name)
    return redirect('dashboard_categories')


@staff_required
def banner_list(request):
    return render(request, 'dashboard/banner_list.html', {
        'dash_section': 'banners',
        'banners': Banner.objects.all(),
    })


@staff_required
def banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, 'Banner "%s" was created.' % banner.title)
            return redirect('dashboard_banners')
    else:
        form = BannerForm()
    return render(request, 'dashboard/banner_form.html', {
        'dash_section': 'banners',
        'form': form,
        'mode': 'create',
        'title': 'New banner',
    })


@staff_required
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner "%s" was updated.' % banner.title)
            return redirect('dashboard_banners')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'dashboard/banner_form.html', {
        'dash_section': 'banners',
        'form': form,
        'banner': banner,
        'mode': 'edit',
        'title': 'Edit banner',
    })


@staff_required
@require_POST
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    title = banner.title
    banner.delete()
    messages.info(request, 'Banner "%s" was deleted.' % title)
    return redirect('dashboard_banners')


@staff_required
@require_POST
def banner_toggle(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save(update_fields=['is_active'])
    messages.success(request, 'Banner "%s" is now %s.' % (banner.title, 'active' if banner.is_active else 'hidden'))
    return redirect('dashboard_banners')


@staff_required
def order_list(request):
    status = request.GET.get('status', '')
    orders = Order.objects.select_related('user')
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)
    return render(request, 'dashboard/order_list.html', {
        'dash_section': 'orders',
        'orders': orders,
        'active_status': status,
        'statuses': Order.STATUS_CHOICES,
    })


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    return render(request, 'dashboard/order_detail.html', {
        'dash_section': 'orders',
        'order': order,
        'items': order.items.select_related('product'),
        'statuses': Order.STATUS_CHOICES,
    })


@staff_required
@require_POST
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    status = request.POST.get('status', '')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save(update_fields=['status'])
        messages.success(request, 'Order %s marked as %s.' % (order.reference, order.get_status_display()))
    return redirect('dashboard_order_detail', pk=order.pk)


@staff_required
def user_list(request):
    accounts = User.objects.annotate(order_count=Count('orders')).order_by('-date_joined')
    return render(request, 'dashboard/user_list.html', {
        'dash_section': 'users',
        'accounts': accounts,
        'staff_total': User.objects.filter(is_staff=True).count(),
        'customer_total': User.objects.filter(is_staff=False).count(),
    })


@staff_required
def user_create(request):
    if request.method == 'POST':
        form = StaffUserForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, 'User "%s" was created.' % account.username)
            return redirect('dashboard_users')
    else:
        form = StaffUserForm()
    return render(request, 'dashboard/user_form.html', {
        'dash_section': 'users',
        'form': form,
        'mode': 'create',
        'title': 'New user',
    })


@staff_required
def user_edit(request, pk):
    account = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StaffUserForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'User "%s" was updated.' % account.username)
            return redirect('dashboard_users')
    else:
        form = StaffUserForm(instance=account)
    return render(request, 'dashboard/user_form.html', {
        'dash_section': 'users',
        'form': form,
        'account': account,
        'mode': 'edit',
        'title': 'Edit user',
    })


@staff_required
@require_POST
def user_toggle(request, pk):
    account = get_object_or_404(User, pk=pk)
    if account == request.user:
        messages.error(request, 'You cannot change the status of the account you are signed in with.')
        return redirect('dashboard_users')
    account.is_active = not account.is_active
    account.save(update_fields=['is_active'])
    messages.success(request, 'User "%s" is now %s.' % (account.username, 'active' if account.is_active else 'disabled'))
    return redirect('dashboard_users')


@staff_required
@require_POST
def user_delete(request, pk):
    account = get_object_or_404(User, pk=pk)
    if account == request.user:
        messages.error(request, 'You cannot delete the account you are currently signed in with.')
        return redirect('dashboard_users')
    username = account.username
    account.delete()
    messages.info(request, 'User "%s" was deleted.' % username)
    return redirect('dashboard_users')
