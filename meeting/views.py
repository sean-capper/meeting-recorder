from django.shortcuts import render, redirect, HttpResponse
from django.utils.safestring import mark_safe
from login.models import User
from meeting.models import Meeting, Relate
from .forms import CreateMeetingForm
import json

# Create your views here.
def home(request):
    create_meeting_form = CreateMeetingForm()
    return render(request, 'index.html', {
        'create_meeting': create_meeting_form,
    })

def meeting_room(request, meeting_url):
    return render(request, 'meetingroom.html', {
        'meeting_url': mark_safe(json.dumps(meeting_url))
    })

def autocomplete(request):
    if(request.GET['search'] is not ""):
        looking_for = request.GET['search']
    else:
        looking_for = '_'
    search_qs = User.objects.filter(email__startswith=looking_for)
    results = []
    for r in search_qs:
        results.append(r.email)
    resp = request.GET['callback'] + '(' + json.dumps(results) + ');'
    return HttpResponse(resp, content_type='application/json')

def create_meeting(request):
    form = CreateMeetingForm(request.POST or None)
    if(form.is_valid()):
        subject = form.cleaned_data['meeting_subject']
        descripton = form.cleaned_data['meeting_description']
        start_time = form.cleaned_data['meeting_starttime']
        organizer = request.user
        meeting = Meeting.create_meeting(subject=subject, descripton=descripton, start_time=start_time, organizer=organizer)
        meeting.save()
        
        # this will need to be a list of all invited members
        member = User.objects.get(email=form.cleaned_data['meeting_members'])
        
        # create the organizer in the Relate table
        organizer_relate = Relate.objects.create(user=organizer, meeting=meeting, role='ORGANIZER', status='PRESENT')
        # loop through invited members and create them in the Relate table
        relate = Relate.objects.create(user=member, meeting=meeting, role='MEMBER', status='INVITED')
        relate.save()
        print(meeting)
        return redirect('meeting:meeting-room', meeting.url)
    else:
        print("form is invalid")
        return render(request, 'index.html', {
            'create_meeting': form
        })
