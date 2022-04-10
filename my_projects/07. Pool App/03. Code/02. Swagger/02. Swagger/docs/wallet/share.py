from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.serializers.wallet.share import \
    DetailShareSerializer
from services.api.swagger.docs.base.status_401 import status_401_response
from services.api.swagger.docs.base.status_403 import status_403_response
from services.api.swagger.docs.base.status_404 import status_404_response

doc_decorator = swagger_auto_schema(
    responses={
        status.HTTP_200_OK: DetailShareSerializer,

        **status_401_response,
        **status_403_response,
        **status_404_response,
    },
)
