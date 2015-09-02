__author__ = 'joseph'

from django.contrib import admin
from oscar.core.loading import get_model

Quotation = get_model('quotation', 'Quotation')
CommunicationEvent = get_model('quotation', 'CommunicationEvent')
Basket = get_model('basket', 'Basket')


class QuotationAdmin(admin.ModelAdmin):
    model = Basket
    raw_id_fields = ('basket',)
    fieldsets = [
        ('Quotation', {'fields': ['user', 'number', 'basket', 'currency', 'total', 'date_placed']})
    ]


    # readonly_fields = ('basket', 'owner')
    # fieldsets = [('Quotation', {'fields': ['owner', 'basket']})]
    # raw_id_fields = ['user', 'billing_address', 'shipping_address', ]
    # list_display = ('number', 'site', 'user', 'billing_address', 'date_placed')
    # readonly_fields = ('number',)


admin.site.register(Quotation, QuotationAdmin)
admin.site.register(CommunicationEvent)
