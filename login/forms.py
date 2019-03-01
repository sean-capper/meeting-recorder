from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CreateUserForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('email', 'password')
    
class ChangeUserForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = User
        fields = ('email', 'password')
 