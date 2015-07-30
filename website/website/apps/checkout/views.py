from django.conf import settings
from oscar.core.loading import get_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from facade import Facade

from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN

import forms

SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')


class PaymentDetailsView(CorePaymentDetailsView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PaymentDetailsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        if self.preview:
            ctx['stripe_token_form'] = forms.StripeTokenForm(self.request.POST)
            ctx['order_total_incl_tax_cents'] = (
                ctx['order_total'].incl_tax * 100
            ).to_integral_value()
        else:
            ctx['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return ctx

    def handle_payment(self, order_number, total, **kwargs):
        stripe_ref = Facade().charge(
            order_number,
            total,
            card=self.request.POST[STRIPE_TOKEN],
            description=self.payment_description(order_number, total, **kwargs),
            metadata=self.payment_metadata(order_number, total, **kwargs))

        source_type, __ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)
        source = Source(
            source_type=source_type,
            currency=settings.STRIPE_CURRENCY,
            amount_allocated=total.incl_tax,
            amount_debited=total.incl_tax,
            reference=stripe_ref)
        self.add_payment_source(source)

        self.add_payment_event(PAYMENT_EVENT_PURCHASE, total.incl_tax)

    def payment_description(self, order_number, total, **kwargs):
        return self.request.POST[STRIPE_EMAIL]

    def payment_metadata(self, order_number, total, **kwargs):
        return {'order_number': order_number}


























# __author__ = 'joseph'
#
# from oscar.apps.checkout.views import *
# from django.contrib.sites.models import Site, get_current_site
# from django.core.urlresolvers import reverse, NoReverseMatch
#
#
# from django.contrib import messages
# from django import http
# from django.core.urlresolvers import reverse
# from django.utils.translation import ugettext_lazy as _
# from datacash.facade import Facade
#
# from oscar.apps.checkout import views, exceptions
# from oscar.apps.payment.forms import BankcardForm
# from oscar.apps.payment.models import SourceType
# from oscar.apps.order.models import BillingAddress
#
# from .forms import BillingAddressForm
#
#
# # Customise the core PaymentDetailsView to integrate Datacash
# class PaymentDetailsView(views.PaymentDetailsView):
#
#     def check_payment_data_is_captured(self, request):
#         if request.method != "POST":
#             raise exceptions.FailedPreCondition(
#                 url=reverse('checkout:payment-details'),
#                 message=_("Please enter your payment details"))
#
#     def get_context_data(self, **kwargs):
#         ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
#         # Ensure newly instantiated instances of the bankcard and billing
#         # address forms are passed to the template context (when they aren't
#         # already specified).
#         if 'bankcard_form' not in kwargs:
#             ctx['bankcard_form'] = BankcardForm()
#         if 'billing_address_form' not in kwargs:
#             ctx['billing_address_form'] = self.get_billing_address_form(
#                 ctx['shipping_address']
#             )
#         elif kwargs['billing_address_form'].is_valid():
#             # On the preview view, we extract the billing address into the
#             # template context so we can show it to the customer.
#             ctx['billing_address'] = kwargs[
#                 'billing_address_form'].save(commit=False)
#         return ctx
#
#     def get_billing_address_form(self, shipping_address):
#         """
#         Return an instantiated billing address form
#         """
#         addr = self.get_default_billing_address()
#         if not addr:
#             return BillingAddressForm(shipping_address=shipping_address)
#         billing_addr = BillingAddress()
#         addr.populate_alternative_model(billing_addr)
#         return BillingAddressForm(shipping_address=shipping_address,
#                                   instance=billing_addr)
#
#     def handle_payment_details_submission(self, request):
#         # Validate the submitted forms
#         bankcard_form = BankcardForm(request.POST)
#         shipping_address = self.get_shipping_address(
#             self.request.basket)
#         address_form = BillingAddressForm(shipping_address, request.POST)
#
#         # print address_form.is_valid()
#         # print address_form.cleaned_data
#         # print address_form.changed_data
#         # print bankcard_form.is_valid()
#
#
#         if address_form.is_valid() and bankcard_form.is_valid():
#             # If both forms are valid, we render the preview view with the
#             # forms hidden within the page. This seems odd but means we don't
#             # have to store sensitive details on the server.
#             return self.render_preview(
#                 request, bankcard_form=bankcard_form,
#                 billing_address_form=address_form)
#
#         # Forms are invalid - show them to the customer along with the
#         # validation errors.
#         return self.render_payment_details(
#             request, bankcard_form=bankcard_form,
#             billing_address_form=address_form)
#
#     def handle_place_order_submission(self, request):
#         bankcard_form = BankcardForm(request.POST)
#         shipping_address = self.get_shipping_address(
#             self.request.basket)
#         address_form = BillingAddressForm(shipping_address, request.POST)
#
#
#         # print address_form.is_valid()
#         # print address_form.cleaned_data
#         # print address_form.changed_data
#         # print bankcard_form.is_valid()
#
#         # print "Bound: %r" % address_form.is_bound
#         # if address_form.errors:
#             # print address_form.country
#         #     messages.error(request, address_form.errors)
#         # if address_form.has_changed():
#         #     print address_form.cleaned_data
#         #     print address_form.changed_data
#
#         if address_form.is_valid() and bankcard_form.is_valid():
#             # Forms still valid, let's submit an order
#             submission = self.build_submission(
#                 order_kwargs={
#                     'billing_address': address_form.save(commit=False),
#                 },
#                 payment_kwargs={
#                     'bankcard_form': bankcard_form,
#                     'billing_address_form': address_form
#                 }
#             )
#             return self.submit(**submission)
#
#         # Must be DOM tampering as these forms were valid and were rendered in
#         # a hidden element.  Hence, we don't need to be that friendly with our
#         # error message.
#         messages.error(request, _("Invalid submission"))
#         return http.HttpResponseRedirect(
#             reverse('checkout:payment-details'))
#
#     def handle_payment(self, order_number, total, **kwargs):
#         # Make request to DataCash - if there any problems (eg bankcard
#         # not valid / request refused by bank) then an exception would be
#         # raised and handled by the parent PaymentDetail view)
#         facade = Facade()
#         bankcard = kwargs['bankcard_form'].bankcard
#         datacash_ref = facade.pre_authorise(
#             order_number, total.incl_tax, bankcard)
#
#         # Request was successful - record the "payment source".  As this
#         # request was a 'pre-auth', we set the 'amount_allocated' - if we had
#         # performed an 'auth' request, then we would set 'amount_debited'.
#         source_type, _ = SourceType.objects.get_or_create(name='Datacash')
#         source = source_type.sources.model(
#             source_type=source_type,
#             currency=total.currency,
#             amount_allocated=total.incl_tax,
#             reference=datacash_ref)
#         self.add_payment_source(source)
#
#         # Also record payment event
#         self.add_payment_event(
#             'pre-auth', total.incl_tax, reference=datacash_ref)