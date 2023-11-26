from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect

from SMS.sms import SMSManager
from authentication.validators import validate_email, validate_phone
from .models import Account, Transaction
from .transactions import TransactionManager


@login_required
def profile(request):
    account = Account.objects.get(user=request.user)
    context = {
        'disabled': 'disabled',
        'account': account
    }
    return render(request, 'app/profile.html', context=context)


@login_required
def update_profile(request):
    user = request.user
    account = Account.objects.get(user=user)
    if request.method == "POST":
        user.first_name = request.POST['first-name']
        user.last_name = request.POST['last-name']
        account.sms_notifications = request.POST.get('sms_notifications', False) == 'on'
        if validate_email(request.POST['email'], request):
            user.email = request.POST['email']
        if validate_phone(request.POST['phone'], request):
            user.phone = request.POST['phone']
        user.save()
        account.save()
        # processing file
        file = request.FILES.get('img')
        if file:
            file_name = default_storage.save('images/'+file.name, file)
            file_ = default_storage.open(file_name)
            account.profile_image.save(file_name, file_)
        return redirect('user-profile')
    else:
        context = {
            'account': account
        }
        return render(request, 'app/profile.html', context=context)


@login_required
def create_transaction(request):
    user = request.user
    if request.method == "POST":
        sender = Account.objects.get(user=user)
        receiver = request.POST['receiver']
        amount = request.POST['amount']
        try:
            transaction = TransactionManager.transfer(sender, receiver, float(amount))
            if transaction.recipient.sms_notifications:
                SMSManager().transfer_message(transaction)
        except Exception as e:
            messages.add_message(request, messages.INFO, e)
        return redirect('create-transaction')
    else:
        receiver_options = Account.objects.exclude(user=user)
        context = {
            'receiver_options': receiver_options,
        }
        return render(request, 'app/create_transaction.html', context=context)


@login_required
def replenish(request):
    if request.method == "POST":
        account = Account.objects.get(user=request.user)
        try:
            amount = float(request.POST['amount'])
            TransactionManager.replenish(account, amount, request.POST['credentials'])
            messages.add_message(request, messages.INFO, "Successfully replenished for {}".format(request.POST['amount']))
            if account.sms_notifications:
                SMSManager().replenish_message(account, amount)
        except Exception as e:
            messages.add_message(request, messages.INFO, e)
        return redirect('replenish')
    else:
        return render(request, 'app/replenish.html')


@login_required
def transactions(request, transaction_type):
    account = Account.objects.get(user=request.user)
    if transaction_type == 'incoming':
        _transactions = Transaction.objects.filter(recipient=account)
    elif transaction_type == 'outgoing':
        _transactions = Transaction.objects.filter(sender=account)
    else:
        return HttpResponse('Page does not exist')
    context = {
        'transaction_type': transaction_type,
        'transactions': _transactions,
    }
    return render(request, 'app/transaction_list.html', context=context)
