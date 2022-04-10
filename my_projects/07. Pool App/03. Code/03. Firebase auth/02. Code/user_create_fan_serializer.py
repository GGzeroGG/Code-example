from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.auth_core.models import User
from apps.profile.models.profile import Profile


class ProfileInLineSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    address = serializers.CharField(required=True, max_length=200)
    country = serializers.CharField(required=True, max_length=150)

    class Meta:
        default_error_messages = {
            'invalid_date': _('api_errors:invalid_date_format'),
        }

        model = Profile
        fields = ('first_name', 'last_name', 'birthday', 'address', 'country')
        extra_kwargs = {
            'birthday': {
                'error_messages': {
                    'invalid': default_error_messages['invalid_date']
                },
            },
        }


class UserCreateFanSerializer(serializers.ModelSerializer):
    profile = ProfileInLineSerializer()

    class Meta:
        model = User
        fields = ('email', 'profile', 'registration_device')
        extra_kwargs = {
            'registration_device': {'required': True, 'allow_null': False}
        }
