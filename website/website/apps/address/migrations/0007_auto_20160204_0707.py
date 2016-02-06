# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0006_auto_20160204_0704'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraddress',
            old_name='facility',
            new_name='line1',
        ),
        migrations.AddField(
            model_name='useraddress',
            name='line4',
            field=models.CharField(max_length=255, verbose_name='City', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line2',
            field=models.CharField(max_length=255, verbose_name='Second line of address', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line3',
            field=models.CharField(max_length=255, verbose_name='Third line of address', blank=True),
        ),
    ]
