from django import forms
from login.models import User

class CreateMeetingForm(forms.Form):
    meeting_subject = forms.CharField(label='Subject', max_length=50)
    meeting_description = forms.CharField(label='Description', max_length=100)
    meeting_starttime = forms.DateTimeField(label='Start Time')
    # meeting_members = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    meeting_members = forms.CharField()
