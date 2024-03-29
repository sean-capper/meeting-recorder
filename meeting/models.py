from django.db import models
from login.models import User
import random

# Create your models here.
class Meeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    subject = models.CharField(max_length=50)
    descripton = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, related_name='user_id_set', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='Relate', through_fields=('meeting', 'user'))
    url = models.CharField(max_length=128, default='DEFAULT', unique=True)
    duration = models.CharField(max_length=128, null=True)
    started = models.BooleanField(default=False, null=False)

    def __str__(self):
        return 'meeting/%s' % self.url

    @classmethod
    def create_meeting(cls, subject, descripton, start_time, organizer):
        meeting = cls(
            start_time = start_time,
            # end_time = start_time, # place holder will be updated when the actual meeting ends
            subject = subject,
            descripton = descripton,
            organizer = organizer,
            url = Meeting.generate_link()
        )
        return meeting

    def generate_link():
        link = ''
        characters = 'abcdefghijklmnopqrstuvwxyz0123456789'

        while(Meeting.objects.filter(url=link).exists() or link == ''):
            link = ''
            for x in range(10):
                link += characters[random.randint(0, characters.__len__()-1)]

        return link

class Relate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    role = models.CharField(max_length=15)
    status = models.CharField(max_length=15)

    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)


def get_upload_path(instance, filename):
    return '{}/{}'.format(instance.meeting.url, filename)

class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    # message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=15, null=True)
    file_source = models.FileField(upload_to=get_upload_path)
    date_created = models.TimeField(auto_now_add=True)


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attached_file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    timestamp = models.TimeField(auto_now_add=True)
    text = models.CharField(max_length=2000)