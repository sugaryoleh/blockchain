from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users-profile')
        else:
            messages.add_message(request, messages.INFO, "Wrong credentials")
            return redirect('login')
    else:
        return render(request, 'authentication/login.html')


def signup_user(request):
    pass

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')

