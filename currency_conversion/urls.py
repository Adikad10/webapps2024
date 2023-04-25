from django.urls import path
from . import views

urlpatterns = [
    path('conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', views.conversion),
]
