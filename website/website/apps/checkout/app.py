# from oscar.apps.checkout import app
#
# import views
#
#
# class CheckoutApplication(app.CheckoutApplication):
#     # Replace the payment details view with our own
#     payment_details_view = views.PaymentDetailsView
#
#
# application = CheckoutApplication()


from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.conf import settings

from oscar.core.application import Application
from oscar.core.loading import get_class


class CheckoutApplication(Application):
    name = 'checkout'

    index_view = get_class('checkout.views', 'IndexView')
    # request_quote_view = get_class('checkout.views', 'RequestQuoteView')
    shipping_address_view = get_class('checkout.views', 'ShippingAddressView')
    user_address_update_view = get_class('checkout.views',
                                         'UserAddressUpdateView')
    user_address_delete_view = get_class('checkout.views',
                                         'UserAddressDeleteView')
    shipping_method_view = get_class('checkout.views', 'ShippingMethodView')
    payment_method_view = get_class('checkout.views', 'PaymentMethodView')
    payment_details_view = get_class('checkout.views', 'PaymentDetailsView')
    pdf_view = get_class('quotation.views', 'PDFView')

    thankyou_view = get_class('checkout.views', 'ThankYouView')

    def get_urls(self):
        urls = [
            url(r'^$', self.index_view.as_view(), name='index'),

            #Request quote views
            # url(r'request-quote/$',
            #     self.request_quote_view.as_view(), name='request-quote'),

            # Shipping/user address views
            url(r'facility-address/$',
                self.shipping_address_view.as_view(), name='shipping-address'),
            url(r'user-address/edit/(?P<pk>\d+)/$',
                self.user_address_update_view.as_view(),
                name='user-address-update'),
            url(r'user-address/delete/(?P<pk>\d+)/$',
                self.user_address_delete_view.as_view(),
                name='user-address-delete'),

            # Shipping method views
            url(r'shipping-method/$',
                self.shipping_method_view.as_view(), name='shipping-method'),

            # Payment views
            url(r'payment-method/$',
                self.payment_method_view.as_view(), name='payment-method'),
            url(r'payment-details/$',
                self.payment_details_view.as_view(), name='payment-details'),

            # PDF views
            url(r'quote/$', self.pdf_view.as_view(), name='pdf-quote'),

            # Preview and thankyou
            url(r'preview/$',
                self.payment_details_view.as_view(preview=True),
                name='preview'),
            url(r'thank-you/$', self.thankyou_view.as_view(),
                name='thank-you'),
        ]
        return self.post_process_urls(urls)

    def get_url_decorator(self, pattern):
        if not settings.OSCAR_ALLOW_ANON_CHECKOUT:
            return login_required
        if pattern.name.startswith('user-address'):
            return login_required
        return None


application = CheckoutApplication()
