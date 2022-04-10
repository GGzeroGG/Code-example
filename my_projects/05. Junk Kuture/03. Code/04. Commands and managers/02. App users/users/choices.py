from django.db import models
from django.utils.translation import gettext_lazy as _


class OSName(models.IntegerChoices):
    IOS = 0, _('IOS')
    ANDROID = 1, _('Android')


class UserType(models.IntegerChoices):
    CREATOR = 0, _('creator')
    EDUCATOR = 1, _('educator')
    FAN = 2, _('fan')
    ADMIN = 3, _('admin')


class Gender(models.IntegerChoices):
    MALE = 0, _('male')
    FEMALE = 1, _('female')
    OTHER = 2, _('other')
    NOT_SPECIFIED = 3, _('prefer not to say')


class MessageType(models.IntegerChoices):
    SENT = 0, _('sent')
    RECEIVED = 1, _('received')


users_choices_map = {
    'user_type': {
        UserType.CREATOR.value: 'creator',
        UserType.EDUCATOR.value: 'educator',
        UserType.FAN.value: 'fan',
        UserType.ADMIN.value: 'admin',
    },
    'gender': {
        Gender.MALE.value: 'male',
        Gender.FEMALE.value: 'female',
        Gender.OTHER.value: 'other',
        Gender.NOT_SPECIFIED.value: 'prefer_not_to_say',
    },
    'message_type': {
        MessageType.SENT.value: 'sent',
        MessageType.RECEIVED.value: 'received',
    },
}
