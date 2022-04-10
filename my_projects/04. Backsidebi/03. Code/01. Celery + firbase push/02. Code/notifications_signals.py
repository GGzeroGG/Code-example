from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template import Template, Context

from apps.main.models import Comment, STATUS, Post
from apps.notifications.models import Notification
from apps.notifications.templates import NOTIFICATION
from apps.users.models import Device
from services.tasks.notifications import send_notification_multicast
from . import utils

METADATA_HANDLERS = {
    Notification.TYPE.POST_BLOCKED.value: utils.fetch_metadata_post_blocked,
    Notification.TYPE.COMMENT_CREATED.value: utils.fetch_metadata_comment_created,
    Notification.TYPE.COMMENT_ANSWERED.value: utils.fetch_metadata_comment_answered,
}


@receiver(pre_save, sender=Post)
def post_blocked_handler(instance: Post, **kwargs):
    if instance._state.adding:
        return

    queryset = Post.objects.filter(id=instance.id).filter(
        status=STATUS.CHECK_PASSED
    )
    if instance.status == STATUS.CHECK_NOT_PASSED.value and queryset.exists():
        Notification.objects.create(
            type=Notification.TYPE.POST_BLOCKED,
            object_id=instance.id,
            recipient=instance.user,
            sender=None,
        )


@receiver(pre_save, sender=Notification)
def notification_create_handler(instance: Notification, **kwargs):
    # skip on editing
    if not instance._state.adding:
        return

    context = Context({'obj': instance})
    title_t = Template(NOTIFICATION[instance.type]['title'])
    body_t = Template(NOTIFICATION[instance.type]['body'])

    title = title_t.render(context)
    body = body_t.render(context)

    metadata_handler = METADATA_HANDLERS.get(instance.type, None)
    if metadata_handler:
        metadata = metadata_handler(instance.related_obj)
    else:
        metadata = {}

    metadata['type'] = str(instance.type)
    instance.meta = metadata
    instance.title = title
    instance.body = body


@receiver(post_save, sender=Notification)
def notification_sending_handler(instance: Notification, **kwargs):
    if kwargs['created']:
        registration_tokens = Device.objects.filter(
            user_id=instance.recipient_id
        ).values_list('registration_token', flat=True)
        registration_tokens = list(set(registration_tokens))
        if len(registration_tokens) > 0:
            send_notification_multicast(
                registration_tokens=registration_tokens,
                title=instance.title,
                body=instance.body,
                data=dict(instance.meta, notification=str(instance.id)),
            )


@receiver(post_save, sender=Comment)
def create_comment_handler(instance: Comment, **kwargs):
    """
    Sends notifications on new comment. There are two possible cases:
     - comment added for the post;
     - answer added for user's comment.
    """
    if kwargs['created']:
        initiator = instance.user
        post_user = instance.post.user
        if not instance.comment:
            if post_user != initiator:
                Notification.objects.create(
                    type=Notification.TYPE.COMMENT_CREATED,
                    object_id=instance.id,
                    sender=initiator,
                    recipient=post_user,
                )
        elif instance.comment.user:
            if instance.comment.user != initiator:
                Notification.objects.create(
                    type=Notification.TYPE.COMMENT_ANSWERED,
                    object_id=instance.id,
                    sender=initiator,
                    recipient=instance.comment.user,
                )
