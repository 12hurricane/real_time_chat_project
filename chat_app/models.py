from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import base64
import os

# Generate a key for encryption (In production, store this in environment variables)
# For this project, we'll use a hardcoded key for demonstration or generate one if not present
# But to ensure persistence across restarts, we should use a static key or load it.
# Here is a static key for demo purposes.
# You can generate a new one with: Fernet.generate_key()
ENCRYPTION_KEY = b'YourStaticFernetKeyForDemoPurposeOnly=' # This needs to be 32 url-safe base64-encoded bytes.
# Let's use a valid key:
ENCRYPTION_KEY = b'epj_J1L4s5zL3A7K5qT8xL9zR0aQ2wE4rT5yU7iO8p0=' 

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField() # Stores encrypted content
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Encrypt message before saving"""
        if self.content:
            cipher_suite = Fernet(ENCRYPTION_KEY)
            # If content is already bytes, use it, otherwise encode
            if isinstance(self.content, str):
                content_bytes = self.content.encode('utf-8')
            else:
                content_bytes = self.content
            
            # Encrypt
            encrypted_content = cipher_suite.encrypt(content_bytes)
            # Save as string
            self.content = encrypted_content.decode('utf-8')
        
        super().save(*args, **kwargs)

    @property
    def decrypted_content(self):
        """Decrypt message for display"""
        try:
            cipher_suite = Fernet(ENCRYPTION_KEY)
            decrypted_content = cipher_suite.decrypt(self.content.encode('utf-8'))
            return decrypted_content.decode('utf-8')
        except Exception as e:
            return "[Decryption Error]"
