import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from chat_app.models import ChatRoom, Message

class EncryptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sec_user', password='password')
        self.room = ChatRoom.objects.create(name='secret_room')

    def test_encryption_on_save(self):
        """Test that data is encrypted when saved to the DB."""
        original_text = "Secret Message"
        
        # 1. Save Message
        msg = Message.objects.create(user=self.user, room=self.room, content=original_text)
        
        # 2. Refresh from DB to see raw stored value
        msg.refresh_from_db()
        
        # 3. Verify it is Encrypted (Not equal to original, and ends with '=')
        self.assertNotEqual(msg.content, original_text)
        self.assertTrue(msg.content.endswith('=')) # Fernet padding

    def test_decryption_property(self):
        """Test that .decrypted_content returns the original text."""
        original_text = "Another Secret"
        msg = Message.objects.create(user=self.user, room=self.room, content=original_text)
        
        # Verify decryption works
        self.assertEqual(msg.decrypted_content, original_text)