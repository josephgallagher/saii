__author__ = 'joseph'
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

from oscar.core.loading import get_class, get_classes, get_model
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from django.conf import settings


class AddressRequiredMixin(object):
    @method_decorator(user_passes_test(lambda u: len(u.addresses.all()) != 0, reverse_lazy(settings.ADDRESS_REDIRECT_URL)))
    def dispatch(self, *args, **kwargs):
        # messages.add_message(self.request, messages.INFO, 'Please add an address before continuing.')
        # messages.error(self.request, 'Document deleted.')
        return super(AddressRequiredMixin, self).dispatch(*args, **kwargs)