from django.urls import path
from . import views

app_name="meeting"
urlpatterns = [
    path('', views.home, name='home'),
    path('meeting/room/<str:room_name>', views.meeting_room, name='meeting-room'),
]