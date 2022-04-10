from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from ..serializers.notifications import NotificationSerializer


class NotificationUserListView(ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by(
        'read', '-created_timestamp'
    )
    filter_fields = ('read', 'id')

    def get_queryset(self):
        return self.queryset.filter(recipient_id=self.request.user.id)


class NotificationReadView(APIView):
    queryset = Notification.objects.all()

    def put(self, request, *args, **kwargs):
        self.queryset.filter(
            recipient_id=self.request.user.id,
            id=self.kwargs['pk'],
        ).update(read=True)
        return Response()


class NotificationReadAllView(APIView):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(
            recipient_id=self.request.user.id,
            read=False,
        ).update(read=True)
        return Response()
