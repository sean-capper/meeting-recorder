# meeting/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from login.models import User

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'meeting%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        userID = int(text_data_json['userID'])
        message = text_data_json['message']
        timestamp = text_data_json['timestamp']
        user = User.objects.get(pk=userID)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user_firstname': user.first_name,
                'user_lastname': user.last_name,
                'message': message,
                'timestamp': timestamp,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        user_firstname = event['user_firstname']
        user_lastname = event['user_lastname']
        message = event['message']
        timestamp = event['timestamp']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'user_firstname': user_firstname,
            'user_lastname': user_lastname,
            'message': message,
            'timestamp': timestamp,
        }))