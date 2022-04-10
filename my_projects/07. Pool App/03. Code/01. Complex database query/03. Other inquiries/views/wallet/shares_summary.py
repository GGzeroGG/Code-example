import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import F, Sum, OuterRef, Subquery, Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.artists.models import ChangeSharePrice
from apps.profile.models import UserShares
from services.api.permission_classes import FanOnly
from services.api.serializers.wallet.shares_summary import \
    WalletSharesSerializer
from services.api.swagger.docs.wallet.shares_summary import doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class WalletSharesView(APIView):
    permission_classes = (FanOnly,)

    DAY_HOURS_COUNT = 24
    WEEK_DAY_COUNT = 7
    DECIMAL_PLACES = 3
    DECIMAL_PLACES_PERCENT = 2

    def get(self, request, *args, **kwargs):
        current_timezone = timezone.get_current_timezone()

        time_limit_day = (
            datetime.datetime.now(tz=current_timezone) -
            relativedelta(hours=self.DAY_HOURS_COUNT, minutes=5)
        )
        time_limit_week = (
            datetime.datetime.now(tz=current_timezone) -
            relativedelta(days=self.WEEK_DAY_COUNT, minutes=5)
        )

        change_share_price_day = ChangeSharePrice.objects.filter(
            artist_id=OuterRef('artist__id'),
            created_timestamp__gt=time_limit_day,
        ).order_by('created_timestamp')
        change_share_price_week = ChangeSharePrice.objects.filter(
            artist_id=OuterRef('artist__id'),
            created_timestamp__gt=time_limit_week,
        ).order_by('created_timestamp')

        response_data = UserShares.objects.filter(
            user=self.request.user.id,
        ).values('artist_id').annotate(
            count_shares=Sum(F('count')),
            artist_price=F('artist__price'),
            artist_price_day=Subquery(
                change_share_price_day.values('changed_price')[:1],
            ),
            artist_price_week=Subquery(
                change_share_price_week.values('changed_price')[:1],
            ),
        ).aggregate(
            total_shares_worth=Sum(F('count_shares') * F('artist_price')),
            price_day_ago=Sum(F('count_shares') * F('artist_price_day')),
            price_week_ago=Sum(
                F('count_shares') * F('artist_price_week'),
            ),
            purchase_price=Sum(F('count_shares') * F('price')),
            sum_count_shares=Sum(F('count_shares')),
            count_artists=Count(F('artist_id'), distinct=True),
        )

        total_shares_worth = response_data['total_shares_worth']
        if total_shares_worth is None:
            total_shares_worth = 0

        price_day_ago = response_data['price_day_ago']
        if price_day_ago is None:
            price_day_ago = 0
            difference_for_day_percentage = 0
        else:
            difference_for_day_percentage = \
                (response_data['total_shares_worth'] -
                 response_data['price_day_ago']) / \
                response_data['price_day_ago'] * 100

        price_week_ago = response_data['price_week_ago']
        if price_week_ago is None:
            price_week_ago = 0
            difference_for_week_percentage = 0
        else:
            difference_for_week_percentage = \
                (response_data['total_shares_worth'] -
                 response_data['price_week_ago']) / \
                response_data['price_week_ago'] * 100

        purchase_price = response_data['purchase_price']
        if purchase_price is None:
            purchase_price = 0
            difference_for_all_percentage = 0
        else:
            difference_for_all_percentage = \
                (response_data['total_shares_worth'] -
                 response_data['purchase_price']) / \
                response_data['purchase_price'] * 100

        serializer = WalletSharesSerializer(
            {
                'fan_name': self.request.user.profile.first_name,
                'total_shares_worth': total_shares_worth,
                'difference_for_day': total_shares_worth - price_day_ago,
                'difference_for_day_percentage': difference_for_day_percentage,
                'difference_for_week': total_shares_worth - price_week_ago,
                'difference_for_week_percentage':
                    difference_for_week_percentage,
                'difference_for_all': total_shares_worth - purchase_price,
                'difference_for_all_percentage': difference_for_all_percentage,
                'count_shares': response_data['sum_count_shares'],
                'count_artists': response_data['count_artists'],
            },
        )

        return Response(data=serializer.data)
