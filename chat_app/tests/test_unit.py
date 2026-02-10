import os
import django
from django.conf import settings

# --- CRITICAL FIX START ---
# This must run BEFORE importing any django models
if not settings.configured:
    # Point this to your project's settings file
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
# --- CRITICAL FIX END ---

# Now it is safe to import Django modules
from django.test import TestCase
from django.contrib.auth.models import User
from chat_app.models import ChatRoom, Message
from chat_app.forms import SignUpForm, LoginForm

class ModelUnitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='unit_user', password='password')
        self.room = ChatRoom.objects.create(name='unit_room')

    def test_room_string_representation(self):
        """Test the string representation of the ChatRoom model."""
        self.assertEqual(str(self.room), 'unit_room')

    def test_message_creation_basic(self):
        """Test that a message can be created and linked to user/room."""
        msg = Message.objects.create(user=self.user, room=self.room, content="Test")
        self.assertEqual(msg.user.username, 'unit_user')
        self.assertEqual(msg.room.name, 'unit_room')

class FormUnitTests(TestCase):
    def test_signup_form_valid_data(self):
        """Test that the signup form accepts valid input."""
        form = SignUpForm(data={
            'username': 'newuser',
            'password': 'safe_password_123' 
        })
        self.assertTrue(form.is_bound)
        self.assertIn('username', form.fields)

    def test_login_form_valid_data(self):
        """Test login form validation."""
        User.objects.create_user(username='login_test', password='password')
        form = LoginForm(data={'username': 'login_test', 'password': 'password'})
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_data(self):
        """Test login form rejects wrong passwords."""
        User.objects.create_user(username='login_fail', password='password')
        form = LoginForm(data={'username': 'login_fail', 'password': 'WRONGpassword'})
        self.assertFalse(form.is_valid())