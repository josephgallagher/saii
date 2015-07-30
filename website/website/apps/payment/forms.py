__author__ = 'joseph'

from oscar.apps.payment.forms import *
from oscar.apps.payment.forms import BankcardForm as BaseBankcardForm


# class BankcardForm(BaseBankcardForm):
#     # By default, this number field will accept any number. The only validation
#     # is whether it passes the luhn check. If you wish to only accept certain
#     # types of card, you can pass a types kwarg to BankcardNumberField, e.g.
#     #
#     # BankcardNumberField(types=[bankcards.VISA, bankcards.VISA_ELECTRON,])
#
#     number = BankcardNumberField()
#     ccv = BankcardCCVField()
#     start_month = BankcardStartingMonthField()
#     expiry_month = BankcardExpiryMonthField()
#
#     class Meta(BaseBankcardForm.Meta):
#         BaseBankcardForm.Meta.fields = ('number', 'ccv', 'expiry_month')
#         print ("Fields After Meta: ", BaseBankcardForm.Meta.fields)
#
#     def delete_non_child_fields(self):
#         """
#         Deletes any fields not needed for child products. Override this if
#         you want to e.g. keep the description field.
#         """
#         for field_name in ['start_month']:
#             if field_name in self.fields:
#                 del self.fields[field_name]