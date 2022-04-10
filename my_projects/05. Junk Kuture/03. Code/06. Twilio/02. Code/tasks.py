from django.conf import settings
from twilio.rest import Client

from config.celery import app as celery_app


@celery_app.task
def sending_sms(body, to):
    """
    body: string
    from_: number phone
    """
    if settings.SMS_SERVICE_DEBUG:
        return
    else:
        client = Client(settings.SMS_SERVICE_ACCOUNT_SID,
                        settings.SMS_SERVICE_AUTH_TOKEN)
        client.messages.create(
            body=body,
            from_=settings.SMS_SERVICE_FROM_SMS,
            to=to
        )


@celery_app.task
def send_chat_sms(body, to):
    """
    body: string
    to: number phone
    """
    if settings.SMS_CHAT_DEBUG:
        return
    else:
        client = Client(settings.SMS_SERVICE_ACCOUNT_SID,
                        settings.SMS_SERVICE_AUTH_TOKEN)
        client.messages.create(
            body=body,
            from_=settings.SMS_SERVICE_CHAT_PHONE_NUMBER,
            to=to
        )
