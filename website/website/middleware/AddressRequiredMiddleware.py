# __author__ = 'joseph'
#
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import user_passes_test
# from django import http
# from django.core.urlresolvers import reverse, reverse_lazy
# from django.shortcuts import get_object_or_404, redirect
#
# from django.shortcuts import redirect
#
# from oscar.core.loading import get_class, get_classes, get_model
#
# Dispatcher = get_class('customer.utils', 'Dispatcher')
#
#
# class AddressRequiredMiddleware(object):
#     # @method_decorator(user_passes_test(lambda u: len(u.addresses.all()) != 0))
#     # def dispatch(self, *args, **kwargs):
#     #     return super(AddressRequiredMiddleware, self).dispatch(*args, **kwargs)
#
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         path = 'customer:address-create'
#         if user_passes_test(lambda u: len(u.addresses.all()) != 0):
#             return http.HttpResponseRedirect(reverse('customer:address-create'))