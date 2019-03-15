from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
import json

# Create your views here.
def home(request):
    return render(request, 'index.html')

def meeting_room(request, room_name):
    return render(request, 'meetingroom.html', {
        'meeting_name': mark_safe(json.dumps(room_name))
    })
