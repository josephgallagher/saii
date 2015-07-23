__author__ = 'joseph'
# myproject/app.py
from django.conf.urls import include, url, patterns
from oscar import app


class MyShop(app.Shop):
    # Override get_urls method
    def get_urls(self):
        urls = [
            url(r'^catalog/', include(self.catalogue_app.urls)),
            url(r'', include(app.application.urls)),

        ]
        return urls

application = MyShop()