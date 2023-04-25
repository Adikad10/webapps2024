from django import forms
from register.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

CURRENCY_CHOICES = (
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('JPY', 'JPY'),
)


class SendMoneyForm(forms.Form):
    recipient_email = forms.EmailField()
    amount = forms.DecimalField(min_value=0.01)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)

    def clean_recipient_email(self):
        email = self.cleaned_data['recipient_email']
        try:
            recipient = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_('The recipient does not exist.'))
        return email


class RequestMoneyForm(forms.Form):
    sender_email = forms.EmailField()
    amount = forms.DecimalField(min_value=0.01)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)

    def clean_sender_email(self):
        email = self.cleaned_data['sender_email']
        try:
            sender = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_('The sender does not exist.'))
        return email
