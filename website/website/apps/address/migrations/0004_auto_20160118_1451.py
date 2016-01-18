# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_auto_20151213_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='user',
            field=models.OneToOneField(related_name='addresses', verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
    ]
