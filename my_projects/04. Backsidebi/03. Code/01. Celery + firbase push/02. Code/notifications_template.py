from .models import Notification

NOTIFICATION = {
    Notification.TYPE.COMMENT_CREATED.value: {
        'title': 'A new comment has been added',
        'body': 'Your post has been commented',
    },
    Notification.TYPE.COMMENT_ANSWERED.value: {
        'title': 'Reply to your comment',
        'body': 'You have been answered {{obj.id}} on a comment',
    },
    Notification.TYPE.POST_BLOCKED.value: {
        'title': 'Your post has been blocked',
        'body': 'Your post has been blocked',
    },
}