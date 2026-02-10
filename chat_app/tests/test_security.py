import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from chat_app.models import ChatRoom

class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_view_post_success(self):
        """Test that a user can sign up successfully."""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password_2': 'password123' # Django requires confirmation usually, but your form might be simple
        })
        # Should redirect to index upon success
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_view_get(self):
        """Test that the signup page loads."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_success(self):
        """Test that a user can login."""
        User.objects.create_user(username='existing', password='password')
        
        response = self.client.post(reverse('login'), {
            'username': 'existing',
            'password': 'password'
        })
        # Should redirect to index
        self.assertEqual(response.status_code, 302)
        self.assertEqual