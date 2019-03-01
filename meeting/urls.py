from django.urls import path
from . import views

app_name="meeting"
urlpatterns = [
    path('', views.home, name='home'),
]