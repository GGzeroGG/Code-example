from django.db.models import F, Value
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import OrderLogs, Preorder
from services.api.permission_classes import FanOnly
from services.api.serializers.wallet.shares_history import \
    SharesHistorySerializer
from services.api.swagger.docs.wallet.shares_history import doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class SharesHistoryView(APIView):
    serializer_class = SharesHistorySerializer
    permission_classes = (FanOnly,)
    INITIAL_ORDER_QUANTITY = 4

    def get(self, request, *args, **kwargs):
        order_logs = OrderLogs.objects.filter(
            buyer_id=self.request.user.id,
        ).annotate(
            price_sum=F('price') * F('count_shares'),
            is_preorder=Value(False),
        ).values(
            'id', 'price', 'created_timestamp', 'artist_id', 'artist__name',
            'artist__photo', 'buy', 'count_shares', 'price_sum', 'is_preorder',
        ).order_by('-created_timestamp')

        # filter order_logs by the buy field
        buy_filter = self.request.query_params.get('buy')
        if buy_filter is not None:
            if buy_filter.lower() == 'true':
                order_logs = order_logs.filter(buy=True)

                # there should be pre-orders in the output
                # pre-order and order fulfilment
                preorders = Preorder.objects.filter(
                    buyer_id=self.request.user.id,
                ).annotate(
                    buy=Value(True),
                    count_shares=F('count'),
                    price_sum=F('price') * F('count'),
                    is_preorder=Value(True),
                ).values(
                    'id', 'price', 'created_timestamp', 'artist_id',
                    'artist__name', 'artist__photo', 'buy', 'count_shares',
                    'price_sum', 'is_preorder',
                )

                order_logs = order_logs.union(preorders)
            elif buy_filter.lower() == 'false':
                order_logs = order_logs.filter(buy=False)

        order_logs = order_logs.order_by('-created_timestamp')

        # filter order_logs by the view_all field
        count = order_logs.count()
        view_all_filter = self.request.query_params.get('view_all')

        if view_all_filter is not None and view_all_filter.lower() == 'true':
            order_logs = order_logs[self.INITIAL_ORDER_QUANTITY:]
        else:
            order_logs = order_logs[:self.INITIAL_ORDER_QUANTITY]

        serializer = SharesHistorySerializer(
            order_logs, many=True, context={'request': self.request},
        )

        return Response(
            {'count': count, 'results': serializer.data},
        )
