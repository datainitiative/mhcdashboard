# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0031_auto_20150603_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='mhcactivity',
            name='year',
            field=models.IntegerField(default=2016),
        ),
        migrations.AddField(
            model_name='organizationactivity',
            name='year',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='workplanarea',
            name='year',
            field=models.IntegerField(default=2016),
        ),
        migrations.AlterField(
            model_name='output',
            name='active_quarter',
            field=models.ForeignKey(default=1, verbose_name=b'Reporting Quarter', to='mhcdashboardapp.ActiveQuarter', null=True),
        ),
    ]
