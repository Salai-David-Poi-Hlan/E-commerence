from rest_framework import serializers
from .models import Order,OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderItem
        fields=['id','product','product_name','price','quantity']

class OrderItemCreateSerializer(serializers.Serializer):
    product=serializers.IntegerField()
    quantity=serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model=Order
        fields=['id','status','total_price','shipping_address','items','created_at']
        read_only_fields=['total_price','status']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address=serializers.CharField()
    items=OrderItemCreateSerializer(many=True)


