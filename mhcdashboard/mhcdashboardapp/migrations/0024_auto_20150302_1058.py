# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0023_auto_20150302_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workplanarea',
            name='indicator',
            field=models.ForeignKey(to='mhcdashboardapp.Indicator', null=True),
            preserve_default=True,
        ),
    ]
