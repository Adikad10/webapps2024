from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import HttpRequest


CONVERSION_RATES = {
    'USD': {'EUR': 0.85, 'GBP': 0.73},
    'EUR': {'USD': 1.18, 'GBP': 0.85},
    'GBP': {'USD': 1.38, 'EUR': 1.17},
}


@api_view(['GET'])
def conversion(request, currency1, currency2, amount_of_currency1):
    if currency1 not in CONVERSION_RATES or currency2 not in CONVERSION_RATES[currency1]:
        return JsonResponse({'error': 'Unsupported currency'}, status=status.HTTP_400_BAD_REQUEST)

    amount_of_currency1 = float(amount_of_currency1)
    conversion_rate = CONVERSION_RATES[currency1][currency2]
    converted_amount = amount_of_currency1 * conversion_rate

    return JsonResponse({
        'currency1': currency1,
        'currency2': currency2,
        'amount_of_currency1': amount_of_currency1,
        'conversion_rate': conversion_rate,
        'converted_amount': converted_amount,
    })


def get_converted_amount(amount, currency1, currency2):
    if currency1 == currency2:
        return amount

    if currency1 not in CONVERSION_RATES or currency2 not in CONVERSION_RATES[currency1]:
        print(f'Unsupported currency: currency1={currency1}, currency2={currency2}')
        raise ValueError('Unsupported currency')

    amount = float(amount)
    conversion_rate = CONVERSION_RATES[currency1][currency2]
    converted_amount = amount * conversion_rate

    return converted_amount


