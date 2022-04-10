from django.db.models import Case, When, Value, F, Sum, DecimalField, Subquery, \
    OuterRef
from django.db.models import Func
from rest_framework.generics import GenericAPIView

from apps.offer.choices.offer import OfferStatus
from apps.offer.models import Offer, OfferComponent
from apps.products.choices.component import ComponentUnit
from services.api.filters import OffersAdminListFilter


class BaseOffersDownloadFileView(GenericAPIView):
    queryset = Offer.objects.all()
    serializer_class = None
    filterset_class = OffersAdminListFilter

    def get_queryset(self):
        components = OfferComponent.objects.filter(
            offer_id=OuterRef('pk'),
        ).annotate(
            price_unit=Case(
                When(
                    unit=ComponentUnit.UNITS.value,
                    then=Func(F('count'), function='ceil') *
                         OuterRef('hectares') * F('price') *
                         (F('tax') + 100) / 100,
                ),
                When(
                    unit=ComponentUnit.LITERS.value,
                    then=Func(F('count'), function='ceil') *
                         OuterRef('hectares') * F('price') *
                         (F('tax') + 100) / 100,
                ),
                When(
                    unit=ComponentUnit.SEEDS.value,
                    then=Func(OuterRef('hectares') * OuterRef('seeds_per_m') *
                              10000 / F('count'), function='ceil') *
                         F('price') * (F('tax') + 100) / 100,
                ),
                output_field=DecimalField(max_digits=10, decimal_places=3)
            ),
        ).values('offer').annotate(
            price_sum=Sum('price_unit'),
        ).values_list('price_sum')

        return self.filter_queryset(self.queryset).annotate(
            status_str=Case(
                When(
                    status=OfferStatus.CONFIRMED.value, then=Value(
                        str(OfferStatus.CONFIRMED.label),
                    ),
                ),
                When(
                    status=OfferStatus.PENDING.value, then=Value(
                        str(OfferStatus.PENDING.label),
                    ),
                ),
                When(
                    status=OfferStatus.ACCEPTED.value, then=Value(
                        str(OfferStatus.ACCEPTED.label),
                    ),
                ),
                When(
                    status=OfferStatus.REJECTED.value, then=Value(
                        str(OfferStatus.REJECTED.label),
                    ),
                ),
                When(
                    status=OfferStatus.EXPIRED.value, then=Value(
                        str(OfferStatus.EXPIRED.label),
                    ),
                ),
            ),
            price=Func(
                Subquery(
                    components,
                    output_field=DecimalField(max_digits=10, decimal_places=3)
                ),
                3, function='round',
                output_field=DecimalField(max_digits=10, decimal_places=3),
            )
        ).values_list(
            'created_timestamp__date', 'offer_distributor__agents_name', 'id',
            'status_str', 'product__name', 'hectares', 'seeds_per_m',
            'price',
        )
