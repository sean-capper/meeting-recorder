from django import forms
from login.models import User
from .models import Meeting, File

class CreateMeetingForm(forms.Form):
    meeting_subject = forms.CharField(label='Subject', max_length=50)
    meeting_description = forms.CharField(label='Description', max_length=100)
    meeting_starttime = forms.DateTimeField(label='Start Time', 
                                            widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                            input_formats=['%Y-%m-%dT%H:%M'])
    meeting_members = forms.CharField(label='Members')

class JoinMeetingForm(forms.Form):
    meeting_url = forms.CharField(label='URL', max_length=10)


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('user', 'meeting', 'file_source')