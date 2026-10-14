from .cart import get_cart_count


def cart(request):
    return {'cart_count': get_cart_count(request)}
