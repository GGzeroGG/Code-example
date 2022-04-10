from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.serializers.wallet.shares_summary import \
    WalletSharesSerializer
from services.api.swagger.docs.base.status_401 import status_401_response
from services.api.swagger.docs.base.status_403 import status_403_response

doc_decorator = swagger_auto_schema(
    responses={
        status.HTTP_200_OK: WalletSharesSerializer,

        **status_401_response,
        **status_403_response,
    },
)
