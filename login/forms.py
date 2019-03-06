from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm, UserChangeForm as DjangoUserChangeForm
from .models import User

class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
    
class UserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
 