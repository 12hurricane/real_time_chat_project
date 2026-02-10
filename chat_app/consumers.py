import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            username = self.scope['user'].username
            
            # Save message to database
            await self.save_message(username, self.room_name, message)

            # Send acknowledgement to the sender (Delivery Verification)
            await self.send(text_data=json.dumps({
                'type': 'ack',
                'status': 'Message saved',
                'message': message
            }))

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )
            
        elif message_type == 'typing':
            # Broadcast typing status
            username = self.scope['user'].username
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing',
                    'username': username,
                    'is_typing': text_data_json.get('is_typing', True)
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))

    # Receive typing event from room group
    async def typing(self, event):
        username = event['username']
        is_typing = event['is_typing']
        
        # Send typing status to WebSocket (exclude self if needed, handled in frontend usually, or here)
        # We'll just broadcast to all, frontend checks if it's me
        if username != self.scope['user'].username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': username,
                'is_typing': is_typing
            }))

    @database_sync_to_async
    def save_message(self, username, room_name, message_content):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(name=room_name)
        # Content is encrypted in the save() method of the model
        Message.objects.create(user=user, room=room, content=message_content)
