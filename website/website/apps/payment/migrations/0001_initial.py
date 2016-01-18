# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oscar.models.fields.autoslugfield
from decimal import Decimal
import oscar.core.utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('order', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bankcard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('card_type', models.CharField(max_length=128, verbose_name='Card Type')),
                ('name', models.CharField(max_length=255, verbose_name='Name', blank=True)),
                ('number', models.CharField(max_length=32, verbose_name='Number')),
                ('expiry_date', models.DateField(verbose_name='Expiry Date')),
                ('partner_reference', models.CharField(max_length=255, verbose_name='Partner Reference', blank=True)),
                ('user', models.ForeignKey(related_name='bankcards', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Bankcard',
                'verbose_name_plural': 'Bankcards',
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currency', models.CharField(default=oscar.core.utils.get_default_currency, max_length=12, verbose_name='Currency')),
                ('amount_allocated', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Allocated', max_digits=12, decimal_places=2)),
                ('amount_debited', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Debited', max_digits=12, decimal_places=2)),
                ('amount_refunded', models.DecimalField(default=Decimal('0.00'), verbose_name='Amount Refunded', max_digits=12, decimal_places=2)),
                ('reference', models.CharField(max_length=128, verbose_name='Reference', blank=True)),
                ('label', models.CharField(max_length=128, verbose_name='Label', blank=True)),
                ('order', models.ForeignKey(related_name='sources', verbose_name='Order', to='order.Order')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
            },
        ),
        migrations.CreateModel(
            name='SourceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('code', oscar.models.fields.autoslugfield.AutoSlugField(populate_from=b'name', editable=False, max_length=128, blank=True, help_text='This is used within forms to identify this source type', unique=True, verbose_name='Code')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Source Type',
                'verbose_name_plural': 'Source Types',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('txn_type', models.CharField(max_length=128, verbose_name='Type', blank=True)),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=12, decimal_places=2)),
                ('reference', models.CharField(max_length=128, verbose_name='Reference', blank=True)),
                ('status', models.CharField(max_length=128, verbose_name='Status', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('source', models.ForeignKey(related_name='transactions', verbose_name='Source', to='payment.Source')),
            ],
            options={
                'ordering': ['-date_created'],
                'abstract': False,
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
        migrations.AddField(
            model_name='source',
            name='source_type',
            field=models.ForeignKey(related_name='sources', verbose_name='Source Type', to='payment.SourceType'),
        ),
    ]
