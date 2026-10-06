from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer



class ProductViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
# Create your views here.
    def get_permission(self):
        if self.action in ["create","update","partial_update","destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
