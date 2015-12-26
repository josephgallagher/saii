__author__ = 'joseph'
from oscar.apps.address import config
from django.utils.translation import ugettext_lazy as _


class AddressConfig(config.AddressConfig):
    label = 'address'
    name = 'website.apps.address'
    verbose_name = _('Address')
