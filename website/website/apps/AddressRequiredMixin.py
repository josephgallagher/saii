__author__ = 'joseph'
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from oscar.core.loading import get_class, get_classes, get_model
from django.shortcuts import redirect
from django.conf import settings

Dispatcher = get_class('customer.utils', 'Dispatcher')

class AddressRequiredMixin(object):
    @method_decorator(user_passes_test(lambda u: len(u.addresses.all()) != 0))
    def dispatch(self, *args, **kwargs):
        redirect(settings.ADDRESS_REDIRECT_URL)
        return super(AddressRequiredMixin, self).dispatch(*args, **kwargs)