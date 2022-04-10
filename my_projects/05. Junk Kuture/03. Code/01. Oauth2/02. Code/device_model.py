import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from oauth2_provider.settings import oauth2_settings

from apps.main.models_abstract import BaseTimeStampedModel
from apps.users.choices import OSName


class Device(BaseTimeStampedModel):
    # foreign keys
    id = models.UUIDField(primary_key=True, verbose_name=_('ID'),
                          default=uuid.uuid4, editable=False)
    auth_token = models.ForeignKey(
        oauth2_settings.ACCESS_TOKEN_MODEL, null=True,
        on_delete=models.SET_NULL,
    )

    # main fields
    device_id = models.CharField(_('device id'), max_length=200)
    os_name = models.IntegerField(_('os name'), choices=OSName.choices)
    app_version = models.CharField(_('application version'), max_length=200)
    os_version = models.CharField(_('os version'), max_length=200)
    model = models.CharField(_('model'), max_length=200)
    firebase_token = models.CharField(
        _('firebase token'), max_length=200, null=True, blank=True,
    )

    class Meta:
        ordering = ('-created_timestamp',)
        verbose_name = _('device')
        verbose_name_plural = _('devices')

    def __str__(self):
        return self.device_id
