from drf_yasg.utils import swagger_auto_schema

from services.api.swagger.docs.base.status_401 import status_401_response
from services.api.swagger.docs.base.status_403 import status_403_response

doc_decorator = swagger_auto_schema(
    responses={
        **status_401_response,
        **status_403_response,
    }
)
