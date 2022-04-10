from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Device


class DeviceLogoutView(APIView):
    queryset = Device.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def post(self, request, *args, **kwargs):
        token = bytes.decode(self.request.auth, encoding='utf-8')
        Device.objects.filter(auth_token=token).delete()

        return Response(status=status.HTTP_200_OK)
