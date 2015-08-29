__author__ = 'joseph'
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class QuotationConfig(AppConfig):
    label = 'quotation'
    name = 'quotation'
    verbose_name = _('Quotation')
