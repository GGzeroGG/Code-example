from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


from phonenumber_field.modelfields import PhoneNumberField

from ..choices import Gender, UserType
from ..file_path.user_avatar import avatar_upload_handler
from ..managers import UserManager
from ...main.models import Region
from ...main.models_abstract import BaseTimeStampedModel


class User(AbstractUser, BaseTimeStampedModel):
    # foreign keys
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, related_name='users',
        verbose_name=_('region'),
    )

    # main fields
    type = models.IntegerField(_('type'), choices=UserType.choices, blank=True)
    phone_number = PhoneNumberField(_('phone number'), unique=True)
    email = models.EmailField(_('email address'), null=True, blank=True) # noqa
    name = models.CharField(_('name'), max_length=200)
    birthday = models.DateField(_('birthday'))
    gender = models.IntegerField(
        _('gender'), choices=Gender.choices, default=Gender.NOT_SPECIFIED,
    )
    bio = models.CharField(_('bio'), null=True, blank=True, max_length=160) # noqa
    is_private = models.BooleanField(_('is private'), default=False)
    avatar = models.ImageField(
        _('profile picture'), upload_to=avatar_upload_handler, null=True,
        blank=True,
    )
    avatar_small = models.ImageField(
        _('profile picture small'), upload_to=avatar_upload_handler, null=True,
        blank=True,
    )

    # unnecessary fields
    first_name = None
    last_name = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'type', 'name', 'birthday']

    objects = UserManager()

    class Meta:
        ordering = ('-created_timestamp',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def clean(self):
        user_admin: User = User.objects.filter(
            type=UserType.ADMIN.value,
        ).exclude(id=self.id).exists()
        if user_admin and self.type == UserType.ADMIN.value:
            raise ValidationError({
                'type': _('You cannot create more than one admin'),
            })
