from django.test import TestCase,TransactionTestCase
from threading import Barrier,Thread
from accounts.models import User
from django.db import connection
from rest_framework.test import APIClient
from products.models import Product
from .models import Order
from .services import change_order_status,InvalidTransition
from unittest.mock import patch
import stripe
from datetime import timedelta
from django.core.management import call_command
from django.utils import timezone


def make_client(user):
    client=APIClient()
    client.force_authenticate(user=user)
    return client


class OrderRulesTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('buyer',email='buyer@example.com',password='x')
        self.staff=User.objects.create_user('boss',email='boss@example.com',password='x',is_staff=True)
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
        self.users=[User.objects.create_user(f'u{i}',email=f'u{i}@example.com',password='x') for i in range(2)]
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



class WebhookTests(TestCase):
    def setUp(self):
        user=User.objects.create_user('buyer',email='buyer@example.com',password='x')
        product=Product.objects.create(name='Mouse',price='10.00',stock_qty=3)
        make_client(user).post('/api/orders/',{
            'shipping_address':'Bangkok',
            'items':[{'product':product.id,'quantity':1}],
        },format='json')
        self.order=Order.objects.get()
    

    def event(self,payment_status='paid'):
        return stripe.Event.construct_from({
            'id':'evt_test',
            'object':'event',
            'type':'checkout.session.completed',
            'data':{
                'object':{
                    'id':'cs_test_123',
                    'object':'checkout.session',
                    'payment_status':payment_status,
                    'metadata':{'order_id':str(self.order.pk)}
                }
            }
        },'sk_test_x')

    def post(self):
        return self.client.post('/api/stripe/webhook/',data='{}',content_type='application/json',HTTP_STRIPE_SIGNATURE='x')

    @patch('orders.views.stripe.Webhook.construct_event')
    def test_paid_event_marks_order_paid(self,construct):
        construct.return_value=self.event()
        self.assertEqual(self.post().status_code,200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'paid')
        self.assertIsNotNone(self.order.paid_at)

    @patch('orders.views.stripe.Webhook.construct_event')
    def test_duplicate_delivery_is_harmless(self,construct):
        construct.return_value=self.event()
        self.post()
        self.order.refresh_from_db()
        first_paid_at=self.order.paid_at
        self.assertEqual(self.post().status_code,200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid_at,first_paid_at)


    @patch('orders.views.stripe.Webhook.construct_event')
    def test_unpaid_session_does_not_mark_paid(self,construct):
        construct.return_value=self.event('unpaid')
        self.post()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'pending')


    def test_bad_signature_rejected(self):
        self.assertEqual(self.post().status_code,400)


    @patch('orders.views.stripe.Webhook.construct_event')
    def test_missing_metadata_return_200(self,construct):
        ev=self.event()
        ev['data']['object']['metadata']={}
        construct.return_value=ev
        self.assertEqual(self.post().status_code,200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'pending')




class ExpireCommandTests(TestCase):

    def setUp(self):
        user=User.objects.create_user('buyer',email='buyer@example.com',password='x')
        self.product= Product.objects.create(name='Mouse',price='10.00',stock_qty=3)
        make_client(user).post('/api/orders/',{
            'shipping_address':"Bangkok",
            'items':[{'product':self.product.id,'quantity':2}]
        },format='json')

        self.order=Order.objects.get()

    def age(self,minutes):
        Order.objects.filter(pk=self.order.pk).update(
            created_at=timezone.now() - timedelta(minutes=minutes)
        )

    def stock(self):
        self.product.refresh_from_db()
        return self.product.stock_qty
    

    def test_old_pending_order_is_cancelled_and_stock_restored(self):
        self.assertEqual(self.stock(),1) 
        self.age(60)
        call_command('expire_pending_orders')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'cancelled')
        self.assertEqual(self.stock(),3)    


    def test_recent_pending_order_is_untouched(self):
        self.age(5)
        call_command('expire_pending_orders')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'pending')
        self.assertEqual(self.stock(),1)

    def test_paid_order_is_never_expired(self):
        change_order_status(self.order.pk,'paid')
        self.age(60)
        call_command('expire_pending_orders')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'paid')

    def test_guard_blocks_cancel_id_paid_in_the_meantime(self):
        change_order_status(self.order.pk,'paid')
        with self.assertRaises(InvalidTransition):
            change_order_status(self.order.pk,'cancelled',expected_status='pending')
        self.assertEqual(self.stock(),1) 


class OrderHistoryTests(TestCase):
    def setUp(self):
        self.alice=User.objects.create_user("alice",email='alice@example.com',password='x')
        self.bob= User.objects.create_user("bob",email="bob@example.com",password='x')
        self.staff=User.objects.create_user('bosss',email='boss@example.com',password='x',is_staff=True)
        self.product=Product.objects.create(name='Mouse',price='10.00',stock_qty=5)

        make_client(self.alice).post('/api/orders/',{
            'shipping_address':'Bangkok',
            'items':[{'product':self.product.id,'quantity':2}]
        },format='json')

        self.order=Order.objects.get()


    def test_list_returns_only_own_orders(self):
        self.assertEqual(len(make_client(self.alice).get('/api/orders/').data),1) 
        self.assertEqual(len(make_client(self.bob).get('/api/orders/').data),0)


    def test_staff_list_is_personal_unless_scope_all(self):
        staff=make_client(self.staff)
        self.assertEqual(len(staff.get('/api/orders/').data),0)
        self.assertEqual(len(staff.get('/api/orders/?scope=all').data),1)

    def test_customer_can_cancel_own_pending_order_and_stock_returns(self):
        res=make_client(self.alice).post(
            f'/api/orders/{self.order.pk}/status/',{'status':'cancelled'},format='json'
        )
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.data['status'],'cancelled')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty,5)



    def test_cannot_cancel_someone_else_order(self):
        res=make_client(self.bob).post(
            f'/api/orders/{self.order.pk}/status/',{'status':'cancelled'},format='json'
        )
        self.assertEqual(res.status_code,404)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'pending')

    def test_list_includes_items(self):
        data=make_client(self.alice).get('/api/orders/').data
        self.assertEqual(data[0]['items'][0]['product_name'],'Mouse')

class AdminOrderTests(TestCase):

    def setUp(self):
        self.alice=User.objects.create_user("alice",email='alice@example.com',password='x')
        self.staff=User.objects.create_user('bosss',email='boss@example.com',password='x',is_staff=True)
        self.product=Product.objects.create(name='Mouse',price='10.00',stock_qty=5)
    
        make_client(self.alice).post('/api/orders/',{
                'shipping_address':'Bangkok',
                'items':[{'product':self.product.id,'quantity':1}]
            },format='json')
    
        self.order=Order.objects.get()
        self.admin=make_client(self.staff)


    def test_scope_all_is_forbidden_for_customers(self):
        res=make_client(self.alice).get('/api/orders/?scope=all')
        self.assertEqual(res.status_code,403)

    def test_staff_sees_everyones_orders_with_customer_name(self):
        data=self.admin.get('/api/orders/?scope=all').data
        self.assertEqual(len(data),1)
        self.assertEqual(data[0]['customer'],'alice')

    def test_status_filter(self):
        self.assertEqual(len(self.admin.get('/api/orders/?scope=all&status=paid').data),0)
        self.assertEqual(len(self.admin.get('/api/orders/?scope=all&status=pending').data),1)

    def test_staff_cannot_mark_paid_through_api(self):
        res=self.admin.post(f'/api/orders/{self.order.pk}/status/',{'status':'paid'},format='json')
        self.assertEqual(res.status_code,403)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status,'pending')

    def test_staff_can_ship_then_deliver_a_paid_order(self):
        change_order_status(self.order.pk,'paid')
        url=f'/api/orders/{self.order.pk}/status/'
        self.assertEqual(self.admin.post(url,{'status':'shipped'},format='json').status_code,200)
        res=self.admin.post(url,{'status':'delivered'},format='json')
        self.assertEqual(res.data['status'],'delivered')
        self.assertEqual(res.data['next_statuses'],[])


    def test_next_statuses_reflect_state_machine(self):
        data=self.admin.get('/api/orders/?scope=all').data
        self.assertEqual(data[0]['next_statuses'],['cancelled','paid'])

    def test_me_endpoint(self):
        self.assertTrue(self.admin.get('/api/me/').data['is_staff'])
        self.assertFalse(make_client(self.alice).get('/api/me/').data['is_staff'])









    










# Create your tests here.
