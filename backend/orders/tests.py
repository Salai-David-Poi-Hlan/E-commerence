from django.test import TestCase,TransactionTestCase
from threading import Barrier,Thread
from django.contrib.auth.models import User
from django.db import connection
from rest_framework.test import APIClient
from products.models import Product
from .models import Order
from .services import change_order_status,InvalidTransition

def make_client(user):
    client=APIClient()
    client.force_authenticate(user=user)
    return client

class OrderRulesTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('buyer',password='x')
        self.staff=User.objects.create_user('boss',password='x',is_staff=True)
        self.product=Product.objects.create(name='Mouse',price='10.00',stock_qty=3)
        self.client=make_client(self.user)

    def place_order(self,items,client=None):
        return (client or self.client).post(
            '/api/orders/',
            {'shipping_address':'Bangkok','items':items},
            format='json'
        )



    def test_cannot_order_more_than_stock(self):
        res=self.place_order([{'product':self.product.id,'quantity':5}])
        self.assertEqual(res.status_code,400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,3)
        self.assertEqual(Order.objects.count(),0)


    def test_duplication_lines_are_merged(self):
        res=self.place_order([
            {'product':self.product.id,'quantity':2},
            {'product':self.product.id,'quantity':2},
        ])
        self.assertEqual(res.status_code,400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,3)
        self.assertEqual(Order.objects.count(), 0)

    def test_failed_order_rolls_back_other_lines(self):
        other=Product.objects.create(name="Keyboard",price='50.00',stock_qty=1)
        res=self.place_order([
            {'product':self.product.id,'quantity':1},
            {'product':other.id,'quantity':9}
        ])
        self.assertEqual(res.status_code,400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,3)
        self.assertEqual(Order.objects.count(),0)

    def test_cancel_restores_stock_once(self):
        self.place_order([{'product':self.product.id,'quantity':2}])
        order=Order.objects.get()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,1)
        change_order_status(order.pk,'cancelled')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,3)
        with self.assertRaises(InvalidTransition):
            change_order_status(order.pk,'cancelled')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,3)

    

    def test_illegal_transition_return_409(self):
        self.place_order([{'product':self.product.id,'quantity':1}])
        order=Order.objects.get()
        change_order_status(order.pk,'paid')
        res=make_client(self.staff).post(
            f'/api/orders/{order.pk}/status/',{'status':'delivered'}
        )
        self.assertEqual(res.status_code,409)

    def test_customer_cannot_cancel_paid_order(self):
        self.place_order([{'product':self.product.id,'quantity':1}])
        order=Order.objects.get()
        change_order_status(order.pk,'paid')
        res=self.client.post(
            f'/api/orders/{order.pk}/status/',{'status':'cancelled'},format='json'
        )
        self.assertEqual(res.status_code,403)



def run_in_threads(funcs):
    barrier=Barrier(len(funcs))
    results=[None]* len(funcs)

    def worker(i,fn):
        try:
            barrier.wait()
            results[i]=fn()
        except Exception as e:
            results[i]=e
        finally:
            connection.close()
    threads=[Thread(target=worker,args=(i,fn)) for i,fn in enumerate(funcs)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.users=[User.objects.create_user(f'u{i}',password='x') for i in range(2)]
        self.product=Product.objects.create(name='Last item',price='10.00',stock_qty=1)

    def test_two_buyers_one_item_only_one_wins(self):
        def buy(user):
            def go():
                res=make_client(user).post(
                    '/api/orders/',
                    {'shipping_address':'Bangkok',
                      'items':[{'product':self.product.id,'quantity':1}]
                    },
                    format='json'
                )

                return res.status_code
            return go
        results=run_in_threads([buy(u) for u in self.users])
        self.assertEqual(
            sorted(r for r in results if isinstance(r,int)),[201,400])
        errors=[r for r in results if isinstance(r,Exception)]
        self.assertEqual(errors,[])
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,0)
        self.assertEqual(Order.objects.count(),1)
    




    def test_simultaneous_cancel_restores_stock_one(self):
        make_client(self.users[0]).post(
            '/api/orders/',
            {'shipping_address':'Bangkok','items':[{'product':self.product.id,'quantity':1}]},
            format='json',
        )

        order=Order.objects.get()
        

        results=run_in_threads([lambda: change_order_status(order.pk,'cancelled')]*2)


        successes=[r for r in results if isinstance(r,Order)]
        failures=[r for r in results if isinstance(r,InvalidTransition)]
        self.assertEqual((len(successes),len(failures)),(1,1))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,1)







# Create your tests here.
