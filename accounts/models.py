from django.db import models
from django.contrib.auth.models import User
import random


def generate_luhn_card():
    base = '400000' + str(random.randint(10000000, 99999999))
    digits = [int(x) for x in base]
    copy = digits[:]

    for i in range(len(copy)):
        if i % 2 == 0:
            copy[i] *= 2
        if copy[i] > 9:
            copy[i] -= 9

    total = sum(copy)
    check_digit = (10 - (total % 10)) % 10
    digits.append(check_digit)
    return ''.join(map(str, digits))


class BankAccount(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bank_account')
    card_number = models.CharField(max_length=20, unique=True)
    balance     = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    def masked_card(self):
        c = self.card_number
        return f"{c[:4]} **** **** {c[-4:]}"

    def __str__(self):
        return f"{self.user.username} - {self.card_number}"


class Transaction(models.Model):
    TYPES = [
        ('DEPOSIT',      'Deposit'),
        ('TRANSFER_OUT', 'Transfer Out'),
        ('TRANSFER_IN',  'Transfer In'),
    ]
    account          = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPES)
    amount           = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after    = models.DecimalField(max_digits=12, decimal_places=2)
    description      = models.CharField(max_length=255, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount}"
