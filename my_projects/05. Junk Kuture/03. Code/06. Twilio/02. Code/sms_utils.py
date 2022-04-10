import random

from django.conf import settings


def generate_sms_code():
    if settings.SMS_SERVICE_DEBUG:
        code = settings.SMS_DEBUG_CODE
    else:
        code = random.randrange(1000, 9999, 1)
    return code
