import xlwt
from django.http import HttpResponse
from django.utils.decorators import method_decorator

from services.api.swagger.docs.offer.offer_download_xls import doc_decorator
from services.api.views.constants import OFFERS_FILE_HEADERS
from services.api.views.offer.base_download_file import \
    BaseOffersDownloadFileView


@method_decorator(name='get', decorator=doc_decorator)
class OffersDownloadXLSView(BaseOffersDownloadFileView):
    def get(self, request, *args, **kwargs):
        file_create = xlwt.Workbook()
        file_list = file_create.add_sheet(sheetname='offers')

        for number_header, header in enumerate(OFFERS_FILE_HEADERS):
            file_list.write(0, number_header, str(header))

        for number_offer, offer in enumerate(self.get_queryset()):
            for number_field, offer_field in enumerate(offer):
                file_list.write(
                    number_offer + 1, number_field, str(offer_field),
                )

        response = HttpResponse(content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=offers.xls'
        file_create.save(response)

        return response
