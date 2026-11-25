from collections import defaultdict
from products.models import Product
from django.db import transaction
from django.db.models import F
from products.models import Product
from .models import Order
from django.utils import timezone
from .payment import refund_order

ALLOWED_TRANSITIONS={
      'pending':{'paid','cancelled'},
      'paid':{'shipped','cancelled'},
      'shipped':{'delivered'},
      'delivered':set(),
      'cancelled':set()
}

class InvalidTransition(Exception):
    pass



def change_order_status(order_id,new_status,expected_status=None):
    with transaction.atomic():
        order=Order.objects.select_for_update().get(pk=order_id)
        if expected_status and order.status != expected_status:
            raise InvalidTransition(
                f"Order is '{order.status}', expected '{expected_status}'"
            )
        if new_status not in ALLOWED_TRANSITIONS[order.status]:
            raise InvalidTransition(
                f"Cannot move order from '{order.status}' to {new_status}"
            )
        update_fields=['status','updated_at']

        if new_status == 'cancelled':
            if order.status == 'paid':
                refund=refund_order(order)
                order.stripe_refund_id=refund.id
                order.refunded_at=timezone.now()
                update_fields+=["stripe_refund_id","refunded_at"]
            for item in order.items.all():
                if item.product_id:
                    Product.objects.filter(pk=item.product_id).update(
                        stock_qty=F('stock_qty')+ item.quantity
                    )
        if new_status == 'paid':
            order.paid_at=timezone.now()
            update_fields.append('paid_at')
        order.status=new_status
        order.save(update_fields=update_fields)
    return order



def check_stock(items,lock=False):
    merged=defaultdict(int)
    for item in items:
        merged[item['product']]+=item['quantity']

    qs=Product.objects.filter(id__in=merged.keys())
    if lock:
        qs=qs.select_for_update()
    products={p.id : p for p in qs}

    lines,problems=[],[]

    for product_id, qty in merged.items():
        product=products.get(product_id)
        if product is None:
            problems.append({'product':product_id, 'error':'not_found'})
        elif product.stock_qty < qty:
            problems.append({
                'product':product_id,
                'name':product.name,
                'error':'insufficient_stock',
                'requested':qty,
                'available':product.stock_qty
            })
        else:
            lines.append((product,qty))
    return lines,problems
