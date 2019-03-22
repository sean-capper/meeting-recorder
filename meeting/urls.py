from django.urls import path
from . import views

app_name="meeting"
urlpatterns = [
    path('', views.home, name='home'),
    path('create-meeting/', views.create_meeting, name='create-meeting'),
    path('join-meeting/', views.join_meeting, name='join-meeting'),
    path('m/<str:meeting_url>/', views.meeting_room, name='meeting-room'),
    path('search.json', views.autocomplete, name='autocomplete'),
    path('history/', views.history, name='history'),
    path('transcript/<int:meeting_id>/', views.transcript, name='transcript'),
]