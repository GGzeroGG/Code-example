from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import connection
from django.db.models import Avg, Value
from django.db.models.fields import DateField, IntegerField
from django.db.models.functions import Cast, ExtractIsoWeekDay, TruncDate
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.artists.models import Artist
from services.api.permission_classes import FanOnly
from services.api.swagger.docs.artists.get_price_change_graph import \
    doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class GetPriceChangeGraphView(APIView):
    AVAILABLE_CATEGORIES = ('day', 'week', 'month', 'max')
    DEFAULT_CATEGORY = 'day'
    MONTH_DAYS_COUNT = 31
    DAY_HOURS_COUNT = 24
    WEEK_DAY_COUNT = 7
    DECIMAL_PLACES = 3
    POINTS_FOR_MAX = 12

    permission_classes = (FanOnly,)

    def get(self, request, *args, **kwargs):
        change_share_price, artist = self._get_change_price_queryset()
        category = self.request.query_params.get('category',
                                                 self.DEFAULT_CATEGORY)
        if category not in self.AVAILABLE_CATEGORIES:
            raise ValidationError(detail={
                'category': 'Invalid category entered. The category can be: '
                            'day, week, month, max',
            })

        if not change_share_price.exists():
            data = []

        if category == 'day':
            data = self._get_day_range_data(change_share_price)
        elif category == 'week':
            data = self._get_week_range_data(change_share_price)
        elif category == 'month':
            data = self._get_month_range_data(change_share_price)
        elif category == 'max':
            data = self._get_max_range_data(change_share_price, artist)

        last_dot = data.pop()
        data.append({
            'changed_price': round(artist.price, self.DECIMAL_PLACES),
            'created_timestamp': last_dot['created_timestamp'],
        })

        return Response(data=data, status=status.HTTP_200_OK)

    def _get_month_range_data(self, change_share_price):
        current_timezone = timezone.get_current_timezone()
        time_limit = (
            datetime.now(tz=current_timezone) -
            relativedelta(days=self.MONTH_DAYS_COUNT)
        )

        group_change_share_price = change_share_price.filter(
            created_timestamp__date__gte=time_limit,
        ).annotate(
            monday=Cast(TruncDate('created_timestamp__date') -
                        Cast(ExtractIsoWeekDay('created_timestamp') - Value(1),
                             output_field=IntegerField()),
                        output_field=DateField()),
        ).values(
            'monday',
        ).annotate(
            price=Avg('changed_price'),
        ).order_by(
            'monday',
        )

        group_change_share_price = list(group_change_share_price)

        data = []
        for group in group_change_share_price:
            created_timestamp = current_timezone.localize(
                datetime(year=group['monday'].year,
                         month=group['monday'].month,
                         day=group['monday'].day),
            )

            data.append({
                'changed_price': round(group['price'], self.DECIMAL_PLACES),
                'created_timestamp': created_timestamp,
            })

        return data

    def _get_day_range_data(self, change_share_price):
        current_timezone = timezone.get_current_timezone()
        time_limit = (
            datetime.now(tz=current_timezone) -
            relativedelta(hours=self.DAY_HOURS_COUNT)
        )

        group_change_share_price = change_share_price.filter(
            created_timestamp__gte=time_limit,
        ).values(
            'created_timestamp__date', 'created_timestamp__hour',
        ).annotate(
            price=Avg('changed_price'),
        ).order_by(
            'created_timestamp__date', 'created_timestamp__hour',
        )

        data = []
        for group in group_change_share_price:
            created_timestamp_date = group['created_timestamp__date']
            created_timestamp = datetime(
                year=created_timestamp_date.year,
                month=created_timestamp_date.month,
                day=created_timestamp_date.day,
                hour=group['created_timestamp__hour'],
                tzinfo=current_timezone,
            )
            data.append({
                'changed_price': round(group['price'], self.DECIMAL_PLACES),
                'created_timestamp': created_timestamp,
            })

        return data

    def _get_week_range_data(self, change_share_price):
        current_timezone = timezone.get_current_timezone()
        time_limit = (
            datetime.now(tz=current_timezone) -
            relativedelta(days=self.WEEK_DAY_COUNT)
        )

        group_change_share_price = change_share_price.filter(
            created_timestamp__gte=time_limit,
        ).values(
            'created_timestamp__date',
        ).annotate(
            price=Avg('changed_price'),
        ).order_by(
            'created_timestamp__date',
        )

        data = []
        for group in group_change_share_price:
            created_timestamp_date = group['created_timestamp__date']
            created_timestamp = datetime(
                year=created_timestamp_date.year,
                month=created_timestamp_date.month,
                day=created_timestamp_date.day,
                tzinfo=current_timezone,
            )
            data.append({
                'changed_price': round(group['price'], self.DECIMAL_PLACES),
                'created_timestamp': created_timestamp,
            })

        return data

    def _get_max_range_data(self, change_share_price, artist):
        step = change_share_price.all().count() / self.POINTS_FOR_MAX

        query = (
            """
            WITH change_share_price as (
                SELECT
                    created_timestamp,
                    ROW_NUMBER() OVER (ORDER BY created_timestamp ASC) as row,
                    changed_price
                FROM artists_changeshareprice
                WHERE artist_id = %s
            )
            SELECT
                MIN(created_timestamp),
                CEIL((row) / %s) as point,
                AVG(changed_price)
            FROM change_share_price
            GROUP BY point
            ORDER BY point ASC
            """
        )

        with connection.cursor() as cursor:
            cursor.execute(query, [artist.id, step])
            group_change_share_price = cursor.fetchall()

        data = []
        for iteration, group in enumerate(group_change_share_price):
            data.append({
                'changed_price': round(group[2], self.DECIMAL_PLACES),
                'created_timestamp': group[0],
            })

        return data

    def _get_change_price_queryset(self):
        artist = get_object_or_404(
            Artist.objects.all(), **{'id': self.kwargs['pk']},
        )
        return artist.change_share_prices.all(), artist
