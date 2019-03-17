from django import forms
from login.models import User
from .models import Meeting

class CreateMeetingForm(forms.Form):
    meeting_subject = forms.CharField(label='Subject', max_length=50)
    meeting_description = forms.CharField(label='Description', max_length=100)
    meeting_starttime = forms.DateTimeField(label='Start Time', 
                                            widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                            input_formats=['%Y-%m-%dT%H:%M'])
    meeting_members = forms.CharField(label='Members')
