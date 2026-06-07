from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BankAccount, generate_luhn_card


def validate_luhn(card_number):
    num = card_number[::-1]
    digits = [int(x) for x in num]
    s1 = sum(digits[::2])
    for i in range(len(digits)):
        if i % 2 != 0:
            digits[i] *= 2
    for i in range(len(digits)):
        if digits[i] > 9:
            digits[i] -= 9
    s2 = sum(digits[1::2])
    return (s1 + s2) % 10 == 0


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name  = forms.CharField(max_length=50)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Auto-generate card when user registers
            card_number = generate_luhn_card()
            BankAccount.objects.create(user=user, card_number=card_number)
        return user


class DepositForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount'})
    )


class TransferForm(forms.Form):
    receiver_card = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '16-digit card number'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount'})
    )

    def clean_receiver_card(self):
        card = self.cleaned_data['receiver_card'].strip()
        if not validate_luhn(card):
            raise forms.ValidationError("Invalid card number.")
        if not BankAccount.objects.filter(card_number=card, is_active=True).exists():
            raise forms.ValidationError("This card does not exist.")
        return card