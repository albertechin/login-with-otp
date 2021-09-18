from django.contrib import admin
from .models import User, PhoneOTP
# Register your models here.

admin.site.register(User)
admin.site.register(PhoneOTP)
