import decimal

from rest_framework import serializers


class WalletSharesSerializer(serializers.Serializer):
    fan_name = serializers.CharField(max_length=150)
    total_shares_worth = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_for_day = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_for_day_percentage = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_for_week = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_for_week_percentage = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_for_all = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    difference_for_all_percentage = serializers.DecimalField(
        decimal_places=2, max_digits=9, rounding=decimal.ROUND_FLOOR,
    )
    count_shares = serializers.IntegerField()
    count_artists = serializers.IntegerField()
