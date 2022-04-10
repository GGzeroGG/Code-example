from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from apps.auth_core.choices import UserType
from apps.auth_core.models import User
from services.firebase.utils import get_firebase_app, get_firebase_uid


class FirebaseAuthentication(BaseAuthentication):
    def __init__(self):
        self._app = get_firebase_app()

    def authenticate_header(self, request):
        return 'Firebase realm="api"'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if auth_header is None or 'Firebase' not in auth_header:
            return None

        # Checking token validity
        id_token = auth_header.split('Firebase ').pop()

        firebase_uid = get_firebase_uid(id_token=id_token, app=self._app)

        if not firebase_uid:
            msg = _('api_errors:invalid_auth_token')
            raise exceptions.AuthenticationFailed(msg)

        user = User.objects.filter(firebase_uid=firebase_uid,
                                   type=UserType.FAN.value).first()

        if user is None:
            msg = _('api_errors:user_does_not_exist')
            raise exceptions.AuthenticationFailed(msg)

        return user, None
