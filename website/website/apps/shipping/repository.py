__author__ = 'joseph'
from oscar.apps.shipping import repository

from . import methods


# Override shipping repository in order to provide our own two
# custom methods
class Repository(repository.Repository):
    methods = (methods.UPS(), methods.FedExSecond(), methods.FedExNext(), methods.FedExInternational())