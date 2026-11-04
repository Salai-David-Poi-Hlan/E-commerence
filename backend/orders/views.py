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
from products.models import Product
from .models import Order,OrderItem
from .serializers import OrderSerializer,OrderCreateSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


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
                  {'product':p.id,'name':p.name,'prcie':p.price,'quantity':qty}
                  for p,qty in lines
              ],
              'problems':problems
        })










