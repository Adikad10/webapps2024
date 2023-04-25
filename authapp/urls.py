from django.urls import path
from . import views

app_name = 'authapp'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('send_money/', views.send_money_view, name='send_money'),
    path('request_money', views.request_money_view, name= 'request_money'),
    path('approve_money_request/', views.approve_money_request, name='approve_money_request'),
    path('reject_money_request/', views.reject_money_request, name='reject_money_request'),
    ]
