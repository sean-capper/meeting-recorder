# meeting/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from login.models import User
from meeting.models import Meeting, Relate, Message, File
import json
import datetime

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

        if(_type == 'chat_message'):
            userID = int(text_data_json['userID'])
            meetingID = int(text_data_json['meetingID'])
            message_text = text_data_json['message']
            timestamp = text_data_json['timestamp']
            file_source = text_data_json['file_source']
            
            user = User.objects.get(pk=userID)
            
            if(file_source):
                file_ = File.objects.get(file_source=file_source)
                file_extension = ('.' + file_.file_type) if file_.file_type is not None else ''
                file_name = "{}{}".format(file_.file_name, file_extension)
            else:
                file_name = None

            # save the message in the DB
            message = Message()
            message.user = User.objects.get(pk=userID)
            message.meeting = Meeting.objects.get(pk=meetingID)
            message.text = message_text
            message.attached_file_id = file_.file_id if file_source is not None else None
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
                    'file_source': file_source,
                    'file_name': file_name,
                }
            )
        elif(_type == 'start_meeting'):
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': _type,
                    'meeting_id': int(text_data_json['meetingID']),
                    'organizer': int(text_data_json['userID']),
                }
            )
        elif(_type == 'end_meeting'):
            meeting = Meeting.objects.get(pk=int(text_data_json['meetingID']))
            meeting.end_time = datetime.datetime.now()
            meeting.save()
            # send a message to all connected users that the meeting is ended
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': _type,
                    'meeting_id': int(text_data_json['meetingID']),
                    'organizer': int(text_data_json['userID']),
                }
            )

        elif(_type == 'refresh_timer'):
            meeting = Meeting.objects.get(pk=int(text_data_json['meetingID']))
            meeting.duration = str(text_data_json['timer'])
            meeting.save()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': _type,
                    'meeting_id': int(text_data_json['meetingID']),
                    'organizer': int(text_data_json['userID']),
                    'timer': text_data_json['timer']
                }
            )

    # Receive message from room group   
    def chat_message(self, event):
        _type = event['type']
        user_firstname = event['user_firstname']
        user_lastname = event['user_lastname']
        message = event['message']
        timestamp = event['timestamp']
        file_source = event['file_source']
        file_name = event['file_name']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': _type,
            'user_firstname': user_firstname,
            'user_lastname': user_lastname,
            'message': message,
            'timestamp': timestamp,
            'file_source': file_source,
            'file_name': file_name,
        }))
    
    def refresh_members_list(self, event):
        _type = event['type']
        members = event['members']
        self.send(text_data=json.dumps({
            'type': _type,
            'members': members
        }))

    def start_meeting(self, event):
        _type = event['type']
        meeting = event['meeting_id']
        organizer = event['organizer']
        self.send(text_data=json.dumps({
            'type': _type,
            'meeting': meeting,
            'organizer': organizer,
        }))

    def refresh_timer(self, event):
        _type = event['type']
        meeting = event['meeting_id']
        organizer = event['organizer']
        timer = event['timer']
        self.send(text_data=json.dumps({
            'type': _type,
            'meeting': meeting,
            'organizer': organizer,
            'timer': timer
        }))

    def end_meeting(self, event):
        _type = event['type']
        meeting = event['meeting_id']
        organizer = event['organizer']
        self.send(text_data=json.dumps({
            'type': _type,
            'meeting': meeting,
            'organizer': organizer,
        }))
