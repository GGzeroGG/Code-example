from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

mobile_api_schema_view = get_schema_view(
    openapi.Info(
        title='API documentation',
        default_version='v1',
        description=('API documentation for mobile application. '
                     'Authenticated requests allowed only from users '
                     'with FAN type.')
    ),
    urlconf='services.api.urls',
    public=True,
    permission_classes=(AllowAny,)
)


artist_api_schema_view = get_schema_view(
    openapi.Info(
        title='API documentation',
        default_version='v1',
        description=('API documentation for artist admin panel. '
                     'Authenticated requests allowed only from users '
                     'with ARTIST type.')
    ),
    urlconf='services.api.admin_urls',
    public=True,
    permission_classes=(AllowAny,)
)


class MobileApiSchemaView(LoginRequiredMixin, mobile_api_schema_view):
    login_url = settings.SWAGGER_SETTINGS['LOGIN_URL']


class AdminPanelApiSchemaView(LoginRequiredMixin, artist_api_schema_view):
    login_url = settings.SWAGGER_SETTINGS['LOGIN_URL']
