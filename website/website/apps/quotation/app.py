__author__ = 'joseph'


from django.conf.urls import url
# from django.contrib.auth.decorators import login_required
# from django.conf import settings
from oscar.core.application import Application
from oscar.core.loading import get_class


class QuotationApplication(Application):
    name = 'quotation'

    index_view = get_class('quotation.views', 'IndexView')
    request_quote_view = get_class('quotation.views', 'RequestQuoteView')
    pdf_view = get_class('quotation.views', 'PDFView')

    def get_urls(self):
        urls = [
            url(r'^$', self.index_view.as_view(), name='index'),

            # Request quote views
            # url(r'request-quote/(?P<pk>\d+)/$',
            #     self.request_quote_view.as_view(), name='request-quote'),
            # url(r'request-quote/$',
            #     self.request_quote_view.as_view(), name='request-quote'),
            url(r'request-quote/$', self.request_quote_view.as_view(), name='request-quote'),
            url(r'quote/$', self.pdf_view.as_view(), name='pdf-quote')

        ]
        return self.post_process_urls(urls)


application = QuotationApplication()
