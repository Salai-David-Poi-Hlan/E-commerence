from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand,CommandError
from django.db import transaction
from products.models import Category,Product

CATEGORIES = [
    ('Electronics', None),
    ('Accessories', 'Electronics'),
    ('Home', None),
    ('Kitchen', 'Home'),
]

# name, description, price, stock, category
PRODUCTS = [
    ('Wireless Mouse', 'Ergonomic 2.4GHz mouse', '15.99', 50, 'Accessories'),
    ('Mechanical Keyboard', 'Hot-swappable, brown switches', '79.99', 20, 'Accessories'),
    ('USB-C Hub', '7-in-1 hub with HDMI', '34.50', 35, 'Accessories'),
    ('Noise-Cancelling Headphones', 'Over-ear, 30h battery', '129.00', 15, 'Electronics'),
    ('Webcam 1080p', 'Autofocus, built-in mic', '45.00', 25, 'Electronics'),
    ('Ceramic Mug', '350 ml, dishwasher safe', '8.50', 100, 'Kitchen'),
    ('Chef Knife', '20 cm stainless steel', '39.90', 12, 'Kitchen'),
    ('Desk Lamp', 'LED, adjustable brightness', '22.00', 40, 'Home'),
    ('Last One Left', 'Handy for testing the out-of-stock path', '10.00', 1, 'Home'),
    ('Sold Out Item', 'Stock is zero on purpose', '19.00', 0, 'Home'),
]


DEMO_PASSWORD = 'demo-pass-12345'  



class Command(BaseCommand):
    help="Laod sample categories, products and demo users for local development"

    def add_arguments(self, parser):
        parser.add_argument('--reset-stock',action='store_true',
                            help='Reset stock of seeded products to the seed values')
        parser.add_argument('--no-users',action='store_true',
                            help='Skip creating the demo admin and customer')


    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Refusing to seed data while DEBUG is False')


        categories = {}
        for name,parent_name in CATEGORIES:
            parent = categories.get(parent_name)
            categories[name], _=Category.objects.get_or_create(name=name,parent=parent)

        created=  updated = 0
        for name,desc, price, stock, cat in PRODUCTS:

            product, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'description':desc,
                    'price':Decimal(price),
                    'stock_qty':stock,
                    'category':categories[cat]
                }
            )

            if was_created:
                created+=1

            elif options['reset_stock'] and product.stock_qty != stock:
                product.stock_qty = stock
                product.save(update_fields=['stock_qty'])
                updated+=1

        self.stdout.write(f'Products: {created} created, {updated} stock reset')
        if not options['no_users']:
            self.seed_users()


    def seed_users(self):
        User = get_user_model()
        demo = [
                    ('admin_demo', 'admin_demo@example.com', {'is_staff': True, 'is_superuser': True}),
                    ('customer_demo', 'customer_demo@example.com', {}),
                ]

        for username,email,flags in demo:
            user,was_created = User.objects.get_or_create(
                username=username,defaults={'email':email
                                            ,**flags}
            )
            if was_created:
                user.set_password(DEMO_PASSWORD)
                user.save(update_fields=['password'])
                self.stdout.write(f'User created: {username} / {DEMO_PASSWORD}')
            else:
                self.stdout.write(f'User exists: {username} (password unchanged)')