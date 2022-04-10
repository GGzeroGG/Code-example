from django.db.models import F, Sum
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.artists.models import Artist
from apps.profile.models import UserShares
from services.api.permission_classes import FanOnly
from services.api.serializers.wallet.share import \
    DetailShareSerializer
from services.api.swagger.docs.wallet.share import doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class DetailShareView(APIView):
    error_messages = {
        'not_shares': _('api_errors:no_user_shares_of_artist'),
    }
    permission_classes = (FanOnly,)

    def get(self, request, *args, **kwargs):
        queryset = UserShares.objects.filter(
            user_id=self.request.user.id, artist_id=self.kwargs['artist_id'],
        ).order_by('-created_timestamp')

        if not queryset.exists():
            return Response({
                'detail': self.error_messages['not_shares'],
            }, status=status.HTTP_404_NOT_FOUND)

        shares_buy_details_queryset = queryset.annotate(
            total_purchase_price=(F('count') * F('price')),
            current_price=(F('count') * F('artist__price')),
            difference_sum_price=(
                F('current_price') - F('total_purchase_price')
            ),
            difference_sum_price_percentage=(
                (F('current_price') - F('total_purchase_price')) /
                F('total_purchase_price') * 100
            ),
        )

        aggregated_data = shares_buy_details_queryset.aggregate(
            total_count=Sum(F('count')),
            total_sum_current_price=Sum(F('current_price')),
            difference_total_sum_price_percentage=(
                (Sum(F('current_price')) - Sum(F('total_purchase_price'))) /
                Sum(F('total_purchase_price')) * 100
            ),
        )

        artist_data = Artist.objects.values(
            'id', 'name', 'price', 'photo_plate',
        ).get(id=self.kwargs['artist_id'])

        serializer = DetailShareSerializer({
            'pooled_data': {**artist_data, **aggregated_data},
            'shopping_list': shares_buy_details_queryset,
        }, context={'request': request})

        return Response(data=serializer.data)
