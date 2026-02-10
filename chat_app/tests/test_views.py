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
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='existing').id)

    def test_login_view_get(self):
        """Test that the login page loads."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_logout_view(self):
        """Test logout functionality."""
        User.objects.create_user(username='outuser', password='password')
        self.client.login(username='outuser', password='password')
        
        response = self.client.get(reverse('logout'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        # Session should be empty/user id gone
        self.assertNotIn('_auth_user_id', self.client.session)

class RoomViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='chatuser', password='password')
        self.client.force_login(self.user)

    def test_index_view_create_room(self):
        """Test creating a room via the dashboard."""
        response = self.client.post(reverse('index'), {
            'room_name': 'python_zone'
        })
        self.assertEqual(response.status_code, 302) # Redirects to index or room
        self.assertTrue(ChatRoom.objects.filter(name='python_zone').exists())

    def test_room_view_loads(self):
        """Test that the room page loads correctly."""
        room = ChatRoom.objects.create(name='test_room')
        response = self.client.get(reverse('room', args=['test_room']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room.html')