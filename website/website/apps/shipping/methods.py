__author__ = 'joseph'
from decimal import Decimal as D
from django.template.loader import render_to_string

from oscar.apps.shipping import methods
from oscar.core import prices


class UPS(methods.Base):
    code = 'standard'
    name = 'UPS Ground'

    # charge_per_item = D('0.99')
    # threshold = D('12.00')

    # description = render_to_string(
    #     'shipping/standard.html', {
    #         'charge_per_item': charge_per_item,
    #         'threshold': threshold})

    description = "$25.00"

    def calculate(self, basket):
        # Free for orders over some threshold
        # if basket.total_incl_tax > self.threshold:
        #     return prices.Price(
        #         currency=basket.currency,
        #         excl_tax=D('0.00'),
        #         incl_tax=D('0.00'))

        # Simple method - charge 0.99 per item
        # total = basket.num_items * self.charge_per_item
        total = D('25.00')
        return prices.Price(
            currency=basket.currency,
            excl_tax=total,
            incl_tax=total)


class FedExSecond(methods.Base):
    code = 'express'
    name = 'FedEx Second Day'

    # charge_per_item = D('1.50')
    # description = render_to_string(
    #     'shipping/express.html', {'charge_per_item': charge_per_item})

    description = "$28.00"

    def calculate(self, basket):
        # Free for orders over some threshold
        # if basket.total_incl_tax > self.threshold:
        #     return prices.Price(
        #         currency=basket.currency,
        #         excl_tax=D('0.00'),
        #         incl_tax=D('0.00'))

        # Simple method - charge 0.99 per item
        # total = basket.num_items * self.charge_per_item
        total = D('28.00')
        return prices.Price(
            currency=basket.currency,
            excl_tax=total,
            incl_tax=total)


class FedExNext(methods.Base):
    code = 'express_next'
    name = 'FedEx Next Day'

    # charge_per_item = D('1.50')
    # description = render_to_string(
    #     'shipping/express.html', {'charge_per_item': charge_per_item})

    description = "$45.00"

    def calculate(self, basket):
        # Free for orders over some threshold
        # if basket.total_incl_tax > self.threshold:
        #     return prices.Price(
        #         currency=basket.currency,
        #         excl_tax=D('0.00'),
        #         incl_tax=D('0.00'))

        # Simple method - charge 0.99 per item
        # total = basket.num_items * self.charge_per_item
        total = D('45.00')
        return prices.Price(
            currency=basket.currency,
            excl_tax=total,
            incl_tax=total)


class FedExInternational(methods.Base):
    code = 'express_int'
    name = 'FedEx International'

    # charge_per_item = D('1.50')
    # description = render_to_string(
    #     'shipping/express.html', {'charge_per_item': charge_per_item})

    description = "$145.00"

    def calculate(self, basket):
        # Free for orders over some threshold
        # if basket.total_incl_tax > self.threshold:
        #     return prices.Price(
        #         currency=basket.currency,
        #         excl_tax=D('0.00'),
        #         incl_tax=D('0.00'))

        # Simple method - charge 0.99 per item
        # total = basket.num_items * self.charge_per_item
        total = D('145.00')
        return prices.Price(
            currency=basket.currency,
            excl_tax=total,
            incl_tax=total)


class FedExInternationalPriority(methods.Base):
    code = 'express_int_priority'
    name = 'FedEx International Priority'

    # charge_per_item = D('1.50')
    # description = render_to_string(
    #     'shipping/express.html', {'charge_per_item': charge_per_item})

    description = "$190.00"

    def calculate(self, basket):
        # Free for orders over some threshold
        # if basket.total_incl_tax > self.threshold:
        #     return prices.Price(
        #         currency=basket.currency,
        #         excl_tax=D('0.00'),
        #         incl_tax=D('0.00'))

        # Simple method - charge 0.99 per item
        # total = basket.num_items * self.charge_per_item
        total = D('190.00')
        return prices.Price(
            currency=basket.currency,
            excl_tax=total,
            incl_tax=total)