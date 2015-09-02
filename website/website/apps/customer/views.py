__author__ = 'joseph'
from oscar.core.loading import get_class, get_classes, get_model
from oscar.views.generic import PostActionMixin


from django.conf import settings
from django.contrib import messages
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from django.utils.translation import ugettext_lazy as _

PageTitleMixin, RegisterUserMixin = get_classes('customer.mixins', ['PageTitleMixin', 'RegisterUserMixin'])
Quotation = get_model('quotation', 'Quotation')
OrderSearchForm = get_class('customer.forms', 'OrderSearchForm')

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
        #     is_available, reason = line.is_available_to_reorder(
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