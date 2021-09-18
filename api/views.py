from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import pyotp
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PhoneOTP
import base64


# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"

class GenerateOTP(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def post(request):
        phone = request.data["phone_number"]
        try:
            mobile = PhoneOTP.objects.get(mobile=phone)  # if mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            PhoneOTP.objects.create(
                mobile=phone,
            )
            mobile = PhoneOTP.objects.get(mobile=phone)  # user Newly created Model
        mobile.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model for OTP is created
        print(f'Generated OTP for {phone}: {OTP.now()}')
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        return Response({"OTP": OTP.now()}, status=200)  # Just for demonstration
