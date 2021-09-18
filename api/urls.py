from django.urls import path
from .views import GenerateOTP, VerifyOTP

urlpatterns = [
    
    path("get_otp/", GenerateOTP.as_view(), name="get_otp"),
    path("verify_otp/", VerifyOTP.as_view(), name="view_otp"),

]