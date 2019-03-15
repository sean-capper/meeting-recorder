from django.shortcuts import render, redirect, HttpResponse
from django.utils.safestring import mark_safe
from login.models import User
from .forms import CreateMeetingForm
import json

# Create your views here.
def home(request):
    create_meeting_form = CreateMeetingForm()
    return render(request, 'index.html', {
        'create_meeting': create_meeting_form,
    })

def meeting_room(request, room_name):
    return render(request, 'meetingroom.html', {
        'meeting_name': mark_safe(json.dumps(room_name))
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
    print(form)
    if(form.is_valid()):
        print(form.cleaned_data)
    else:
        print("form is invalid")
    return redirect('meeting:meeting-room', 'test')
