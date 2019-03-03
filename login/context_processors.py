from django.contrib.auth.forms import AuthenticationForm

def add_login_form(request):
    return {
        'login_form': AuthenticationForm(),
    }