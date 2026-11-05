from collections import defaultdict
from products.models import Product
from django.db import transaction
from django.db.models import F
from products.models import Product
from .models import Order



ALLOWED_TRANSITIONS={
      'pending':{'paid','cancelled'},
      'paid':{'shipped','cancelled'},
      'shipped':{'delivered'},
      'delivered':set(),
      'cancelled':set()
}

class InvalidTransition(Exception):
    pass



def change_order_status(order_id,new_status):
    with transaction.atomic():
        order=Order.objects.select_for_update().get(pk=order_id)


        if new_status not in ALLOWED_TRANSITIONS[order.status]:
            raise InvalidTransition(
                f"Cannot move order from '{order.status}' to {new_status}"
            )

        if new_status == 'cancelled':
            for item in order.items.all():
                if item.product_id:
                    Product.objects.filter(pk=item.product_id).update(
                        stock_qty=F('stock_qty')+ item.quantity
                    )

        order.status=new_status
        order.save(update_fields=['status','updated_at'])
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
            lines.append((product,qty
                          ))

    return lines,problems
