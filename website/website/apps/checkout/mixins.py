__author__ = 'joseph'

import logging

from oscar.core.loading import get_class, get_model

from oscar.apps.checkout.mixins import OrderPlacementMixin as CoreOrderPlacementMixin

Dispatcher = get_class('customer.utils', 'Dispatcher')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

CommunicationEventType = get_model('customer', 'CommunicationEventType')


logger = logging.getLogger('oscar.checkout')


class OrderPlacementMixin(CoreOrderPlacementMixin):

    def send_confirmation_message(self, order, code, **kwargs):
        ctx = self.get_message_context(order)
        try:
            event_type = CommunicationEventType.objects.get(code=code)
        except CommunicationEventType.DoesNotExist:
            # No event-type in database, attempt to find templates for this
            # type and render them immediately to get the messages.  Since we
            # have not CommunicationEventType to link to, we can't create a
            # CommunicationEvent instance.
            messages = CommunicationEventType.objects.get_and_render(code, ctx)
            event_type = None
        else:
            messages = event_type.get_messages(ctx)

        if messages and messages['body']:
            logger.info("Order #%s - sending %s messages", order.number, code)
            kwargs["quotation_id"] = order.basket_id
            dispatcher = Dispatcher(logger)
            dispatcher.dispatch_order_messages(order, messages,
                                               event_type, **kwargs)
        else:
            logger.warning("Order #%s - no %s communication event type",
                           order.number, code)

