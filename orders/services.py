from .models import Order, OrderItem

def create_order_from_cart(cart):
    order = Order.objects.create(
        user=cart.user,
        vendor=cart.vendor,
        session_key=cart.session_key,
        total=cart.total
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            total=item.total
        )

    cart.is_active = False
    cart.save()

    return order