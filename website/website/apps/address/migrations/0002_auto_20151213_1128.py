# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraddress',
            name='country',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='state',
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='line1',
            field=models.CharField(max_length=255, verbose_name='Facility'),
        ),
    ]
