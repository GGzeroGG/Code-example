from django.conf import settings
from django.utils import timezone

from firebase_admin import credentials, get_app, initialize_app, messaging

from oauth2_provider.admin import AccessToken

from apps.users.models import Device


class FirebaseNotification:
    def get_g_app(self):
        cred = credentials.Certificate(settings.FIREBASE_APP_CREDENTIALS)
        try:
            return initialize_app(credential=cred)
        except: # noqa
            return get_app()

    def user_registration_tokens(self, user_id: int):
        """
        Takes the User id and searches for all active devices
        """
        registration_tokens = None
        current_time = timezone.now()

        access_tokens = AccessToken.objects.filter(
            user_id=user_id,
            expires__gt=current_time,
        )
        if access_tokens.exists():
            registration_tokens = Device.objects.filter(
                auth_token__in=access_tokens.values_list('id', flat=True),
            ).exclude(
                firebase_token=None,
            ).values_list('firebase_token', flat=True)

        return registration_tokens

    def users_registration_tokens(self, user_ids: list):
        """
        Takes a list of user id's and searches for all active devices
        """
        registration_tokens = None
        current_time = timezone.now()

        access_tokens = AccessToken.objects.filter(
            user_id__in=user_ids,
            expires__gt=current_time,
        )
        if access_tokens.exists():
            registration_tokens = Device.objects.filter(
                auth_token__in=access_tokens.values_list('id', flat=True),
            ).exclude(
                firebase_token=None,
            ).values_list('firebase_token', flat=True)

        return registration_tokens

    def user_send_multicast(self, title: str, body: str, user_id: int,
                            data=None):
        """
        Sends push notifications to user in firebase
        """
        if data:
            data = self._changing_data_to_str(data=data)
        registration_tokens = self.user_registration_tokens(user_id=user_id)
        if registration_tokens:
            message = messaging.MulticastMessage(
                data=data,
                notification=messaging.Notification(title=title, body=body),
                tokens=list(registration_tokens),
            )
            messaging.send_multicast(message, app=self.get_g_app())

    def users_send_multicast(self, title: str, body: str, user_ids: list,
                             data=None):
        """
        Sends push notifications to user in firebase
        """
        if data:
            data = self._changing_data_to_str(data=data)
        registration_tokens = self.users_registration_tokens(user_ids=user_ids)
        if registration_tokens:
            message = messaging.MulticastMessage(
                data=data,
                notification=messaging.Notification(title=title, body=body),
                tokens=list(registration_tokens),
            )
            messaging.send_multicast(message, app=self.get_g_app())

    def _changing_data_to_str(self, data):
        """
        Gets the dictionary and changes the key type to a string
        """
        for field in data:
            data[field] = str(data[field])
        return data
