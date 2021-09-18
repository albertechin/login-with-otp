from django.urls import path
from .views import GenerateOTP

urlpatterns = [
    
    path("get_otp/", GenerateOTP.as_view(), name="get_otp"),

]