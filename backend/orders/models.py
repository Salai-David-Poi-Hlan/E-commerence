from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES=[
        ('pending','Pending'),
        ('paid','Paid'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled')
    ]


    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    shipping_address=models.TextField(blank=True)


    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"



class OrderItem(models.Model):
    order=models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)

    product_name=models.CharField(max_length=255)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.PositiveBigIntegerField()



    def subtotal(self):
        return self.price * self.quantity


    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
