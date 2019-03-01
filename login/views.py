from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from .forms import UserCreationForm, UserChangeForm

# Create your views here.
def login(request):
    form = AuthenticationForm()
    if(request.user.is_authenticated):
        return redirect(request.session['login_from'])
    elif(request.POST):
        form = AuthenticationForm(data=request.POST)
        if(form.is_valid()):
            user = form.get_user()
            auth_login(request, user)
            print(request.session['login_from'])
            if('login' not in request.session['login_from']):
                return redirect(request.session['login_from'])
            else:
                return redirect('blog:index')
    else:
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')

    return render(request, 'login.html', {
        'form': form,
    })

def logout(request):
    auth_logout(request)
    # return to the previous
    return redirect(request.META.get('HTTP_REFERER', '/'))