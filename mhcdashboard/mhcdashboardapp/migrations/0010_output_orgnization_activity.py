# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0009_auto_20150210_0122'),
    ]

    operations = [
        migrations.AddField(
            model_name='output',
            name='orgnization_activity',
            field=models.ForeignKey(default=0, verbose_name=b'Organization Activity', to='mhcdashboardapp.OrganizationActivity'),
            preserve_default=False,
        ),
    ]
