from django.contrib import admin
from .models import User, Transaction, Request

admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Request)
