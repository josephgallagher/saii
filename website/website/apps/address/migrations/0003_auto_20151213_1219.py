# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oscar.models.fields
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_auto_20151213_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='country',
            field=models.ForeignKey(default=datetime.datetime(2015, 12, 13, 17, 19, 55, 574303, tzinfo=utc), verbose_name='Country', to='address.Country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='useraddress',
            name='postcode',
            field=oscar.models.fields.UppercaseCharField(max_length=64, verbose_name='Post/Zip-code', blank=True),
        ),
        migrations.AddField(
            model_name='useraddress',
            name='state',
            field=models.CharField(max_length=255, verbose_name='State/County', blank=True),
        ),
    ]
