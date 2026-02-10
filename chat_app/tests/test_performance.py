import time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from chat_app.models import ChatRoom, Message

class PerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user and room
        self.user = User.objects.create_user(username='perf_user', password='password')
        self.room = ChatRoom.objects.create(name='perf_room')
        self.client.force_login(self.user)

    def test_dashboard_load_speed(self):
        """
        Measure how long it takes to load the main dashboard.
        Target: Under 0.2 seconds (200ms).
        """
        start_time = time.time()
        
        response = self.client.get(reverse('index'))
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print the result so you can see it in the terminal
        print(f"\n    -> Dashboard Load Time: {duration:.4f} seconds")
        
        self.assertEqual(response.status_code, 200)
        # Fail if it takes longer than 0.2 seconds
        self.assertLess(duration, 0.2, "Dashboard is too slow!")

    def test_bulk_message_creation(self):
        """
        Measure the speed of encrypting and saving 100 messages.
        Target: Under 0.5 seconds.
        """
        start_time = time.time()
        
        # Simulate high traffic: Create 100 messages in a loop
        for i in range(100):
            Message.objects.create(
                user=self.user, 
                room=self.room, 
                content=f"Stress test message number {i}"
            )
            
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n    -> 100 Messages Encrypted & Saved in: {duration:.4f} seconds")
        
        # Fail if it takes longer than 0.5 seconds
        self.assertLess(duration, 0.5, "Database insertion is too slow!")