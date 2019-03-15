from django.db import models
from login.models import User

# Create your models here.
class Meeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    subject = models.CharField(max_length=50)
    descripton = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, related_name='user_id_set', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='Relate')
    url = models.CharField(max_length=128, default='DEFAULT')

class Relate(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15)
    status = models.CharField(max_length=15)

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)

class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100)
    file_type = models.CharField(max_length=15)
    file_source = models.FileField(upload_to='files/')
    date_created = models.DateTimeField(auto_now_add=True)


