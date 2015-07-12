__author__ = 'joseph'

from oscar.apps.checkout.views import *


# ===============
# Request Quote
# ===============


class RequestQuoteView(CheckoutSessionMixin, generic.TemplateView):
    template_name = 'checkout/request_quote.html'
    pre_conditions = ['check_basket_is_not_empty',
                      'check_basket_is_valid',
                      'check_user_email_is_captured']
