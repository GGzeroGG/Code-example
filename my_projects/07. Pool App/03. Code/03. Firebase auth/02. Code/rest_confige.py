from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'services.firebase.authentication.FirebaseAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

if DEBUG is True:
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].insert(0, 'rest_framework.authentication.SessionAuthentication')

API_SECRET_KEY = env.str('API_SECRET_KEY',
                         default='4QPKQDiybWdtM-gDA5vA5w4GPzbQ5DXbpFsBtwjjJYI=')
API_REQUEST_ALLOWED_TIMEDELTA = timedelta(minutes=5)
