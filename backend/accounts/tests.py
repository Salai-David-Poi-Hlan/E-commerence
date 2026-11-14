from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APITestCase


URL='/api/register/'
GOOD={'username':'alice','email':'Alice@Example.com','password':'c0rrect-horse-battery'}

class RegisterTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_success_creates_non_staff_user_with_hashed_password(self):
        res=self.client.post(URL,GOOD,format='json')
        self.assertEqual(res.status_code,201)
        self.assertNotIn('password',res.data)
        user=User.objects.get(username='alice')
        self.assertEqual(user.email,'alice@example.com')
        self.assertNotEqual(user.password,GOOD['password'])
        self.assertFalse(user.is_staff)

    def test_new_user_can_log_in(self):
        self.client.post(URL,GOOD,format='json')
        res=self.client.post('/api/token/',{
            'username':'alice','password':GOOD['password']
        },format='json')
        self.assertEqual(res.status_code,200)
        self.assertIn('access',res.data)

    def test_cannot_register_as_staff(self):
        self.client.post(URL,{**GOOD,'is_staff':True,'is_superuser':True},format='json')
        user=User.objects.get(username='alice')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_duplicate_username_is_case_insensitive(self):
        self.client.post(URL,GOOD,format='json')
        res=self.client.post(URL,{**GOOD,'username':'ALICE','email':'b@example.com'},format='json')
        self.assertEqual(res.status_code,400)
        self.assertIn('username',res.data)

    def test_duplicate_email_is_case_insensitive(self):
        self.client.post(URL,GOOD,format='json')
        res=self.client.post(URL,{**GOOD,'username':'bob','email':'ALICE@example.com'},format='json')
        self.assertEqual(res.status_code,400)
        self.assertIn('email',res.data)

    def test_weak_passwords_rejected(self):
        for pw in ['12345678','password','short1','alice123']:
            res=self.client.post(URL,{**GOOD,'password':pw},format='json')
            self.assertEqual(res.status_code,400,pw)
            self.assertIn('password',res.data)
        self.assertEqual(User.objects.count(),0)

    def test_stale_token_does_not_block_registration(self):
        res=self.client.post(URL,GOOD,format='json',HTTP_AUTHORIZATION='Bearer garbage')
        self.assertEqual(res.status_code,201)


class RefreshTests(APITestCase):
    def setUp(self):
        User.objects.create_user('alice',password='c0rrect-horse-battery')
        res=self.client.post('/api/token/',{
            'username':'alice','password':'c0rrect-horse-battery'
        },format='json')
        self.refresh=res.data['refresh']


    def refresh_with(self,token):

        return self.client.post('/api/token/refresh/',{'refresh':token})

    def test_refresh_rotates_and_old_token_dies(self):
        res=self.refresh_with(self.refresh)
        self.assertEqual(res.status_code,200)
        self.assertIn('access',res.data)
        self.assertNotEqual(res.data['refresh'],self.refresh)
        self.assertEqual(self.refresh_with(self.refresh).status_code,401)

    def test_blacklisted_token_cannot_refresh(self):
        self.client.post('/api/token/blacklist/',{'refresh':self.refresh},format='json')
        self.assertEqual(self.refresh_with(self.refresh).status_code,401)






    