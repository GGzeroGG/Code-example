import decimal

from django.core.files.storage import default_storage

from rest_framework import serializers

from apps.profile.models import UserShares


class WalletSharesListSerializer(serializers.ModelSerializer):
    total_worth = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_percents = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    artist_name = serializers.CharField(max_length=100)
    first_by_datetime = serializers.DateTimeField()
    amount = serializers.IntegerField()
    photo_plate = serializers.SerializerMethodField()

    class Meta:
        model = UserShares
        fields = (
            'artist_id', 'artist_name', 'total_worth', 'difference',
            'difference_percents', 'first_by_datetime', 'amount',
            'photo_plate',
        )

    def get_photo_plate(self, data):
        if not data['photo_plate']:
            return ''

        request = self.context.get('request')
        url = default_storage.url(data['photo_plate'])
        return request.build_absolute_uri(url)
