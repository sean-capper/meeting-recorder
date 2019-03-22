from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages as session_message
from django.utils.safestring import mark_safe
from django.db import models
from login.models import User
from meeting.models import Meeting, Relate, Message, File
from .forms import CreateMeetingForm, JoinMeetingForm
import json

# Create your views here.
def home(request):
    create_meeting_form = CreateMeetingForm()
    join_meeting_form = JoinMeetingForm()
    return render(request, 'index.html', {
        'create_meeting': create_meeting_form,
        'join_meeting': join_meeting_form
    })

def meeting_room(request, meeting_url):
    try:
        user = User.objects.get(email=request.user)
    except models.ObjectDoesNotExist:
        user = None

    try:
        meeting = Meeting.objects.get(url=meeting_url)
    except models.ObjectDoesNotExist:
        meeting = None

    try:
        is_invited = Relate.objects.filter(user=user, meeting=meeting).exists()
    except models.ObjectDoesNotExist:
        is_invited = None

    # if the meeting exists, the user is logged in, and the user was invited to this specific meeting, return the meeting room view
    if(is_invited):
        return render(request, 'meetingroom.html', {
            'meeting_id': mark_safe(json.dumps(meeting.meeting_id)),
            'meeting_url': mark_safe(json.dumps(meeting_url))
        })
    # if the meeting does not exist, create a different error
    if(meeting is None):
        session_message.error(request, 'This meeting does not exist!')
    # otherwise, if the user is not logged in or not invited, create an error message
    elif(not is_invited):
        session_message.error(request, 'You were not invited to this meeting!')
    return redirect('meeting:home')

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
        
        # create the organizer in the Relate table
        organizer_relate = Relate.objects.create(user=organizer, meeting=meeting, role='ORGANIZER', status='PRESENT')
        
        # email_list is the raw input from the form
        email_list = form.cleaned_data['meeting_members'].strip(',').split(',')
        # member_list is the list of User objects from the DB
        member_list = []
        for member in email_list:
            try:
                member_list.append(User.objects.get(email=member))
            except models.ObjectDoesNotExist:
                member_list.append(None)
        
        # loop through invited members and create them in the Relate table
        for member in member_list:
            if(member):
                relate = Relate.objects.create(user=member, meeting=meeting, role='MEMBER', status='INVITED')
                relate.save()
            
        return redirect('meeting:meeting-room', meeting.url)
    else:
        print("form is invalid")
        return render(request, 'index.html', {
            'create_meeting': form
        })

def join_meeting(request):
    form = JoinMeetingForm(request.POST or None)
    if(form.is_valid()):
        url = form.cleaned_data['meeting_url']
        return redirect('meeting:meeting-room', url)
    
    return redirect('meeting:home')

def history(request):
    if(request.user.is_authenticated):
        meetings_list = Relate.objects.filter(user=request.user)
        print(meetings_list[0].meeting)
        return render(request, 'history.html', {
            'meetings_list': meetings_list,
        })
    else:
        return redirect('meeting:home')

def transcript(request, meeting_id):
    # if the user is signed in, and the user was invited or part of the requested meeting
    if(request.user.is_authenticated and Relate.objects.filter(user=request.user, meeting=meeting_id).exists()):
        message_list = Message.objects.filter(meeting_id=meeting_id).order_by('time')
        print(message_list)
        return render(request, 'transcript.html', {
            'meeting': Meeting.objects.get(pk=meeting_id),
            'message_list': message_list,
        })
    else:
        session_message.error(request, 'You were not invited to this meeting and cannot view the transcript!')
        return redirect('meeting:home')