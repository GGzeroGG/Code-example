import decimal

from django.core.files.storage import default_storage

from rest_framework import serializers


class AnnotateDetailShareSerializer(serializers.Serializer):
    created_timestamp = serializers.DateTimeField()
    count = serializers.IntegerField()
    difference_sum_price = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_sum_price_percentage = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )


class AggregateDetailShareSerializer(serializers.Serializer):
    photo_plate = serializers.SerializerMethodField()
    artist_name = serializers.CharField(source='name')
    artist_price = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
        source='price',
    )
    total_count = serializers.IntegerField()

    total_sum_current_price = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_total_sum_price_percentage = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )

    def get_photo_plate(self, obj):
        if not obj['photo_plate']:
            return ''

        request = self.context.get('request')
        url = default_storage.url(obj['photo_plate'])
        return request.build_absolute_uri(url)


class DetailShareSerializer(serializers.Serializer):
    pooled_data = AggregateDetailShareSerializer()
    shopping_list = AnnotateDetailShareSerializer(many=True)
