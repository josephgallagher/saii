__author__ = 'joseph'

from django.db import models
from oscar.core.compat import AUTH_USER_MODEL
from oscar.core.utils import get_default_currency
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now


class Quotation(models.Model):
    basket = models.OneToOneField('basket.Basket', verbose_name=_("Basket"), related_name='basket')
    user = models.ForeignKey(AUTH_USER_MODEL, related_name='quotations', null=True, verbose_name=_("User"))
    guest_email = models.EmailField(_("Guest email address"), max_length=75, blank=True)
    date_placed = models.DateTimeField(db_index=True)

    def __unicode__(self):
        return "Quote: %d, User: %s" % (self.basket_id, self.user)

    def set_date_placed_default(self):
        if self.date_placed is None:
            self.date_placed = now()

    @property
    def is_anonymous(self):
        # It's possible for an order to be placed by a customer who then
        # deletes their profile.  Hence, we need to check that a guest email is
        # set.
        return self.user is None and bool(self.guest_email)

    def save(self, *args, **kwargs):
        # Ensure the date_placed field works as it auto_now_add was set. But
        # this gives us the ability to set the date_placed explicitly (which is
        # useful when importing orders from another system).
        self.set_date_placed_default()
        super(Quotation, self).save(*args, **kwargs)


@python_2_unicode_compatible
class CommunicationEvent(models.Model):
    """
    An order-level event involving a communication to the customer, such
    as an confirmation email being sent.
    """
    quotation = models.ForeignKey(
        'quotation.Quotation', related_name="communication_events",
        verbose_name=_("Quotation"))
    event_type = models.ForeignKey(
        'customer.CommunicationEventType', related_name="quotation", verbose_name=_("Event Type"))
    date_created = models.DateTimeField(_("Date"), auto_now_add=True)

    class Meta:
        abstract = False
        app_label = 'quotation'
        verbose_name = _("Communication Event")
        verbose_name_plural = _("Communication Events")
        ordering = ['-date_created']

    def __str__(self):
        return _("'%(type)s' event for quotation #%(number)s") \
            % {'type': self.event_type.name, 'number': self.quotation.number}











    """
    The main quote model
    """
    # number = models.CharField(
    #     _("Quote number"), max_length=128, db_index=True, unique=True)
    #
    # # We track the site that each order is placed within
    # site = models.ForeignKey(
    #     'sites.Site', verbose_name=_("Site"), null=True,
    #     on_delete=models.SET_NULL)
    #
    # basket = models.ForeignKey(
    #     'basket.Basket', verbose_name=_("Basket"),
    #     null=True, blank=True, on_delete=models.SET_NULL)
    #
    # # Orders can be placed without the user authenticating so we don't always
    # # have a customer ID.
    # user = models.ForeignKey(
    #     AUTH_USER_MODEL, related_name='quotations', null=True, blank=True,
    #     verbose_name=_("User"), on_delete=models.SET_NULL)
    #
    # # Billing address is not always required (eg paying by gift card)
    # billing_address = models.ForeignKey(
    #     'order.BillingAddress', null=True, blank=True,
    #     verbose_name=_("Billing Address"),
    #     on_delete=models.SET_NULL)
    #
    # # Not all lines are actually shipped (such as downloads), hence shipping
    # # address is not mandatory.
    # shipping_address = models.ForeignKey(
    #     'order.ShippingAddress', null=True, blank=True,
    #     verbose_name=_("Shipping Address"),
    #     on_delete=models.SET_NULL)
    #
    # # FedEx/UPS/DHL
    # shipping_method = models.CharField(
    #     _("Shipping method"), max_length=128, blank=True)
    #
    #
    # # Index added to this field for reporting
    # date_placed = models.DateTimeField(db_index=True)












    """
    OPTIONAL: ADD AS NEEDED IN THE FUTURE
    """
    # Total price looks like it could be calculated by adding up the
    # prices of the associated lines, but in some circumstances extra
    # order-level charges are added and so we need to store it separately
    # currency = models.CharField(
    #     _("Currency"), max_length=12, default=get_default_currency)
    # total_incl_tax = models.DecimalField(
    #     _("Order total (inc. tax)"), decimal_places=2, max_digits=12)
    # total_excl_tax = models.DecimalField(
    #     _("Order total (excl. tax)"), decimal_places=2, max_digits=12)

    # Shipping charges
    # shipping_incl_tax = models.DecimalField(
    #     _("Shipping charge (inc. tax)"), decimal_places=2, max_digits=12,
    #     default=0)
    # shipping_excl_tax = models.DecimalField(
    #     _("Shipping charge (excl. tax)"), decimal_places=2, max_digits=12,
    #     default=0)
        # Identifies shipping code
    # shipping_code = models.CharField(blank=True, max_length=128, default="")

    # Use this field to indicate that an order is on hold / awaiting payment
    # status = models.CharField(_("Status"), max_length=100, blank=True)
    # # TODO Remove the max_length kwarg when support for Django 1.7 is dropped
    # guest_email = models.EmailField(_("Guest email address"), max_length=75,
    #                                 blank=True)
