# __author__ = 'joseph'
# from django.db import models
# from oscar.core.compat import AUTH_USER_MODEL
# from oscar.core.utils import get_default_currency
# from django.utils.translation import ugettext_lazy as _
#
#
# class AbstractQuotation():
#     """
#     The main order model
#     """
#     number = models.CharField(
#         _("Quote number"), max_length=128, db_index=True, unique=True)
#
#     # We track the site that each order is placed within
#     site = models.ForeignKey(
#         'sites.Site', verbose_name=_("Site"), null=True,
#         on_delete=models.SET_NULL)
#
#     basket = models.ForeignKey(
#         'basket.Basket', verbose_name=_("Basket"),
#         null=True, blank=True, on_delete=models.SET_NULL)
#
#     # Orders can be placed without the user authenticating so we don't always
#     # have a customer ID.
#     user = models.ForeignKey(
#         AUTH_USER_MODEL, related_name='quotations', null=True, blank=True,
#         verbose_name=_("User"), on_delete=models.SET_NULL)
#
#     # Billing address is not always required (eg paying by gift card)
#     billing_address = models.ForeignKey(
#         'order.BillingAddress', null=True, blank=True,
#         verbose_name=_("Billing Address"),
#         on_delete=models.SET_NULL)
#
#     # Total price looks like it could be calculated by adding up the
#     # prices of the associated lines, but in some circumstances extra
#     # order-level charges are added and so we need to store it separately
#     currency = models.CharField(
#         _("Currency"), max_length=12, default=get_default_currency)
#     total_incl_tax = models.DecimalField(
#         _("Order total (inc. tax)"), decimal_places=2, max_digits=12)
#     total_excl_tax = models.DecimalField(
#         _("Order total (excl. tax)"), decimal_places=2, max_digits=12)
#
#     # Shipping charges
#     shipping_incl_tax = models.DecimalField(
#         _("Shipping charge (inc. tax)"), decimal_places=2, max_digits=12,
#         default=0)
#     shipping_excl_tax = models.DecimalField(
#         _("Shipping charge (excl. tax)"), decimal_places=2, max_digits=12,
#         default=0)
#
#     # Not all lines are actually shipped (such as downloads), hence shipping
#     # address is not mandatory.
#     shipping_address = models.ForeignKey(
#         'order.ShippingAddress', null=True, blank=True,
#         verbose_name=_("Shipping Address"),
#         on_delete=models.SET_NULL)
#     shipping_method = models.CharField(
#         _("Shipping method"), max_length=128, blank=True)
#
#     # Identifies shipping code
#     shipping_code = models.CharField(blank=True, max_length=128, default="")
#
#     # Use this field to indicate that an order is on hold / awaiting payment
#     status = models.CharField(_("Status"), max_length=100, blank=True)
#     # TODO Remove the max_length kwarg when support for Django 1.7 is dropped
#     guest_email = models.EmailField(_("Guest email address"), max_length=75,
#                                     blank=True)
#
#     # Index added to this field for reporting
#     date_placed = models.DateTimeField(db_index=True)
#
