import csv

from django.http import HttpResponse
from django.utils.decorators import method_decorator

from services.api.swagger.docs.offer.offer_download_csv import doc_decorator
from services.api.views.constants import OFFERS_FILE_HEADERS
from services.api.views.offer.base_download_file import \
    BaseOffersDownloadFileView


@method_decorator(name='get', decorator=doc_decorator)
class OffersDownloadCSVView(BaseOffersDownloadFileView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition':
                    'attachment; filename="offers.csv"',
            },
        )
        file_csv = csv.writer(response, delimiter=';')
        file_csv.writerow(OFFERS_FILE_HEADERS)
        file_csv.writerows(self.get_queryset())

        return response
