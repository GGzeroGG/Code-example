from django.db.models import F, Sum, Value, Min
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.profile.models import UserShares
from services.api.filters_classes import WalletSharesListFilter
from services.api.permission_classes import FanOnly
from services.api.serializers.wallet.shares import WalletSharesListSerializer
from services.api.swagger.docs.wallet.shares import doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class WalletSharesListView(GenericAPIView):
    permission_classes = (FanOnly,)
    serializer_class = WalletSharesListSerializer
    filter_class = WalletSharesListFilter
    search_fields = ('artist__name',)

    # Overridden order because filter_class uses a slice and breaks the
    # search_fields logic
    filter_backends = [
        SearchFilter, OrderingFilter, DjangoFilterBackend,
    ]

    queryset = UserShares.objects.all().values(
        'artist_id',
    ).annotate(
        artist_name=F('artist__name'),
        total_current_worth=Sum(F('artist__price') * F('count')),
        amount=Sum(F('count')),
        total_worth=Sum(F('price') * F('count')),
        photo_plate=F('artist__photo_plate'),

        difference=F('total_current_worth') - F('total_worth'),
        difference_percents=(
            (F('total_current_worth') - F('total_worth')) /
            F('total_worth') * Value(100)
        ),

        first_by_datetime=Min('created_timestamp'),
    ).order_by('-artist__pool', '-total_worth')

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        queryset, count = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response(data={'count': count, 'results': serializer.data})
