from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages as session_message
from django.utils.safestring import mark_safe
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from login.models import User
from meeting.models import Meeting, Relate, Message, File
from .forms import CreateMeetingForm, JoinMeetingForm, FileForm
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

    if(meeting.end_time):
        session_message.error(request, 'This meeting has already ended! View the transcript via the history page.')
    else:
        # if the meeting exists, the user is logged in, and the user was invited to this specific meeting, return the meeting room view
        if(is_invited):
            return render(request, 'meetingroom.html', {
                'meeting_id': mark_safe(json.dumps(meeting.meeting_id)),
                'meeting_url': mark_safe(json.dumps(meeting_url)),
                'organizer_id': int(meeting.organizer_id),
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
         
        return render(request, 'history.html', {
            'meetings_list': meetings_list,
        })
    else:
        return redirect('meeting:home')

def transcript(request, meeting_id):
    # if the user is signed in, and the user was invited or part of the requested meeting
    if(request.user.is_authenticated and Relate.objects.filter(user=request.user, meeting=meeting_id).exists()):
        message_list = Message.objects.filter(meeting_id=meeting_id).order_by('timestamp')
         
        return render(request, 'transcript.html', {
            'meeting': Meeting.objects.get(pk=meeting_id),
            'message_list': message_list,
        })
    else:
        session_message.error(request, 'You were not invited to this meeting and cannot view the transcript!')
        return redirect('meeting:home')

def load_chat_history(request, meeting_url):
    meeting_id = int(request.GET['meeting_id'])
    messages_qs = Message.objects.filter(meeting=meeting_id).order_by('timestamp')
    messages = []
    for message in messages_qs:
        user = User.objects.get(pk=message.user_id)
        timestamp = message.timestamp.__str__()[0:5]
        hours = int(timestamp[0:2])
        if(hours > 12):
            hours -= 12
            timestamp = "%d:%s PM" % (hours, timestamp[3:])
        else:
            timestamp = '%s AM' % timestamp
        uf = File.objects.get(file_id=message.attached_file_id) if message.attached_file_id is not None else None
        if(uf):
            file_source = uf.file_source
            file_extension = ('.' + uf.file_type) if uf.file_type is not None else ''
            file_name = "{}{}".format(uf.file_name, file_extension)
        else:
            file_source = None
            file_name = None
        messages.append({
                'user_firstname': user.first_name,
                'user_lastname': user.last_name,
                'message': message.text,
                'timestamp': timestamp,
                'file_source': file_source.__str__(),
                'file_name': file_name
        })

    return HttpResponse(json.dumps(messages), content_type='application/json')


@csrf_exempt
def upload_file(request, meeting_url):
    form = FileForm(request.POST, request.FILES)
    if(form.is_valid()):
         
        uf = File()
        uf.user = form.cleaned_data['user']
        uf.meeting = form.cleaned_data['meeting']
        uf.file_source = form.cleaned_data['file_source']
        
        full_filename = form.cleaned_data['file_source'].__str__().split('.')
        file_name = full_filename[0]
        file_extension = full_filename[1] if len(full_filename) == 2 else None
        uf.file_name = file_name
        uf.file_type = file_extension
        uf.save()

    result = {'file_source': uf.file_source.__str__()}
    return HttpResponse(json.dumps(result), content_type='application/json')
