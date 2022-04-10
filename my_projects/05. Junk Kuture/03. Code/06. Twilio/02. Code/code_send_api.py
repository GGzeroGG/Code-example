import secrets

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.api.serializers.auth.code_send import CodeSendSerializer
from services.api.swagger.docs import code_send as code_send_doc

from apps.main.choices import Flow, PhoneVerificationStatus
from apps.main.models.phone_verification import PhoneVerification
from apps.main.sms_utils import generate_sms_code
from apps.main.tasks import sending_sms
from apps.users.models.user import User


class CodeSendView(APIView):
    permission_classes = ()
    serializer_class = CodeSendSerializer
    error_messages = {
        'phone_number_exists': _('The phone number is already taken.'),
        'phone_number_does_not_exist': _('User with the phone number does '
                                         'not exist'),
    }

    @code_send_doc.doc_decorator
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Shared variables
        phone_number = serializer.validated_data['phone_number']
        flow = serializer.validated_data['flow']

        user_exists = User.objects.filter(phone_number=phone_number).exists()
        # Registration errors
        if flow == Flow.SIGN_UP:
            # If a user with this number exists, we raise an error
            if user_exists:
                return Response({
                    'phone_number': [
                        self.error_messages['phone_number_exists'],
                    ],
                }, status=status.HTTP_400_BAD_REQUEST)

        # Password change errors
        if flow == Flow.RESET_PASSWORD:
            # Check if a user with this number exists
            if not user_exists:
                return Response({
                    'non_field_errors': [
                        self.error_messages['phone_number_does_not_exist'],
                    ],
                }, status=status.HTTP_404_NOT_FOUND)

        # If the code has already arrived, then it must be canceled
        PhoneVerification.objects.filter(
            flow=flow,
            status=PhoneVerificationStatus.SENT,
            phone_number=serializer.validated_data['phone_number'],
        ).update(status=PhoneVerificationStatus.CANCELLED)

        # Generating code and token and instantiating the model
        token = secrets.token_urlsafe(32)
        code = generate_sms_code()
        PhoneVerification.objects.create(
            phone_number=phone_number,
            flow=flow,
            status=PhoneVerificationStatus.SENT,
            code=code,
            attempts=0,
            token=token,
            device=serializer.validated_data['device'],
        )

        # Send SMS with code
        sending_sms.delay(body=f'Your code: {code}', to=phone_number)

        return Response({'token': token})
