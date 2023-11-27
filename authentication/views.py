from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from app.models import Account
from SMS.sms import SMSManager
from authentication.validators import validate_account_data_register


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user-profile')
        else:
            messages.add_message(request, messages.INFO, "Wrong credentials")
            return redirect('login')
    else:
        return render(request, 'authentication/login.html')


def signup_user(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        username = request.POST['username']
        password = request.POST['password']
        confirmed_password = request.POST['confirm_password']
        if validate_account_data_register(first_name, last_name, phone, username, password, confirmed_password, request):
            user = User.objects.create_user(first_name=first_name,
                                            last_name=last_name,
                                            username=username,
                                            password=password)
            acc = Account.objects.get(user=user)
            acc.phone = phone
            acc.save()
            messages.add_message(request, messages.INFO, "Account successfully created")
            SMSManager().create_new_account_message(acc)

            return redirect('login')
        else:
            return redirect('signup')
    else:
        return render(request, 'authentication/signup.html')


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')

