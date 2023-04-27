from django.urls import path
from . import views

urlpatterns = [
    # ... other URL patterns ...
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
