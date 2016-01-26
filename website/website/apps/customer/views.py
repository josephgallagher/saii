__author__ = 'joseph'

from oscar.core.loading import get_class, get_classes, get_model
from oscar.views.generic import PostActionMixin
from oscar.core.utils import safe_referrer
from . import signals

from django import http
from django.conf import settings
from django.contrib import messages
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login as auth_login
from oscar.apps.customer.utils import get_password_reset_url
from django.contrib.sites.models import get_current_site


from django.utils.translation import ugettext_lazy as _

PageTitleMixin, RegisterUserMixin = get_classes('customer.mixins', ['PageTitleMixin', 'RegisterUserMixin'])
Quotation = get_model('quotation', 'Quotation')
OrderSearchForm = get_class('customer.forms', 'OrderSearchForm')
UserAddress = get_model('address', 'UserAddress')
UserAddressForm = get_class('address.forms', 'UserAddressForm')
EmailUserCreationForm = get_class('customer.forms', 'EmailUserCreationForm')
EmailAuthenticationForm = get_class('customer.forms', 'EmailAuthenticationForm')
AddressCreationForm = get_class('customer.forms', 'AddressCreationForm')
ProfileForm, ConfirmPasswordForm = get_classes(
    'customer.forms', ['ProfileForm', 'ConfirmPasswordForm'])
CommunicationEventType = get_model('customer', 'CommunicationEventType')
Dispatcher = get_class('customer.utils', 'Dispatcher')
# FormSet = get_class('customer.forms', 'FormSet')


from django.forms.models import inlineformset_factory
from oscar.core.compat import get_user_model

User = get_user_model()

FormSet = inlineformset_factory(User, UserAddress, exclude=(), )


class AccountAuthView(RegisterUserMixin, generic.TemplateView):
    """
    This is actually a slightly odd double form view that allows a customer to
    either login or register.
    """
    template_name = 'customer/login_registration.html'
    login_prefix, registration_prefix, address_prefix = 'login', 'registration', 'address'
    login_form_class = EmailAuthenticationForm
    registration_form_class = EmailUserCreationForm
    # address_form_class = AddressCreationForm
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super(AccountAuthView, self).get(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(AccountAuthView, self).get_context_data(*args, **kwargs)
        if 'login_form' not in kwargs:
            ctx['login_form'] = self.get_login_form()
        if 'registration_form' not in kwargs:
            ctx['registration_form'] = self.get_registration_form()
        # if 'address_form' not in kwargs:
        #     ctx['address_form'] = self.get_address_form()
        return ctx

    def post(self, request, *args, **kwargs):
        # Use the name of the submit button to determine which form to validate
        if u'login_submit' in request.POST:
            return self.validate_login_form()
        elif u'registration_submit' in request.POST:
            return self.validate_registration_form()
        # elif u'address_submit' in request.POST:
        #     return self.validate_address_form()
        return http.HttpResponseBadRequest()

    # LOGIN

    def get_login_form(self, bind_data=False):
        return self.login_form_class(
            **self.get_login_form_kwargs(bind_data))

    def get_login_form_kwargs(self, bind_data=False):
        kwargs = {}
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.login_prefix
        kwargs['initial'] = {
            'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
        }
        if bind_data and self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def validate_login_form(self):
        form = self.get_login_form(bind_data=True)
        if form.is_valid():
            user = form.get_user()

            # Grab a reference to the session ID before logging in
            old_session_key = self.request.session.session_key

            auth_login(self.request, form.get_user())

            # Raise signal robustly (we don't want exceptions to crash the
            # request handling). We use a custom signal as we want to track the
            # session key before calling login (which cycles the session ID).
            signals.user_logged_in.send_robust(
                sender=self, request=self.request, user=user,
                old_session_key=old_session_key)

            msg = self.get_login_success_message(form)
            messages.success(self.request, msg)

            return redirect(self.get_login_success_url(form))

        ctx = self.get_context_data(login_form=form)
        return self.render_to_response(ctx)

    def get_login_success_message(self, form):
        return _("Welcome back")

    def get_login_success_url(self, form):
        redirect_url = form.cleaned_data['redirect_url']
        if redirect_url:
            return redirect_url

        # Redirect staff members to dashboard as that's the most likely place
        # they'll want to visit if they're logging in.
        if self.request.user.is_staff:
            return reverse('dashboard:index')

        return settings.LOGIN_REDIRECT_URL

    # REGISTRATION

    def get_registration_form(self, bind_data=False):
        return self.registration_form_class(
            **self.get_registration_form_kwargs(bind_data))

    def get_registration_form_kwargs(self, bind_data=False):
        kwargs = {}
        print self.request.get_host()
        kwargs['host'] = self.request.get_host()
        kwargs['prefix'] = self.registration_prefix
        kwargs['initial'] = {
            'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
        }
        if bind_data and self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def validate_registration_form(self):
        form = self.get_registration_form(bind_data=True)
        if form.is_valid():
            self.register_user(form)

            msg = self.get_registration_success_message(form)
            messages.success(self.request, msg)

            return redirect(self.get_registration_success_url(form))

        ctx = self.get_context_data(registration_form=form)
        return self.render_to_response(ctx)

    def get_registration_success_message(self, form):
        return _("Please add an address before continuing!")

    def get_registration_success_url(self, form):
        redirect_url = form.cleaned_data['redirect_url']
        if redirect_url:
            return redirect_url

        return settings.LOGIN_REDIRECT_URL


# Address

    # def get_address_form(self, bind_data=False):
    #     return self.address_form_class(
    #         **self.get_address_form_kwargs(bind_data))
    #
    # def get_address_form_kwargs(self, bind_data=False):
    #     kwargs = {}
    #     user = self.request.user
    #     print self.request.get_host()
    #     kwargs['host'] = self.request.get_host()
    #     kwargs['user'] = user
    #     kwargs['prefix'] = self.address_prefix
    #     kwargs['initial'] = {
    #         'redirect_url': self.request.GET.get(self.redirect_field_name, ''),
    #     }
    #     if bind_data and self.request.method in ('POST', 'PUT'):
    #         kwargs.update({
    #             'data': self.request.POST,
    #             'files': self.request.FILES,
    #         })
    #     return kwargs
    #
    # def validate_address_form(self):
    #     form = self.get_address_form(bind_data=True)
    #     if form.is_valid():
    #         # self.address_user(form)
    #
    #         msg = self.get_address_success_message(form)
    #         messages.success(self.request, msg)
    #
    #         return redirect(self.get_address_success_url(form))
    #
    #     ctx = self.get_context_data(address_form=form)
    #     return self.render_to_response(ctx)
    #
    # def get_address_success_message(self, form):
    #     return _("Thanks for registering!")
    #
    # def get_address_success_url(self, form):
    #     redirect_url = 'redirect_url'
    #     if redirect_url:
    #         return redirect_url
    #
    #     return settings.LOGIN_REDIRECT_URL




class ProfileUpdateView(PageTitleMixin, generic.FormView):
    form_class = ProfileForm
    template_name = 'customer/profile/profile_form.html'
    communication_type_code = 'EMAIL_CHANGED'
    page_title = _('Edit Profile')
    active_tab = 'profile'
    success_url = reverse_lazy('customer:profile-view')

    def get_form_kwargs(self):
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Grab current user instance before we save form.  We may need this to
        # send a warning email if the email address is changed.
        try:
            old_user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            old_user = None

        form.save()

        # We have to look up the email address from the form's
        # cleaned data because the object created by form.save() can
        # either be a user or profile instance depending whether a profile
        # class has been specified by the AUTH_PROFILE_MODULE setting.
        new_email = form.cleaned_data['email']
        if old_user and new_email != old_user.email:
            # Email address has changed - send a confirmation email to the old
            # address including a password reset link in case this is a
            # suspicious change.
            ctx = {
                'user': self.request.user,
                'addresses': self.request.user.addresses,
                'site': get_current_site(self.request),
                'reset_url': get_password_reset_url(old_user),
                'new_email': new_email,
            }
            msgs = CommunicationEventType.objects.get_and_render(
                code=self.communication_type_code, context=ctx)
            Dispatcher().dispatch_user_messages(old_user, msgs)

        messages.success(self.request, _("Profile updated"))
        return redirect(self.get_success_url())


# =============
# Quote history
# =============


class QuotationHistoryView(PageTitleMixin, generic.ListView):
    """
    Customer quote history
    """
    context_object_name = "quotations"
    template_name = 'customer/quotation/quotation_list.html'
    paginate_by = settings.OSCAR_ORDERS_PER_PAGE
    model = Quotation
    form_class = OrderSearchForm
    page_title = _('Quote Request History')
    active_tab = 'quotations'

    def get(self, request, *args, **kwargs):
        if 'date_from' in request.GET:
            self.form = self.form_class(self.request.GET)
            if not self.form.is_valid():
                self.object_list = self.get_queryset()
                ctx = self.get_context_data(object_list=self.object_list)
                return self.render_to_response(ctx)
            data = self.form.cleaned_data

            # If the user has just entered an order number, try and look it up
            # and redirect immediately to the order detail page.
            if data['quotation_number'] and not (data['date_to'] or
                                                     data['date_from']):
                try:
                    quotation = Quotation.objects.get(
                        number=data['quotation_number'], user=self.request.user)
                except Quotation.DoesNotExist:
                    pass
                else:
                    return redirect(
                        'customer:quotation', quotation_number=quotation.number)
        else:
            self.form = self.form_class()
        return super(QuotationHistoryView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model._default_manager.filter(user=self.request.user)
        if self.form.is_bound and self.form.is_valid():
            qs = qs.filter(**self.form.get_filters())
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super(QuotationHistoryView, self).get_context_data(*args, **kwargs)
        ctx['form'] = self.form
        return ctx


class QuotationDetailView(PageTitleMixin, PostActionMixin, generic.DetailView):
    model = Quotation
    active_tab = 'quotations'

    def get_template_names(self):
        return ["customer/quotation/quotation_detail.html"]

    def get_page_title(self):
        """
        Order number as page title
        """
        return u'%s #%s' % (_('Quotation'), self.object.number)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, user=self.request.user,
                                 number=self.kwargs['number'])

    def do_reorder(self, quotation):  # noqa (too complex (10))
        """
        'Order' an existing quote

        This puts the contents of the previous quote into your basket
        """
        # Collect lines to be added to the basket and any warnings for lines
        # that are no longer available.
        basket = self.request.basket
        lines_to_add = []
        warnings = []

        # TODO: Create a custom is_available_to_order() method in quotation/models.py for stock records
        # This simply adds all lines to the basket without checking for stock
        for line in quotation.basket.lines.all():
            lines_to_add.append(line)

        # for line in quotation.basket.lines.all():
        # is_available, reason = line.is_available_to_reorder(
        #         basket, self.request.strategy)
        #     if is_available:
        #         lines_to_add.append(line)
        #     else:
        #         warnings.append(reason)

        # Check whether the number of items in the basket won't exceed the
        # maximum.
        total_quantity = sum([line.quantity for line in lines_to_add])
        is_quantity_allowed, reason = basket.is_quantity_allowed(
            total_quantity)
        if not is_quantity_allowed:
            messages.warning(self.request, reason)
            self.response = redirect('customer:quotation-list')
            return

        # Add any warnings
        for warning in warnings:
            messages.warning(self.request, warning)

        for line in lines_to_add:
            options = []
            for attribute in line.attributes.all():
                if attribute.option:
                    options.append({
                        'option': attribute.option,
                        'value': attribute.value})
            basket.add_product(line.product, line.quantity, options)

        if len(lines_to_add) > 0:
            self.response = redirect('basket:summary')
            messages.info(
                self.request,
                _("All available lines from order %(number)s "
                  "have been added to your basket") % {'number': quotation.number})
        else:
            self.response = redirect('customer:quotation-list')
            messages.warning(
                self.request,
                _("It is not possible to re-order order %(number)s "
                  "as none of its lines are available to purchase") %
                {'number': quotation.number})


# ------------
# Address book
# ------------

class AddressListView(PageTitleMixin, generic.ListView):
    """Customer address book"""
    context_object_name = "addresses"
    template_name = 'customer/address/address_list.html'
    paginate_by = settings.OSCAR_ADDRESSES_PER_PAGE
    active_tab = 'addresses'
    page_title = _('Address Book')

    def get_queryset(self):
        """Return customer's addresses"""
        return UserAddress._default_manager.filter(user=self.request.user)


class AddressCreateView(PageTitleMixin, generic.CreateView):
    form_class = UserAddressForm
    model = UserAddress
    template_name = 'customer/address/address_form.html'
    active_tab = 'addresses'
    page_title = _('Add a new address')
    success_url = reverse_lazy('customer:address-list')

    def get_form_kwargs(self):
        kwargs = super(AddressCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(AddressCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _('Add a new address')
        return ctx

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' created") % self.object.summary)
        return super(AddressCreateView, self).get_success_url()

from fm.views import AjaxCreateView
from feedback_form.forms import FeedbackForm

class UserAddressCreateView(AjaxCreateView):
    form_class = UserAddressForm

    def get_form_kwargs(self):
        kwargs = super(UserAddressCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(UserAddressCreateView, self).get_context_data(**kwargs)
        ctx['title'] = _('Add a new address')
        return ctx

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' created") % self.object.summary)
        return super(UserAddressCreateView, self).get_success_url()


# from django_modalview.generic.edit import ModalFormView
# from django_modalview.generic.component import ModalResponse
#
# class MyFormModal(ModalFormView):
#
#     def __init__(self, *args, **kwargs):
#         super(MyFormModal, self).__init__(*args, **kwargs)
#         # self.title = "My title"
#
#         self.form_class = UserAddressForm #Your django form
#         #self.submit_button has a default value
#
#     def form_valid(self, form, **kwargs):
#         self.response = ModalResponse('Form valid', 'success')



#
# from django_modalview.generic.edit import ModalCreateView
# from django_modalview.generic.component import ModalResponse
#
# # from myapp.forms import MyModelForm
# #
#
# class MyCreateModal(ModalCreateView):
#
#     def __init__(self, *args, **kwargs):
#         super(MyCreateModal, self).__init__(*args, **kwargs)
#         # self.title = "My modal"
#         self.form_class = UserAddressForm
#
#     def form_valid(self, form, **kwargs):
#         '''
#             The form_valid have to return the parent form_valid.
#             In this example I will show you the two most populare case.
#             The first you want just display a success message without the new object
#         '''
#         # self.response = ModalResponse("Good game", "success")
#         # return super(MyCreateModal, self).form_valid(form, **kwargs)
#
#         '''
#             The second, you want use the new object
#         '''
#         self.save(form) #When you save the form an attribute name object is created.
#         self.response = ModalResponse("{obj} is created".format(obj=self.object), 'success')
#         #When you call the parent method you set commit to false because you have save the object.
#         return super(MyCreateModal, self).form_valid(form, commit=False, **kwargs)


class AddressUpdateView(PageTitleMixin, generic.UpdateView):
    form_class = UserAddressForm
    model = UserAddress
    template_name = 'customer/address/address_form.html'
    active_tab = 'addresses'
    page_title = _('Edit address')
    success_url = reverse_lazy('customer:address-list')

    def get_form_kwargs(self):
        kwargs = super(AddressUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(AddressUpdateView, self).get_context_data(**kwargs)
        ctx['title'] = _('Edit address')
        return ctx

    def get_queryset(self):
        return self.request.user.addresses.all()

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' updated") % self.object.summary)
        return super(AddressUpdateView, self).get_success_url()


class AddressDeleteView(PageTitleMixin, generic.DeleteView):
    model = UserAddress
    template_name = "customer/address/address_delete.html"
    page_title = _('Delete address?')
    active_tab = 'addresses'
    context_object_name = 'address'
    success_url = reverse_lazy('customer:address-list')

    def get_queryset(self):
        return UserAddress._default_manager.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' deleted") % self.object.summary)
        return super(AddressDeleteView, self).get_success_url()


class AddressChangeStatusView(generic.RedirectView):
    """
    Sets an address as default_for_(billing|shipping)
    """
    url = reverse_lazy('customer:address-list')
    permanent = False

    def get(self, request, pk=None, action=None, *args, **kwargs):
        address = get_object_or_404(UserAddress, user=self.request.user,
                                    pk=pk)
        # We don't want the user to set an address as the default shipping
        #  address, though they should be able to set it as their billing
        #  address.
        if address.country.is_shipping_country:
            setattr(address, 'is_%s' % action, True)
        elif action == 'default_for_billing':
            setattr(address, 'is_default_for_billing', True)
        else:
            messages.error(request, _('We do not ship to this country'))
        address.save()
        return super(AddressChangeStatusView, self).get(
            request, *args, **kwargs)
