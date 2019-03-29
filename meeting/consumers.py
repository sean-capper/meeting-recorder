# meeting/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from login.models import User
from meeting.models import Meeting, Relate, Message, File

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'meeting%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        # when a user connects to the meeting, update their status in the DB
        user = User.objects.get(email=self.scope['user'])
        meeting = Meeting.objects.get(url=self.room_name)
        relate = Relate.objects.get(user=user, meeting=meeting)
        relate.status = 'PRESENT'
        relate.save()

        # send message to all members in group the new list of present members in chat
        members_qs = Relate.objects.filter(meeting=meeting, status='PRESENT')
        members = []
        for member in members_qs:
            members.append(member.__str__())

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh_members_list',
                'members': members
            }
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        user = User.objects.get(email=self.scope['user'])
        meeting = Meeting.objects.get(url=self.room_name)
        relate = Relate.objects.get(user=user, meeting=meeting)
        relate.status = 'ATTENDED'
        relate.save()

        # send message to all members in group the new list of present members in chat
        members_qs = Relate.objects.filter(meeting=meeting, status='PRESENT')
        members = []
        for member in members_qs:
            members.append(member.__str__())
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'refresh_members_list',
                'members': members
            }
        )
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        _type = text_data_json['type']
        userID = int(text_data_json['userID'])
        meetingID = int(text_data_json['meetingID'])
        message_text = text_data_json['message']
        timestamp = text_data_json['timestamp']
        user = User.objects.get(pk=userID)


        # save the message in the DB
        message = Message()
        message.user = User.objects.get(pk=userID)
        message.meeting = Meeting.objects.get(pk=meetingID)
        message.text = message_text
        # message.timestamp = timestamp
        message.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user_firstname': user.first_name,
                'user_lastname': user.last_name,
                'message': message_text,
                'timestamp': timestamp,
            }
        )

    # Receive message from room group   
    def chat_message(self, event):
        _type = event['type']
        user_firstname = event['user_firstname']
        user_lastname = event['user_lastname']
        message = event['message']
        timestamp = event['timestamp']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': _type,
            'user_firstname': user_firstname,
            'user_lastname': user_lastname,
            'message': message,
            'timestamp': timestamp,
        }))

    def refresh_members_list(self, event):
        _type = event['type']
        members = event['members']
        self.send(text_data=json.dumps({
            'type': _type,
            'members': members
        }))