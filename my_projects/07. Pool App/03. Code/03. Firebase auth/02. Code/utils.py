import logging
from typing import Tuple

import firebase_admin
from django.conf import settings
from django.template import Context, Template
from firebase_admin import auth, credentials
from firebase_admin.auth import UserDisabledError, ExpiredIdTokenError, \
    InvalidIdTokenError, CertificateFetchError, RevokedIdTokenError

from apps.notifications.models import Device
from apps.notifications.templates import NOTIFICATIONS

logger = logging.getLogger(__name__)


def get_firebase_app():
    if settings.IS_TEST_RUN:
        return None

    try:
        cred = credentials.Certificate(settings.FIREBASE_APP_CREDENTIALS)
    except ValueError as ex:
        logger.warning(f'Invalid firebase credentials: {ex}')
        return None

    try:
        return firebase_admin.initialize_app(credential=cred)
    except ValueError:
        return firebase_admin.get_app()


def get_firebase_uid(id_token, app=None):
    """
    Takes id_token checks its validity in the firebase application and returns
    either uid or None
    """
    try:
        decoded_token = auth.verify_id_token(id_token, app=app)
        return decoded_token['uid']
    except (ValueError, InvalidIdTokenError, ExpiredIdTokenError,
            RevokedIdTokenError, CertificateFetchError,
            UserDisabledError) as ex:
        logger.warning(f'Invalid auth token: {ex}, token: {id_token}')
        return None

