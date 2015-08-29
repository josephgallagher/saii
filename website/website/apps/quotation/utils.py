__author__ = 'joseph'
from decimal import Decimal as D

from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model
from oscar.core.loading import get_class
from oscar.apps.order import exceptions

Quotation = get_model('quotation', 'Quotation')
# Line = get_model('quotation', 'Line')
# QuotationDiscount = get_model('quotation', 'QuotationDiscount')
# quotation_placed = get_class('quotation.signals', 'quotation_placed')


class QuotationNumberGenerator(object):
    """
    Simple object for generating quotation numbers.

    We need this as the quotation number is often required for payment
    which takes place before the quotation model has been created.
    """

    def quotation_number(self, basket):
        """
        Return an quotation number for a given basket
        """
        return 999000 + basket.id


class QuotationCreator(object):
    """
    Places the quotation by writing out the various models
    """

    def place_quotation(self, basket, total,  # noqa (too complex (12))
                        shipping_method, shipping_charge, user=None,
                        shipping_address=None, billing_address=None,
                        quotation_number=None, status=None, **kwargs):
        """
        Placing a quotation involves creating all the relevant models based on the
        basket and session data.
        """
        if basket.is_empty:
            raise ValueError(_("Empty baskets cannot be submitted"))
        if not quotation_number:
            generator = QuotationNumberGenerator()
            quotation_number = generator.quotation_number(basket)
        if not status and hasattr(settings, 'OSCAR_INITIAL_ORDER_STATUS'):
            status = getattr(settings, 'OSCAR_INITIAL_ORDER_STATUS')
        try:
            Quotation._default_manager.get(basket_id=quotation_number)
        except Quotation.DoesNotExist:
            pass
        else:
            raise ValueError(_("There is already an quotation with number %s")
                             % quotation_number)

        # Ok - everything seems to be in quotation, let's place the quotation
        quotation = self.create_quotation_model(
            user, basket, shipping_address, shipping_method, shipping_charge,
            billing_address, total, quotation_number, status, **kwargs)
        # for line in basket.all_lines():
        #     self.create_line_models(quotation, line)
        #     self.update_stock_records(line)

        # Record any discounts associated with this quotation
        for application in basket.offer_applications:
            # Trigger any deferred benefits from offers and capture the
            # resulting message
            application['message'] \
                = application['offer'].apply_deferred_benefit(basket, quotation,
                                                              application)
            # Record offer application results
            if application['result'].affects_shipping:
                # Skip zero shipping discounts
                shipping_discount = shipping_method.discount(basket)
                if shipping_discount <= D('0.00'):
                    continue
                # If a shipping offer, we need to grab the actual discount off
                # the shipping method instance, which should be wrapped in an
                # OfferDiscount instance.
                application['discount'] = shipping_discount
            # self.create_discount_model(quotation, application)
            # self.record_discount(application)

        # for voucher in basket.vouchers.all():
        #     self.record_voucher_usage(quotation, voucher, user)

        # Send signal for analytics to pick up
        # quotation_placed.send(sender=self, quotation=quotation, user=user)

        return quotation

    def create_quotation_model(self, user, basket, shipping_address,
                               shipping_method, shipping_charge, billing_address,
                               total, quotation_number, status, **extra_quotation_fields):
        """
        Create an quotation model.
        """
        quotation_data = {'basket': basket,
                          # 'number': quotation_number,
                          # 'site': Site._default_manager.get_current(),
                          # 'currency': total.currency,
                          # 'total_incl_tax': total.incl_tax,
                          # 'total_excl_tax': total.excl_tax,
                          # 'shipping_incl_tax': shipping_charge.incl_tax,
                          # 'shipping_excl_tax': shipping_charge.excl_tax,
                          # 'shipping_method': shipping_method.name,
                          # 'shipping_code': shipping_method.code
                          }
        # if shipping_address:
        #     quotation_data['shipping_address'] = shipping_address
        # if billing_address:
        #     quotation_data['billing_address'] = billing_address
        if user and user.is_authenticated():
            quotation_data['user_id'] = user.id
        if status:
            quotation_data['status'] = status
        if extra_quotation_fields:
            quotation_data.update(extra_quotation_fields)
        quotation = Quotation(**quotation_data)
        quotation.save()
        return quotation
