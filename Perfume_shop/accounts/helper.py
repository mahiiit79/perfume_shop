from kavenegar import *
from Perfume_shop.settings import Kavenegar_API
from random import randint
import datetime
import time
from accounts.models import User


def send_otp(mobile,otp):
    mobile = [mobile, ]
    try:
        api = KavenegarAPI(Kavenegar_API)
        params = {
            'sender': '1000689696',  # optional
            'receptor': mobile,  # multiple mobile number, split by comma
            'message': 'Your OTP is {}'.format(otp),
        }
        response = api.sms_send(params)
        print('otp:', otp)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)

def get_random_otp():
    return randint(1000,9999)


def check_otp_expiration(mobile):
    try:
        user = User.objects.get(mobile=mobile)
        now = datetime.datetime.now()
        otp_time = user.otp_date
        diff_time = now - otp_time
        print('OTP TIME: ', diff_time)

        if diff_time.seconds > 120:
            return False
        return True

    except User.DoesNotExist:
        return False