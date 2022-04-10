import decimal

from django.core.files.storage import default_storage
from rest_framework import serializers


class SharesHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count_shares = serializers.IntegerField()
    price = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    created_timestamp = serializers.DateTimeField()
    artist = serializers.SerializerMethodField()
    price_sum = serializers.SerializerMethodField()
    is_preorder = serializers.BooleanField()

    def get_artist(self, obl):
        if not obl['artist__photo']:
            photo = ''
        else:
            request = self.context.get('request')
            url = default_storage.url(obl['artist__photo'])
            photo = request.build_absolute_uri(url)

        artist_data = {
            'name': obl['artist__name'],
            'photo': photo,
        }

        return artist_data

    def get_price_sum(self, obj) -> str:
        return str(obj['price_sum'] * -1) if obj['buy'] else \
            '+' + str(obj['price_sum'])
