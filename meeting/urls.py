from django.urls import path
from . import views

app_name="meeting"
urlpatterns = [
    path('', views.home, name='home'),
    path('meeting/room/<str:meeting_url>', views.meeting_room, name='meeting-room'),
    path('search.json', views.autocomplete, name='autocomplete'),
    path('create-meeting/', views.create_meeting, name='create-meeting'),

]