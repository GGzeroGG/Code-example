from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title='API documentation',
        default_version='v1',
        description='BayCare API annotation'
    ),
    public=True,
    permission_classes=(AllowAny,)
)


class LoginRequiredSchemaView(LoginRequiredMixin, schema_view):
    login_url = settings.SWAGGER_SETTINGS['LOGIN_URL']
