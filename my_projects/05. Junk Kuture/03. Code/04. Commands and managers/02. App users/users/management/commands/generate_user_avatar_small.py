from django.conf import settings
from django.core.management.base import BaseCommand

from easy_thumbnails.files import get_thumbnailer

from apps.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = User.objects.all().only('avatar')
        for instance in users.iterator():
            if instance.avatar:
                avatar_small = get_thumbnailer(
                    instance.avatar,
                ).get_thumbnail(settings.THUMBNAIL_ALIASES['']['avatar'])
                instance.avatar_small = avatar_small.name
                instance.save(update_fields=['avatar_small'])
