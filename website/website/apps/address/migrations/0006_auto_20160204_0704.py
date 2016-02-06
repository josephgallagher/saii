# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0005_auto_20160118_2052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraddress',
            old_name='line1',
            new_name='facility',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='line4',
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line2',
            field=models.CharField(max_length=255, verbose_name='First line of address', blank=True),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line3',
            field=models.CharField(max_length=255, verbose_name='Second line of address', blank=True),
        ),
    ]
