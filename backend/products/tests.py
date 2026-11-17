from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from .models import Product



@override_settings(DEBUG=True)
class SeedCommandTests(TestCase):


    def test_second_run_creates_nothing_new(self):
        call_command('seed_dev_data', verbosity=0)
        count=Product.objects.count()
        call_command('seed_dev_data', verbosity=0)
        self.assertEqual(Product.objects.count(),count)
        self.assertEqual(get_user_model().objects.filter(username='admin_demo').count(),1)


    def test_rerun_does_not_overwrite_stock_unless_asked(self):
        call_command('seed_dev_data', verbosity=0)
        Product.objects.filter(name='Wireless Mouse').update(stock_qty=3)
        call_command('seed_dev_data', verbosity=0)
        self.assertEqual(Product.objects.get(name='Wireless Mouse').stock_qty,3)
        call_command('seed_dev_data', '--reset-stock',verbosity=0)
        self.assertEqual(Product.objects.get(name='Wireless Mouse').stock_qty,50)

    def test_demo_admin_is_staff_and_can_log_in(self):
        call_command('seed_dev_data', verbosity=0)
        user = get_user_model().objects.get(username='admin_demo')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password('demo-pass-12345'))

    def test_no_users_flag(self):
        call_command('seed_dev_data', '--no-users',verbosity=0)
        self.assertFalse(get_user_model().objects.filter(username='admin_demo').exists())


    @override_settings(DEBUG=False)
    def test_refuses_to_run_in_production_mode(self):
        with self.assertRaises(CommandError):
            call_command('seed_dev_data', verbosity=0)
        self.assertEqual(Product.objects.count(),0)










    