__author__ = 'joseph'

from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.utils.http import urlquote
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

from oscar.apps.order import models
from oscar.core.loading import get_class, get_model, get_classes
from oscar.apps.checkout.mixins import CheckoutSessionMixin
from oscar.apps.checkout import signals

ShippingAddressForm, GatewayForm \
    = get_classes('checkout.forms', ['ShippingAddressForm', 'GatewayForm'])
(BasketLineFormSet, BasketLineForm, AddToBasketForm, BasketVoucherForm,
 SavedLineFormSet, SavedLineForm) \
    = get_classes('basket.forms', ('BasketLineFormSet', 'BasketLineForm',
                                   'AddToBasketForm', 'BasketVoucherForm',
                                   'SavedLineFormSet', 'SavedLineForm'))
Dispatcher = get_class('customer.utils', 'Dispatcher')
Email = get_model('customer', 'Email')
CommunicationEventType = get_model('customer', 'CommunicationEventType')


# ===============
# Index Quote
# ===============

class IndexView(CheckoutSessionMixin, generic.FormView):
    """
    First page of the checkout.  We prompt user to either sign in, or
    to proceed as a guest (where we still collect their email address).
    """
    template_name = 'checkout/gateway.html'
    form_class = GatewayForm
    success_url = reverse_lazy('quotation:request-quote')
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid']

    def get(self, request, *args, **kwargs):
        # We redirect immediately to shipping address stage if the user is
        # signed in.
        if request.user.is_authenticated():
            # We raise a signal to indicate that the user has entered the
            # checkout process so analytics tools can track this event.
            signals.start_checkout.send_robust(
                sender=self, request=request)
            return self.get_success_response()
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(IndexView, self).get_form_kwargs()
        email = self.checkout_session.get_guest_email()
        if email:
            kwargs['initial'] = {
                'username': email,
            }
        return kwargs

    def form_valid(self, form):
        if form.is_guest_checkout() or form.is_new_account_checkout():
            email = form.cleaned_data['username']
            self.checkout_session.set_guest_email(email)

            # We raise a signal to indicate that the user has entered the
            # checkout process by specifying an email address.
            # signals.start_checkout.send_robust(
            #     sender=self, request=self.request, email=email)

            if form.is_new_account_checkout():
                messages.info(
                    self.request,
                    _("Create your account and then you will be redirected "
                      "back to the checkout process"))
                self.success_url = "%s?next=%s&email=%s" % (
                    reverse('customer:register'),
                    # reverse('checkout:shipping-address'),
                    reverse('quotation:request-quote'),
                    urlquote(email)
                )
        else:
            user = form.get_user()
            login(self.request, user)

            # We raise a signal to indicate that the user has entered the
            # checkout process.
            signals.start_checkout.send_robust(
                sender=self, request=self.request)

        return redirect(self.get_success_url())

    def get_success_response(self):
        return redirect(self.get_success_url())


# ===============
# Request Quote
# ===============


from easy_pdf.views import PDFTemplateView


class PDFView(PDFTemplateView):
    template_name = "quotation/quote_pdf.html"


class RequestQuoteView(generic.TemplateView):
    template_name = 'quotation/request_quote.html'
    model = get_model('basket', 'Line')
    basket_model = get_model('basket', 'Basket')
    formset_class = BasketLineFormSet
    form_class = BasketLineForm
    communication_type_code = 'QUOTE_GENERATED'
    pre_conditions = ['check_basket_is_not_empty',
                      'check_basket_is_valid',
                      'check_user_email_is_captured']



class QuoteListView(generic.ListView):
    # Return a list of all of this user's frozen baskets...?
    pass
