import base64
from datetime import datetime
import pyotp

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests
from django.urls import reverse


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from .models import PhoneOTP, User
from .serializers import CreateUserSerializer, UserSerializer

# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"

# Time after which OTP will expire
EXPIRY_TIME = 300 # seconds (5  minutes)

class GenerateOTP(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def post(request):
        phone = request.data.get("phone_number", False)
        if phone:
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
            return Response({"OTP": OTP.now()}, status=status.HTTP_200_OK)  # Just for demonstration
        else:
            message = {
                        "message": "phone_number not recieved in POST request",
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):

    # This Method verifies the OTP
    @staticmethod
    def post(request):
        phone = request.data.get("phone_number", False)
        otp = request.data.get("otp", False)

        if phone and otp: 
            try:
                mobile = PhoneOTP.objects.get(mobile=phone)
            except ObjectDoesNotExist:
                return Response("User does not exist", status=404)  # False Call

            keygen = generateKey()
            key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
            OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model 
            if OTP.verify(otp):  # Verifying the OTP
                mobile.isVerified = True
                mobile.save()
                user = User.objects.filter(phone__iexact = phone)
                if user.exists():
                    response = requests.post(request.build_absolute_uri(reverse('token_obtain_pair')), data={'phone': phone, 'password': str(key) })
                    json_response = response.json()
                    return Response(json_response, status=200) 
                else:
                    temp_data = {'phone': phone, 'password': str(key) }

                    serializer = CreateUserSerializer(data=temp_data)
                    serializer.is_valid(raise_exception=True)
                    user = serializer.save()
                    user.save()

                    request.data.update({"password": str(key)})
                    TokenObtainPairView.as_view()(request)

                    message = {
                        "message": "User Created"
                    }
                    return Response(message, status=200)
            else:
                message = {
                    "message": "OTP is wrong/expired",
                }
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            message = {
                "message": "Either phone_number or otp not recieved in POST request",
            }
            return Response(message, status=status.HTTP_400_BAD_REQUEST)


class Register(APIView):

    '''Takes phone and a password and creates a new user only if otp was verified and phone is new'''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)

        if phone and password:
            phone = str(phone)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already have account associated. Kindly try forgot password'})
            else:
                old = PhoneOTP.objects.filter(phone__iexact = phone)
                if old.exists():
                    old = old.first()
                    if old.logged:
                        Temp_data = {'phone': phone, 'password': password }

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()

                        old.delete()
                        return Response({
                            'status' : True, 
                            'detail' : 'Congrats, user has been created successfully.'
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': 'Your otp was not verified earlier. Please go back and verify otp'

                        })
                else:
                    return Response({
                    'status' : False,
                    'detail' : 'Phone number not recognised. Kindly request a new otp with this number'
                })

        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or password was not recieved in Post request'
            })