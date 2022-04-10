from oauth2_provider.models import AccessToken, RefreshToken

from rest_framework.response import Response
from rest_framework.views import APIView


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        RefreshToken.objects.filter(
            token=self.request.auth.refresh_token,
        ).delete()
        AccessToken.objects.filter(
            token=self.request.auth.token,
        ).delete()
        return Response()
