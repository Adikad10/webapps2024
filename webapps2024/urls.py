"""
URL configuration for webapps2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import  include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from register.views import get_user, add_user, add_transaction, add_request
from currency_conversion import views as cc_views
from payapp import views as pa_views
from authapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_user/', add_user, name='add_user'),
    path('get_user/', get_user, name='get_user'),
    path('authapp/', include('authapp.urls')),
    path('', views.login_view, name='home'),
    path('baseURL/', include('currency_conversion.urls')),
    path('conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', cc_views.conversion),
    path('dashboard/', pa_views.dashboard, name='dashboard'),
    path('register/', include('register.urls')),
]
