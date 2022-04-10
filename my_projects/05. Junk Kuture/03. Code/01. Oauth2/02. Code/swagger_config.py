SWAGGER_SETTINGS = {
    'LOGIN_URL': reverse_lazy('api:rest:login'),
    'LOGOUT_URL': reverse_lazy('api:rest:logout'),

    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'API - Swagger': {
            'type': 'oauth2',
            'authorizationUrl': reverse_lazy('oauth2_provider:authorize'),
            'tokenUrl': reverse_lazy('oauth2_provider:token'),
            'flow': os.getenv('SWAGGER_OAUTH_FLOW', 'password'),
            'scopes': {
            }
        }
    },
    'OAUTH2_CONFIG': {
        'clientId': os.getenv('SWAGGER_OAUTH_CLIENT_ID', '-'),
        'clientSecret': os.getenv('SWAGGER_OAUTH_CLIENT_SECRET', '-'),
        'appName': 'sample'
    },
}
