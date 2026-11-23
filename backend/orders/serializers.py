from rest_framework import serializers
from .models import Order,OrderItem
from .services import ALLOWED_TRANSITIONS

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=['id','product','product_name','price','quantity']

class OrderItemCreateSerializer(serializers.Serializer):
    product=serializers.IntegerField()
    quantity=serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    customer=serializers.CharField(source='user.username',read_only=True)
    customer_email = serializers.CharField(source='user.email',read_only=True)
    next_statuses=serializers.SerializerMethodField()

    class Meta:
        model=Order
        fields=['id','status','total_price','shipping_address','items','created_at','paid_at','customer','customer_email','next_statuses']
        read_only_fields=['total_price','status']


    def get_next_statuses(self,obj):
        return sorted(ALLOWED_TRANSITIONS[obj.status])


class OrderCreateSerializer(serializers.Serializer):
    shipping_address=serializers.CharField()
    items=OrderItemCreateSerializer(many=True)


