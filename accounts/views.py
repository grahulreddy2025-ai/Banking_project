from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import transaction as db_transaction
from .models import BankAccount, Transaction
from .forms import RegisterForm, DepositForm, TransferForm
from django.http import HttpResponse


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Your card has been created.")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard_view(request):
    account      = request.user.bank_account
    transactions = account.transactions.all()[:10]
    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'transactions': transactions,
    })
'''@login_required
def dashboard_view(request):
    try:
        account = request.user.bank_account
    except Exception as e:
        return HttpResponse(f"Error: {e} — No bank account found for user: {request.user.username}")
    transactions = account.transactions.all()[:10]
    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'transactions': transactions,
    })'''


@login_required
def deposit_view(request):
    account = request.user.bank_account
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            with db_transaction.atomic():
                account.balance += amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    balance_after=account.balance,
                    description='Cash deposit',
                )
            messages.success(request, f"₹{amount} deposited successfully!")
            return redirect('dashboard')
    else:
        form = DepositForm()
    return render(request, 'accounts/deposit.html', {'form': form, 'account': account})


@login_required
def transfer_view(request):
    account = request.user.bank_account
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            receiver_card = form.cleaned_data['receiver_card']
            amount        = form.cleaned_data['amount']

            if receiver_card == account.card_number:
                messages.error(request, "You cannot transfer to your own account.")
            elif amount > account.balance:
                messages.error(request, "Insufficient balance.")
            else:
                receiver = BankAccount.objects.get(card_number=receiver_card)
                with db_transaction.atomic():
                    account.balance  -= amount
                    account.save()
                    receiver.balance += amount
                    receiver.save()
                    Transaction.objects.create(
                        account=account,
                        transaction_type='TRANSFER_OUT',
                        amount=amount,
                        balance_after=account.balance,
                        description=f'Transfer to {receiver.masked_card()}',
                    )
                    Transaction.objects.create(
                        account=receiver,
                        transaction_type='TRANSFER_IN',
                        amount=amount,
                        balance_after=receiver.balance,
                        description=f'Transfer from {account.masked_card()}',
                    )
                messages.success(request, f"₹{amount} transferred!")
                return redirect('dashboard')
    else:
        form = TransferForm()
    return render(request, 'accounts/transfer.html', {'form': form, 'account': account})


@login_required
def transactions_view(request):
    account      = request.user.bank_account
    transactions = account.transactions.all()
    return render(request, 'accounts/transactions.html', {
        'account': account,
        'transactions': transactions,
    })


@login_required
def close_account_view(request):
    if request.method == 'POST':
        account = request.user.bank_account
        account.is_active = False
        account.save()
        logout(request)
        messages.info(request, "Your account has been closed.")
        return redirect('login')
    return render(request, 'accounts/close_account.html')