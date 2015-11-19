"""
Uncomment this entire first section to bring the payment view back in
"""

# from django.conf import settings
# from oscar.core.loading import get_model
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
#
# from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
# from facade import Facade
#
# from . import PAYMENT_METHOD_STRIPE, PAYMENT_EVENT_PURCHASE, STRIPE_EMAIL, STRIPE_TOKEN
#
# import forms
#
# SourceType = get_model('payment', 'SourceType')
# Source = get_model('payment', 'Source')
#
#
# class PaymentDetailsView(CorePaymentDetailsView):
#
# @method_decorator(csrf_exempt)
# def dispatch(self, request, *args, **kwargs):
#         return super(PaymentDetailsView, self).dispatch(request, *args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
#         if self.preview:
#             ctx['stripe_token_form'] = forms.StripeTokenForm(self.request.POST)
#             ctx['order_total_incl_tax_cents'] = (
#                 ctx['order_total'].incl_tax * 100
#             ).to_integral_value()
#         else:
#             ctx['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
#         return ctx
#
#     def handle_payment(self, order_number, total, **kwargs):
#         stripe_ref = Facade().charge(
#             order_number,
#             total,
#             card=self.request.POST[STRIPE_TOKEN],
#             description=self.payment_description(order_number, total, **kwargs),
#             metadata=self.payment_metadata(order_number, total, **kwargs))
#
#         source_type, __ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)
#         source = Source(
#             source_type=source_type,
#             currency=settings.STRIPE_CURRENCY,
#             amount_allocated=total.incl_tax,
#             amount_debited=total.incl_tax,
#             reference=stripe_ref)
#         self.add_payment_source(source)
#
#         self.add_payment_event(PAYMENT_EVENT_PURCHASE, total.incl_tax)
#
#     def payment_description(self, order_number, total, **kwargs):
#         return self.request.POST[STRIPE_EMAIL]
#
#     def payment_metadata(self, order_number, total, **kwargs):
#         return {'order_number': order_number}



import logging
import os

from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.checkout.views import signals
from oscar.core.loading import get_model, get_classes, get_class

from django.conf import settings
from django.shortcuts import redirect
from django.utils import six
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage, EmailMultiAlternatives

from django import http

from easy_pdf.views import PDFTemplateView
from xhtml2pdf import pisa
from xhtml2pdf.pdf import pisaPDF
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import cStringIO as StringIO
from cgi import escape
from datetime import datetime

Dispatcher = get_class('customer.utils', 'Dispatcher')
UserAddress = get_model('address', 'UserAddress')
RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes('payment.exceptions', ['RedirectRequired',
                                         'UnableToTakePayment',
                                         'PaymentError'])
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')
logger = logging.getLogger('oscar.checkout')


# ==============
# Payment method
# ==============

class PaymentMethodView(CorePaymentDetailsView):
    """
    View for a user to choose which payment method(s) they want to use.

    This would include setting allocations if payment is to be split
    between multiple sources. It's not the place for entering sensitive details
    like bankcard numbers though - that belongs on the payment details view.
    """
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_shipping_data_is_captured']
    skip_conditions = ['skip_unless_payment_is_required']

    def get(self, request, *args, **kwargs):
        # By default we redirect straight onto the payment details view. Shops
        # that require a choice of payment method may want to override this
        # method to implement their specific logic.
        return self.get_success_response()

    def get_success_response(self):
        return redirect('checkout:payment-details')


# ==============
# PDF
# ==============
import errno
from socket import error as socket_error

class PDFView(PDFTemplateView):
    template_name = "quotation/quote_pdf.html"

    def render_to_pdf(self, template_src, context_dict, filename):
        template = get_template(template_src)
        context = Context(context_dict)
        html = template.render(context)
        # result = open(filename, 'w+b')
        result = StringIO.StringIO()
        # main_pdf = pisaPDF()
        user = context_dict['user']
        quotation_id = context_dict['basket'].id

        try:
            pdf = pisa.pisaDocument(StringIO.StringIO(
                html.encode("UTF-8")), result)
        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                raise serr
        quote_pdf = os.path.join(settings.BASE_DIR, 'media/quote' + str(quotation_id) + ".pdf")

        if not pdf.err:
            # main_pdf.addDocument(pdf)
            # return HttpResponse(main_pdf.getvalue(), content_type='application/pdf')
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'filename="%s"' % filename
            email = EmailMessage('Thanks for your quotation', 'Quotation Attached', 'quotes@i4saquotes.com', [user.email])
            email.attach(quote_pdf, result.getvalue(), 'application/pdf')
            email.send()
            return HttpResponse(response)
        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

# ================
# Order submission
# ================
from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView


class PaymentDetailsView(CorePaymentDetailsView):
    """
    For taking the details of payment and creating the order.

    This view class is used by two separate URLs: 'payment-details' and
    'preview'. The `preview` class attribute is used to distinguish which is
    being used. Chronologically, `payment-details` (preview=False) comes before
    `preview` (preview=True).

    If sensitive details are required (eg a bankcard), then the payment details
    view should submit to the preview URL and a custom implementation of
    `validate_payment_submission` should be provided.

    - If the form data is valid, then the preview template can be rendered with
      the payment-details forms re-rendered within a hidden div so they can be
      re-submitted when the 'place order' button is clicked. This avoids having
      to write sensitive data to disk anywhere during the process. This can be
      done by calling `render_preview`, passing in the extra template context
      vars.

    - If the form data is invalid, then the payment details templates needs to
      be re-rendered with the relevant error messages. This can be done by
      calling `render_payment_details`, passing in the form instances to pass
      to the templates.

    The class is deliberately split into fine-grained methods, responsible for
    only one thing.  This is to make it easier to subclass and override just
    one component of functionality.

    All projects will need to subclass and customise this class as no payment
    is taken by default.
    """
    template_name = 'checkout/payment_details.html'
    template_name_preview = 'checkout/preview.html'

    # These conditions are extended at runtime depending on whether we are in
    # 'preview' mode or not.
    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_shipping_data_is_captured']

    # If preview=True, then we render a preview template that shows all order
    # details ready for submission.
    preview = True

    def get_pre_conditions(self, request):
        if self.preview:
            # The preview view needs to ensure payment information has been
            # correctly captured.
            return self.pre_conditions + ['check_payment_data_is_captured']
        return super(PaymentDetailsView, self).get_pre_conditions(request)

    def get_skip_conditions(self, request):
        if not self.preview:
            # Payment details should only be collected if necessary
            return ['skip_unless_payment_is_required']
        return super(PaymentDetailsView, self).get_skip_conditions(request)

    def post(self, request, *args, **kwargs):
        # Posting to payment-details isn't the right thing to do.  Form
        # submissions should use the preview URL.
        if not self.preview:
            return http.HttpResponseBadRequest()

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        if request.POST.get('action', '') == 'place_order':
            return self.handle_place_order_submission(request)
        return self.handle_payment_details_submission(request)

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

    def handle_payment_details_submission(self, request):
        """
        Handle a request to submit payment details.

        This method will need to be overridden by projects that require forms
        to be submitted on the payment details view.  The new version of this
        method should validate the submitted form data and:

        - If the form data is valid, show the preview view with the forms
          re-rendered in the page
        - If the form data is invalid, show the payment details view with
          the form errors showing.

        """
        # No form data to validate by default, so we simply render the preview
        # page.  If validating form data and it's invalid, then call the
        # render_payment_details view.
        return self.render_preview(request)

    def render_preview(self, request, **kwargs):
        """
        Show a preview of the order.

        If sensitive data was submitted on the payment details page, you will
        need to pass it back to the view here so it can be stored in hidden
        form inputs.  This avoids ever writing the sensitive data to disk.
        """
        self.preview = True
        ctx = self.get_context_data(**kwargs)
        return self.render_to_response(ctx)

    def render_payment_details(self, request, **kwargs):
        """
        Show the payment details page

        This method is useful if the submission from the payment details view
        is invalid and needs to be re-rendered with form errors showing.
        """
        self.preview = False
        ctx = self.get_context_data(**kwargs)
        return self.render_to_response(ctx)

    def get_default_billing_address(self):
        """
        Return default billing address for user

        This is useful when the payment details view includes a billing address
        form - you can use this helper method to prepopulate the form.

        Note, this isn't used in core oscar as there is no billing address form
        by default.
        """
        if not self.request.user.is_authenticated():
            return None
        try:
            return self.request.user.addresses.get(is_default_for_billing=True)
        except UserAddress.DoesNotExist:
            return None

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
        assert basket.is_tax_known, (
            "Basket tax must be set before a user can place an order")
        assert shipping_charge.is_tax_known, (
            "Shipping charge tax must be set before a user can place an order")

        # We generate the order number first as this will be used
        # in payment requests (ie before the order model has been
        # created).  We also save it in the session for multi-stage
        # checkouts (eg where we redirect to a 3rd party site and place
        # the order on a different request).
        order_number = self.generate_order_number(basket)
        self.checkout_session.set_order_number(order_number)
        logger.info("Order #%s: beginning submission process for basket #%d",
                    order_number, basket.id)

        # Freeze the basket so it cannot be manipulated while the customer is
        # completing payment on a 3rd party site.  Also, store a reference to
        # the basket in the session so that we know which basket to thaw if we
        # get an unsuccessful payment response when redirecting to a 3rd party
        # site.
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        # We define a general error message for when an unanticipated payment
        # error occurs.
        error_msg = _("A problem occurred while processing payment for this "
                      "order - no payment has been taken.  Please "
                      "contact customer services if this problem persists")

        signals.pre_payment.send_robust(sender=self, view=self)

        try:
            self.handle_payment(order_number, order_total, **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = six.text_type(e)
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg)
            self.restore_frozen_basket()

            # We assume that the details submitted on the payment details view
            # were invalid (eg expired bankcard).
            return self.render_payment_details(
                self.request, error=msg, **payment_kwargs)
        except PaymentError as e:
            # A general payment error - Something went wrong which wasn't
            # anticipated.  Eg, the payment gateway is down (it happens), your
            # credentials are wrong - that king of thing.
            # It makes sense to configure the checkout logger to
            # mail admins on an error as this issue warrants some further
            # investigation.
            msg = six.text_type(e)
            logger.error("Order #%s: payment error (%s)", order_number, msg,
                         exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)

        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)
        try:
            template_src = "quotation/quote_pdf.html"
            pdf = PDFView()
            PDFView.render_to_pdf(pdf, template_src,
                                  {"title": "Quote Request", 'basket': basket, 'order_number': order_number,
                                   'user': user,
                                   'address': shipping_address, 'datetime': datetime.now()},
                                  "media/quote" + str(basket.id) + ".pdf")

            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = six.text_type(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)

    def get_template_names(self):
        return [self.template_name_preview] if self.preview else [
            self.template_name]


"""
Old stuff
"""
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