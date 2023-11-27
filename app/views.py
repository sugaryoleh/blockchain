from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect

from SMS.sms import SMSManager
from authentication.validators import validate_account_data_register, validate_account_data_update
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
        if not validate_account_data_update(first_name=request.POST['first_name'], last_name=request.POST['last_name'],
                                            email=request.POST['email'], phone=request.POST['phone'], request=request):
            return redirect(request.path_info)
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        account.sms_notifications = request.POST.get('sms_notifications', False) == 'on'
        user.email = request.POST['email']
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
def transactions(request, transaction_type="incoming"):
    account = Account.objects.get(user=request.user)
    if transaction_type == 'incoming':
        _transactions = Transaction.objects.filter(recipient=account)
    elif transaction_type == 'outgoing':
        _transactions = Transaction.objects.filter(sender=account)
    else:
        return HttpResponse('Page does not exist')

    user = request.user
    if request.method == "POST":
        sender = Account.objects.get(user=user)
        receiver = request.POST['receiver']
        amount = request.POST['amount']
        try:
            transaction = TransactionManager.transfer(sender, receiver, int(amount))
            if transaction.recipient.sms_notifications:
                SMSManager().transfer_message(transaction)
        except Exception as e:
            messages.add_message(request, messages.INFO, e)
        return redirect(request.path_info)
    else:
        context = {
            'transaction_type': transaction_type,
            'transactions': _transactions,
        }
        return render(request, 'app/transactions.html', context=context)


@login_required
def replenish(request):
    if request.method == "POST":
        account = Account.objects.get(user=request.user)
        try:
            amount = int(request.POST['amount'])
            TransactionManager.replenish(account, amount, request.POST['credentials'])
            messages.add_message(request, messages.INFO, "Successfully replenished for {}".format(request.POST['amount']))
            if account.sms_notifications:
                SMSManager().replenish_message(account, amount)
        except Exception as e:
            messages.add_message(request, messages.INFO, e)
        return redirect('replenish')
    else:
        return render(request, 'app/replenish.html')
