from django.shortcuts import render
from rest_framework import viewsets,permissions,status,mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from .serializers import OrderCreateSerializer,OrderItemCreateSerializer
from .services import check_stock,change_order_status,InvalidTransition
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Order,OrderItem
from .serializers import OrderSerializer,OrderCreateSerializer
from .payment import create_checkout_session
import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.exceptions import PermissionDenied

logger=logging.getLogger(__name__)

class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

    
    def get_queryset(self):
        qs=Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
        user=self.request.user

        if self.request.query_params.get('scope') == 'all':
            if not user.is_staff:
                raise PermissionDenied()
            wanted=self.request.query_params.get('status')
            if wanted in dict(Order.STATUS_CHOICES):
                qs=qs.filter(status=wanted)
            return qs
        
        if user.is_staff and self.action != 'list':
            return qs
        return qs.filter(user=user)


    def create(self,request):
        serializer=OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.validated_data
        with transaction.atomic():
            lines,problems=check_stock(data['items'],lock=True)
            if problems:
                return Response({'errors':problems},status=status.HTTP_400_BAD_REQUEST)
            
            order=Order.objects.create(
                user=request.user,
                shipping_address=data['shipping_address'],
                total_price=Decimal('0'),
            )
            total=Decimal('0')
            for product,qty in lines:

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=qty
                )

                product.stock_qty-= qty
                product.save(update_fields=['stock_qty'])
                total+=product.price*qty
            order.total_price=total
            order.save(update_fields=['total_price'])
        return Response(OrderSerializer(order).data,status.HTTP_201_CREATED)

    @action(detail=True,methods=['post'],url_path='status')
    def set_status(self,request,pk=None):
        order=self.get_object()
        new_status=request.data.get('status')

        if new_status == 'paid':
            return Response({'error':'Orders are marked paid by the payment webhook only'},status=status.HTTP_403_FORBIDDEN)

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error':'Invalid status'},status=status.HTTP_400_BAD_REQUEST)

        is_self_cancel=new_status == 'cancelled' and order.status == 'pending'
        if not request.user.is_staff and not is_self_cancel:
            return Response({
                'error':'Not allowed'
            },status=status.HTTP_403_FORBIDDEN)
    

        try:
            order=change_order_status(order.pk,new_status)
        except InvalidTransition as e:
            return Response({
            'error':str(e)
            },status=status.HTTP_409_CONFLICT)

        return Response(OrderSerializer(order).data)





class CartValidateView(APIView):
    permission_classes=[permissions.AllowAny]

    def post(self,request):
        serializer=OrderItemCreateSerializer(data=request.data.get('items',[]),many=True)
        serializer.is_valid(raise_exception=True)
        lines,problems= check_stock(serializer.validated_data)
        return Response ({
              'valid':not problems,
              'items':[
                  {'product':p.id,'name':p.name,'price':p.price,'quantity':qty}
                  for p,qty in lines
              ],
              'problems':problems
        })


class PayOrderView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,pk):
        order=get_object_or_404(Order,pk=pk,user=request.user)
        if order.status != 'pending':
            return Response({'error':f'Order is {order.status}'})


        session=create_checkout_session(order)
        order.stripe_session_id=session.id
        order.save(update_fields=['stripe_session_id'])
        return Response({'checkout_url':session.url})

@csrf_exempt
@require_POST
def stripe_webhook(request):
    try:
        event=stripe.Webhook.construct_event(
            request.body,
            request.META.get('HTTP_STRIPE_SIGNATURE',''),
            settings.STRIPE_WEBHOOK_SECRET,
        )

    except (ValueError,stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] in ('checkout.session.completed',
                         'checkout.session.async_payment_succeeded'):
        session=event['data']['object'].to_dict()
        if session['payment_status'] == 'paid':
            order_id=(session.get('metadata') or {}).get('order_id')
            if not order_id:
                logger.warning('Session %s has no order id',session.get('id'))
                return HttpResponse(status=200)
            try:
                change_order_status(int(order_id),'paid')
            except InvalidTransition:
                logger.warning('Payment for order %s but transition not allowed',order_id)
            except Order.DoesNotExist:
                logger.error('Payment for unknown order %s',order_id)

    return HttpResponse(status=200)


                
    










