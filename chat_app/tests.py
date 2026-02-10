from django.test import TestCase
from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from config.asgi import application
from chat_app.models import ChatRoom, Message
from chat_app import consumers, routing
import json
import time
import asyncio

class ChatIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.room = ChatRoom.objects.create(name='testroom')

    async def test_websocket_connection_and_auth(self):
        # We need to test the consumer directly or through routing
        # For Auth, we usually need to simulate a logged-in session, 
        # or we manually construct the scope with the user.
        
        # Construct the application with routing
        test_app = AuthMiddlewareStack(
            URLRouter(routing.websocket_urlpatterns)
        )
        
        # Connect to the room
        communicator = WebsocketCommunicator(test_app, f"/ws/chat/{self.room.name}/")
        
        # Mock the scope to include the user (Simulate authenticated user)
        communicator.scope['user'] = self.user
        
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        
        await communicator.disconnect()

class ChatFunctionalTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='userA', password='password')
        self.user_b = User.objects.create_user(username='userB', password='password')
        self.room = ChatRoom.objects.create(name='chat')

    async def test_user_a_sends_user_b_receives(self):
        # Application instance
        test_app = AuthMiddlewareStack(
            URLRouter(routing.websocket_urlpatterns)
        )

        # Connect User A
        communicator_a = WebsocketCommunicator(test_app, f"/ws/chat/{self.room.name}/")
        communicator_a.scope['user'] = self.user_a
        await communicator_a.connect()

        # Connect User B
        communicator_b = WebsocketCommunicator(test_app, f"/ws/chat/{self.room.name}/")
        communicator_b.scope['user'] = self.user_b
        await communicator_b.connect()

        # User A sends "Hello"
        message_data = {
            'type': 'chat_message',
            'message': 'Hello'
        }
        await communicator_a.send_json_to(message_data)

        # Receive Ack on A
        response_a = await communicator_a.receive_json_from()
        self.assertEqual(response_a['type'], 'ack')
        
        # Receive broadcast on A (A also receives it via group broadcast in our implementation)
        broadcast_a = await communicator_a.receive_json_from()
        self.assertEqual(broadcast_a['message'], 'Hello')

        # Receive broadcast on B
        broadcast_b = await communicator_b.receive_json_from()
        self.assertEqual(broadcast_b['message'], 'Hello')
        self.assertEqual(broadcast_b['username'], 'userA')

        await communicator_a.disconnect()
        await communicator_b.disconnect()

# Performance Stub
async def measure_latency():
    """
    Timestamps a sent message and calculates time until server receives it (ack).
    This is a standalone async function suitable for integration in load tests.
    """
    # Setup
    user = User.objects.create_user(username='latency_user', password='password')
    room = ChatRoom.objects.create(name='latency_room')
    
    test_app = AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
    communicator = WebsocketCommunicator(test_app, f"/ws/chat/{room.name}/")
    communicator.scope['user'] = user
    await communicator.connect()
    
    start_time = time.time()
    
    await communicator.send_json_to({
        'type': 'chat_message',
        'message': 'ping'
    })
    
    # Wait for ack
    response = await communicator.receive_json_from()
    
    end_time = time.time()
    latency = (end_time - start_time) * 1000 # ms
    
    print(f"Message Latency: {latency:.2f} ms")
    
    await communicator.disconnect()
    return latency
