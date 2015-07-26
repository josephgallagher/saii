__author__ = 'joseph'
# myproject/app.py
from django.conf.urls import include, url, patterns
from oscar import app
from oscar.core.loading import get_class


class MyShop(app.Shop):
    # Override get_urls method
    checkout_app = get_class('checkout.app', 'application')
    quotation_app = get_class('website.apps.quotation.app', 'application')

    def get_urls(self):
        urls = [
            # url(r'^catalog/', include(self.catalogue_app.urls)),
            url(r'^checkout/', include(self.checkout_app.urls)),
            url(r'^quotation/', include(self.quotation_app.urls)),
            url(r'', include(app.application.urls)),
        ]
        return urls

application = MyShop()