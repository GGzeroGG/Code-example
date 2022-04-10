from drf_yasg import openapi

offers_list_filters_doc = [
    openapi.Parameter(
        'ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
        default='-created_timestamp',
        description='-created_timestamp or created_timestamp',
    ),
    openapi.Parameter(
        'hectares__range', openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description='example: 1.2,4.22',
    ),
    openapi.Parameter(
        'created_timestamp__range', openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='example: 2016-01-01 8:00,2022-01-01 21:00',
    ),
    openapi.Parameter(
        'distributor_id__in', openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='example: 1,2,3,12',
    ),
    openapi.Parameter(
        'product_id__in', openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='example: 1,2,3,12',
    ),
    openapi.Parameter(
        'farming_style__in', openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='example: 0,1',
    ),
    openapi.Parameter(
        'status__in', openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description='example: 0,1,2,3',
    ),
]
