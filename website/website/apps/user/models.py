__author__ = 'joseph'

# file: your-project/apps/user/models.py
from django.db import models
from django.utils.translation import ugettext_lazy as _

from oscar.apps.customer.abstract_models import AbstractUser
from oscar.core.loading import get_class, get_model


# address = get_class('address.models', 'UserAddress')
from ..address.models import UserAddress

class User(AbstractUser):

    # def get_full_name(self):
    #     full_name = '%s %s' % (self.last_name.upper(), self.first_name)
    #     return full_name.strip()

    # class Meta:
    #     db_table = 'auth_user'

    facility = models.CharField(_("Facility"), max_length=20)
    # address = models.OneToOneField(
    #     UserAddress, related_name='address', verbose_name=_("Address"))



