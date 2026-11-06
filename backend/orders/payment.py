import stripe
from django.conf import settings

stripe.api_key=settings.STRIPE_SECRET_KEY

def create_checkout_session(order):
    line_items=[
        {
            'quantity':item.quantity,
            'price_data':{
                'currency':'thb',
                'unit_amount':int((item.price*100).to_integral_value()),
                'product_data':{'name':item.product_name}
            }
        }
        for item in order.items.all()
    ]

    return stripe.checkout.Session.create(
        mode='payment',
        line_items=line_items,
        client_reference_id=str(order.pk),
        metadata={'order_id':str(order.pk)},
        success_url=f'{settings.FRONTEND_URL}/orders/{order.pk}/success',
        cancel_url=f'{settings.FRONTEND_URL}/cart'
    )