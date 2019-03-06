from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from .forms import UserCreationForm, UserChangeForm

# Create your views here.
def login(request):
    form = AuthenticationForm()
    if(request.user.is_authenticated):
        return redirect(request.path_info)
    elif(request.POST):
        form = AuthenticationForm(data=request.POST)
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
        if(form.is_valid()):
            user = form.get_user()
            auth_login(request, user)
            if('login' not in request.session['login_from']):
                return redirect(request.session['login_from'])
            else:
                return redirect('meeting:home')
    else:
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')

    return render(request, 'login.html', {
        'form': form,
    })

def logout(request):
    auth_logout(request)
    # return to the previous
    return redirect(request.META.get('HTTP_REFERER', '/'))

def register(request):
    form = UserCreationForm(request.POST or None)
    if(request.user.is_authenticated):
        return redirect('meeting:home')
    elif(request.POST):
        if(form.is_valid()):
            form.save()
            return redirect('login:login')
    return render(request, 'register.html', {
        'create_user': form,
    })