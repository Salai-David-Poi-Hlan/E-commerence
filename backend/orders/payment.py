import stripe
from django.conf import settings
import time


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
        cancel_url=f'{settings.FRONTEND_URL}/cart',
        expires_at=int(time.time()) + 31*60
    )




class RefundFailed(Exception):
    pass



def refund_order(order):
    payment_intent= order.stripe_payment_intent_id

    try:
        if not payment_intent and order.stripe_session_id:
            session = stripe.checkout.Session.retrieve(order.stripe_session_id)
            payment_intent=session.payment_intent
        if not payment_intent:
            raise RefundFailed(f"No payment found for order {order.pk}")

        return stripe.Refund.create(
            payment_intent=payment_intent,
            reason='requested_by_customer',
            metadata={'order_id':str(order.pk)},
            idempotency_key=f'refund-order-{order.pk}'
        )
    except stripe.InvalidRequestError as e:
        if getattr(e,'code',None) == 'charge_already_refunded':
            existing = stripe.Refund.list(payment_intent=payment_intent,limit=1).data
            if existing:
                return existing[0]
        raise RefundFailed(str(e)) from e
    
    except stripe.StripeError as e:
        raise RefundFailed(str(e)) from e
