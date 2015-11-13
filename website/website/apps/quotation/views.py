__author__ = 'joseph'

import six

import os
import datetime
from django.conf import settings
from django.http import HttpResponse

from django.template.loader import get_template
from django.template import Context
from xhtml2pdf import pisa

from django import http
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
# from oscar.apps.checkout.mixins import CheckoutSessionMixin
from mixins import QuotationPlacementMixin
# from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.apps.checkout import signals

from oscar.core.compat import get_user_model

User = get_user_model()

ShippingAddressForm, GatewayForm \
    = get_classes('checkout.forms', ['ShippingAddressForm', 'GatewayForm'])
(BasketLineFormSet, BasketLineForm, AddToBasketForm, BasketVoucherForm,
 SavedLineFormSet, SavedLineForm) \
    = get_classes('basket.forms', ('BasketLineFormSet', 'BasketLineForm',
                                   'AddToBasketForm', 'BasketVoucherForm',
                                   'SavedLineFormSet', 'SavedLineForm'))
Dispatcher = get_class('customer.utils', 'Dispatcher')

UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')

Basket = get_model('basket', 'Basket')
Quotation = get_model('quotation', 'Quotation')
Email = get_model('customer', 'Email')
CommunicationEventType = get_model('customer', 'CommunicationEventType')


# ===============
# Index Quote
# ===============

class IndexView(QuotationPlacementMixin, generic.FormView):
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
            # sender=self, request=self.request, email=email)

            if form.is_new_account_checkout():
                messages.info(
                    self.request,
                    _("Create your account and then you will be redirected "
                      "back to the checkout process"))
                self.success_url = "%s?next=%s&email=%s" % (
                    reverse('customer:register'),
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
from xhtml2pdf.pdf import pisaPDF
from easy_pdf import rendering
# from StringIO import StringIO

from django.template.loader import get_template
from django.template import Context
import cStringIO as StringIO
from cgi import escape


# class PDFView(PDFTemplateView):
# template_name = "quotation/quote_pdf.html"
# model = get_model('quotation', 'Quotation')
# query_results = Quotation.objects.all()
#
#     def write_pdf(self, basket, template_src, context_dict, filename):
#         template = get_template(template_src)
#         main_pdf = pisaPDF()
#
#         context = Context(context_dict)
#         html = template.render(context)
#         result = open(filename, 'w+b')  # Changed from file to filename
#         pdf = pisa.pisaDocument(StringIO.StringIO(
#             html.encode("UTF-8")), result)
#
#         if pdf.err:
#             messages.error(
#                 self.request,
#                 _("An problem occured trying to generate the packing slip for "
#                   "quote #%s") % basket.id,
#             )
#         else:
#             main_pdf.addDocument(pdf)
#
#         response = HttpResponse(main_pdf.getvalue(), content_type='application/pdf')
#         # filename = self.get_packing_slip_filename(orders)
#         response['Content-Disposition'] = 'attachment; filename=%s' % filename
#         result.close()
#
#         return response
#
#
#     # def get_context_data(self, **kwargs):
#     #     return super(PDFView, self).get_context_data(
#     #         pagesize="A4",
#     #         title="Quote Request",
#     #         **kwargs
#     #     )


class PDFView(PDFTemplateView):
    template_name = "quotation/quote_pdf.html"
    model = get_model('quotation', 'Quotation')
    query_results = Quotation.objects.all()

    def render_to_pdf(self, template_src, context_dict, filename):
        template = get_template(template_src)
        context = Context(context_dict)
        html = template.render(context)
        result = open(filename, 'w+b')
        main_pdf = pisaPDF()

        pdf = pisa.pisaDocument(StringIO.StringIO(
            html.encode("UTF-8")), result)
        if not pdf.err:
            main_pdf.addDocument(pdf)
            return HttpResponse(main_pdf.getvalue(), content_type='application/pdf')
        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


class RequestQuoteView(QuotationPlacementMixin, generic.TemplateView):
    model = get_model('quotation', 'Quotation')
    template_name = 'quotation/request_quote.html'
    # model = get_model('basket', 'Line')
    # basket_model = get_model('basket', 'Basket')
    # formset_class = BasketLineFormSet
    # form_class = BasketLineForm

    communication_type_code = 'QUOTE_GENERATED'
    pre_conditions = ['check_basket_is_not_empty',
                      'check_basket_is_valid',
                      'check_user_email_is_captured']
    preview = False

    def post(self, request, *args, **kwargs):
        # Posting to payment-details isn't the right thing to do.  Form
        # submissions should use the preview URL.
        # if not self.preview:
        # return http.HttpResponseBadRequest()

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        if request.POST.get('action', '') == 'get_quote':
            return self.handle_place_order_submission(request)

    def handle_place_order_submission(self, request):
        """
        Handle a request to place an order.

        This method is normally called after the customer has clicked "place
        order" on the preview page. It's responsible for (re-)validating any
        form information then building the submission dict to pass to the
        `submit` method.

        If forms are submitted on your payment details view, you should
        override this method to ensure they are valid before extracting their
        data into the submission dict and passing it onto `submit`.
        """
        return self.submit(**self.build_submission())

    def submit(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):

        """
        Submit a basket for order placement.

        The process runs as follows:

         * Generate an order number
         * Freeze the basket so it cannot be modified any more (important when
           redirecting the user to another site for payment as it prevents the
           basket being manipulated during the payment process).
         * Attempt to take payment for the order
           - If payment is successful, place the order
           - If a redirect is required (eg PayPal, 3DSecure), redirect
           - If payment is unsuccessful, show an appropriate error message

        :basket: The basket to submit.
        :payment_kwargs: Additional kwargs to pass to the handle_payment
                         method. It normally makes sense to pass form
                         instances (rather than model instances) so that the
                         forms can be re-rendered correctly if payment fails.
        :order_kwargs: Additional kwargs to pass to the place_order method
        """
        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}

        # Taxes must be known at this point
        # assert basket.is_tax_known, (
        # "Basket tax must be set before a user can place an order")
        # assert shipping_charge.is_tax_known, (
        # "Shipping charge tax must be set before a user can place an order")

        # We generate the order number first as this will be used
        # in payment requests (ie before the order model has been
        # created).  We also save it in the session for multi-stage
        # checkouts (eg where we redirect to a 3rd party site and place
        # the order on a different request).

        quotation_number = self.generate_quotation_number(basket)
        # order_number = basket.id
        self.checkout_session.set_order_number(quotation_number)

        # Freeze the basket so it cannot be manipulated while the customer is
        # completing request.  Also, store a reference to the basket in the session.

        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        # We define a general error message for when an unanticipated payment
        # error occurs.
        # error_msg = _("A problem occurred while processing payment for this "
        #               "order - no payment has been taken.  Please "
        #               "contact customer services if this problem persists")

        # signals.pre_payment.send_robust(sender=self, view=self)

        # try:
        #     self.handle_payment(order_number, order_total, **payment_kwargs)
        # except RedirectRequired as e:
        #     # Redirect required (eg PayPal, 3DS)
        #     return http.HttpResponseRedirect(e.url)
        # except UnableToTakePayment as e:
        #     # Something went wrong with payment but in an anticipated way.  Eg
        #     # their bankcard has expired, wrong card number - that kind of
        #     # thing. This type of exception is supposed to set a friendly error
        #     # message that makes sense to the customer.
        #     msg = six.text_type(e)
        #     self.restore_frozen_basket()
        #
        #     # We assume that the details submitted on the payment details view
        #     # were invalid (eg expired bankcard).
        #     return self.render_payment_details(
        #         self.request, error=msg, **payment_kwargs)
        # except PaymentError as e:
        #     # A general payment error - Something went wrong which wasn't
        #     # anticipated.  Eg, the payment gateway is down (it happens), your
        #     # credentials are wrong - that king of thing.
        #     # It makes sense to configure the checkout logger to
        #     # mail admins on an error as this issue warrants some further
        #     # investigation.
        #     msg = six.text_type(e)
        #     self.restore_frozen_basket()
        #     return self.render_preview(
        #         self.request, error=error_msg, **payment_kwargs)
        # except Exception as e:
        #     # Unhandled exception - hopefully, you will only ever see this in
        #     # development...
        #     self.restore_frozen_basket()
        #     return self.render_preview(
        #         self.request, error=error_msg, **payment_kwargs)

        # signals.post_payment.send_robust(sender=self, view=self)

        # Try and place quote request
        try:

            from oscar.core.prices import Price
            from oscar.apps.shipping.methods import Free, FixedPrice

            """
            Set these values in order to spoof handle_quotation_placement args for now..
            In the future, ask user for shipping address to calculate quote ???
            """
            order_total = basket.total_excl_tax
            order_total = Price('USD', order_total, order_total, 0)
            shipping_charge = Price('USD', 0.00, 0.00, 0)
            shipping_method = FixedPrice

            template_src = "quotation/quote_pdf.html"
            pdf = PDFView()
            PDFView.render_to_pdf(pdf, template_src, {"title": "Quote Request", 'basket': basket, 'user': user,
                                                      'address': shipping_address},
                                  "media/quote" + str(basket.id) + ".pdf")

            return self.handle_quotation_placement(
                quotation_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = six.text_type(e)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)

    def get_template_names(self):
        return [self.template_name_preview] if self.preview else [
            self.template_name]


# =========
# Thank you
# =========
class ThankYouView(generic.DetailView):
    """
    Displays the 'thank you' page which summarises the order just submitted.
    """
    template_name = 'quotation/thank_you.html'
    context_object_name = 'quotation'

    def get_object(self):
        # We allow superusers to force an order thank-you page for testing
        quotation = None
        if self.request.user.is_superuser:
            if 'quotation_number' in self.request.GET:
                quotation = Quotation._default_manager.get(
                    number=self.request.GET['quotation_number'])
            elif 'quotation_id' in self.request.GET:
                quotation = Quotation._default_manager.get(
                    id=self.request.GET['quotation_id'])

        if not quotation:
            if 'checkout_quotation_id' in self.request.session:
                quotation = Quotation._default_manager.get(
                    pk=self.request.session['checkout_quotation_id'])
            else:
                raise http.Http404(_("No order found"))

        return quotation