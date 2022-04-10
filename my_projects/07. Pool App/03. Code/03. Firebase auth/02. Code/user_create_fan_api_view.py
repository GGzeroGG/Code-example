from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings

from apps.auth_core.choices import UserType
from apps.auth_core.models import User
from apps.profile.models import Wallet
from apps.profile.models.profile import Profile
from services.api.permission_classes import SignedAPIRequestPermission
from services.api.serializers.registrations.user_create_fan import \
    UserCreateFanSerializer
from services.api.swagger.docs.registrations.user_create_fan import \
    doc_decorator
from services.firebase.utils import get_firebase_uid


@method_decorator(name='post', decorator=doc_decorator)
class UserCreateFanView(GenericAPIView):
    """
    An api for creating a fan account
    Main fields email and id_token
    Firebase_uid will be extracted from the id_token
    """
    serializer_class = UserCreateFanSerializer
    permission_classes = (SignedAPIRequestPermission,)
    authentication_classes = ()
    error_messages = {
        'not_firebase_uid': _('api_errors:invalid_firebase_token'),
        'not_authorization_header': _(
            'api_errors:authorization_header_was_not_provided',
        ),
        'registration_on_same_device': _(
            'api_errors:another_user_have_registered_on_same_device',
        )
    }

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        authorization_header = request.META.get('HTTP_AUTHORIZATION', '')

        # If the header is not passed or the front is incorrect error 401
        if (not authorization_header or
                not authorization_header.startswith('Firebase ')):
            return Response({
                'detail':
                    self.error_messages['not_authorization_header'],
            }, status=status.HTTP_401_UNAUTHORIZED)

        id_token = authorization_header.split('Firebase ').pop()
        firebase_uid = get_firebase_uid(id_token=id_token)

        # If you cannot get firebase_uid by id_token then the token is invalid
        # or the user is not in the firebase application
        if firebase_uid is None:
            return Response({
                'detail': self.error_messages['not_firebase_uid'],
            }, status=status.HTTP_401_UNAUTHORIZED)

        registration_on_same_device = User.objects.filter(
            registration_device=serializer.validated_data['registration_device']  # noqa: E501
        )
        if registration_on_same_device.exists():
            return Response({
                api_settings.NON_FIELD_ERRORS_KEY: [
                    self.error_messages['registration_on_same_device'],
                ]
            }, status=status.HTTP_409_CONFLICT)

        profile_data = serializer.validated_data.pop('profile')

        user = User.objects.create_user(
            type=UserType.FAN.value, firebase_uid=firebase_uid,
            **serializer.validated_data,
        )
        Profile.objects.create(user_id=user.id, **profile_data)
        Wallet.objects.create(user_id=user.id, amount=0, hold=0)

        return Response(status=status.HTTP_201_CREATED)
