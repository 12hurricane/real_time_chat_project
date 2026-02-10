import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from chat_app.models import ChatRoom, Message

class ModelCoverageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='modeluser', password='password')
        self.room = ChatRoom.objects.create(name='modelroom')

    def test_chatroom_str(self):
        """Test the __str__ method of ChatRoom"""
        self.assertEqual(str(self.room), 'modelroom')

    def test_message_encryption_flow(self):
        """
        Create a message and verify 'save()' encrypts it 
        and 'decrypted_content' decrypts it.
        """
        original_text = "Secrets inside"
        
        # 1. Trigger .save() logic
        msg = Message.objects.create(user=self.user, room=self.room, content=original_text)
        
        # 2. Verify Database Layer (Encryption)
        msg.refresh_from_db()
        self.assertNotEqual(msg.content, original_text)
        self.assertTrue(msg.content.endswith('=')) # Fernet tokens end in =
        
        # 3. Verify Decryption Layer
        self.assertEqual(msg.decrypted_content, original_text)

    def test_save_handles_bytes_and_strings(self):
        """Test edge case where content might already be bytes"""
        # Directly creating a message object without saving yet
        msg = Message(user=self.user, room=self.room)
        # Manually set content as bytes to hit the 'if isinstance' else block in save()
        msg.content = b"ByteContent" 
        msg.save()
        
        msg.refresh_from_db()
        self.assertNotEqual(msg.content, "ByteContent")