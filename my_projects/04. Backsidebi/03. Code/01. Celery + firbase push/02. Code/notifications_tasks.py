from django.conf import settings
from config.celery import app as celery_app

from firebase_admin import messaging, initialize_app, get_app, credentials


def get_g_app():
    cred = credentials.Certificate(settings.FIREBASE_APP_CREDENTIALS)
    try:
        return initialize_app(credential=cred)
    except:
        return get_app()


@celery_app.task
def send_notification(registration_token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ), token=registration_token,
    )
    messaging.send(message, app=get_g_app())


@celery_app.task
def send_notification_multicast(registration_tokens, title, body, data):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(),
        data=dict(
            data,
            title=title,
            body=body,
        ),
        tokens=registration_tokens,
    )
    messaging.send_multicast(message, app=get_g_app())
