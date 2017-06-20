# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oscar.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0007_auto_20160204_0707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='first_name',
            field=models.CharField(max_length=20, verbose_name='First name', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='last_name',
            field=models.CharField(max_length=20, verbose_name='Last name', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line1',
            field=models.CharField(max_length=48, verbose_name='Facility'),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line2',
            field=models.CharField(max_length=48, verbose_name='Second line of address', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line3',
            field=models.CharField(max_length=48, verbose_name='Third line of address', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line4',
            field=models.CharField(max_length=25, verbose_name='City', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='postcode',
            field=oscar.models.fields.UppercaseCharField(max_length=20, verbose_name='Post/Zip-code', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='state',
            field=models.CharField(max_length=20, verbose_name='State/County', blank=True),
        ),
    ]
