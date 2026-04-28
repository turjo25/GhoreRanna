def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values()) if cart else 0
    return {'global_cart_count': count}