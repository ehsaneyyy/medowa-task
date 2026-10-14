from decimal import Decimal

from .models import Product


def _cart(request):
    return request.session.get('cart') or {}


def _save(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def add_to_cart(request, product_id, quantity=1):
    cart = _cart(request)
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + int(quantity)
    _save(request, cart)


def set_quantity(request, product_id, quantity):
    cart = _cart(request)
    key = str(product_id)
    quantity = int(quantity)
    if quantity > 0:
        cart[key] = quantity
    else:
        cart.pop(key, None)
    _save(request, cart)


def clear_cart(request):
    _save(request, {})


def get_cart_items(request):
    cart = _cart(request)
    if not cart:
        return []
    products = Product.objects.filter(pk__in=[int(pk) for pk in cart.keys()], is_active=True)
    by_id = {product.pk: product for product in products}
    items = []
    for key, quantity in cart.items():
        product = by_id.get(int(key))
        if product is None:
            continue
        quantity = int(quantity)
        items.append({
            'product': product,
            'quantity': quantity,
            'line_total': product.price * quantity,
        })
    return items


def get_cart_total(request):
    return sum((item['line_total'] for item in get_cart_items(request)), Decimal('0'))


def get_cart_count(request):
    return sum(int(quantity) for quantity in _cart(request).values())
