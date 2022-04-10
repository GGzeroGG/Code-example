from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AccessToken, RefreshToken

from oauthlib.common import generate_token

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.api.serializers.auth.sign_up import SignUpSerializer
from services.api.swagger.docs import sign_up as sign_up_doc

from apps.main.choices import Flow, PhoneVerificationStatus
from apps.main.models.phone_verification import PhoneVerification
from apps.users.models.user import User


class SignUpView(APIView):
    permission_classes = ()
    serializer_class = SignUpSerializer
    error_messages = {
        'phone_verification_exists': _('Phone verification does not exist'),
        'birthday_under_12': _('You cannot register a user under 12 years '
                               'old'),
        'birthday_creator_over_19': _('Creator must not be older than 19, '
                                      'please select a different account '
                                      'type'),
        'birthday_educator_under_19': _('Educator must be at least 19 '
                                        'years old please select another '
                                        'account type'),
    }

    @sign_up_doc.doc_decorator
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Checking if a device exists
        device = serializer.validated_data['device']

        # We are looking for an instance of the phone model verification
        phone_verification = PhoneVerification.objects.filter(
            token=serializer.validated_data['phone_verify_token'],
            flow=Flow.SIGN_UP,
            status=PhoneVerificationStatus.APPROVED,
            device=device.id,
        ).first()
        if phone_verification is None:
            return Response({
                'phone_verify_token': [
                    self.error_messages['phone_verification_exists'],
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Checking if the application exists
        application = serializer.validated_data['client']

        # Create a user account
        user = User.objects.create_user(
            region=serializer.validated_data['region'],
            type=serializer.validated_data['type'],
            phone_number=phone_verification.phone_number,
            name=serializer.validated_data['name'],
            birthday=serializer.validated_data['birthday'],
            username=serializer.validated_data['username'],
            gender=serializer.validated_data['gender'],
            password=serializer.validated_data['password'],
        )

        # Create tokens and instances of Access Token and Refresh Token
        # And binding the access token to the device
        token = generate_token()
        refresh_token = generate_token()
        access_token = AccessToken.objects.create(
            user_id=user.id,
            token=token,
            application_id=application.id,
            expires=timezone.now() + timedelta(minutes=36000),
            scope='read write',
        )
        refresh_token = RefreshToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            application_id=application.id,
            access_token_id=access_token.id,
        )
        device.auth_token_id = access_token.id
        device.save()

        # Change the status to used so that you cannot use the status token
        phone_verification.status = PhoneVerificationStatus.USED
        phone_verification.save()

        return Response({
            'access_token': access_token.token,
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': access_token.scope,
            'refresh_token': refresh_token.token,
        })
