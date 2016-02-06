__author__ = 'joseph'
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserConfig(AppConfig):
    label = 'user'
    name = 'user'
    verbose_name = _('User')
