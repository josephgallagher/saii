__author__ = 'joseph'
from oscar.apps.shipping import repository
from . import methods as shipping_methods


# class Repository(repository.Repository):
#     # methods = (methods.UPS(), methods.FedExSecond(), methods.FedExNext(), methods.FedExInternational())
#
#     def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
#         if shipping_addr and shipping_addr.country.code == 'US':
#             methods = (shipping_methods.UPS(), shipping_methods.FedExSecond(), shipping_methods.FedExNext())
#             return methods
#         elif shipping_addr and shipping_addr.country.code == 'CA':
#             methods = (shipping_methods.UPS(), shipping_methods.FedExSecond(), shipping_methods.FedExNext(),
#                        shipping_methods.FedExInternational())
#             return methods
#         else:
#             methods = (shipping_methods.FedExInternational(),)
#             return methods