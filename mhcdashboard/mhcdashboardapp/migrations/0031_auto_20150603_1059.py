# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0030_auto_20150328_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='output',
            name='active_quarter',
            field=models.ForeignKey(default=2, verbose_name=b'Reporting Quarter', to='mhcdashboardapp.ActiveQuarter', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='output',
            name='comment',
            field=models.TextField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='output',
            name='is_goal',
            field=models.IntegerField(default=-1, verbose_name=b'Goals Reached?', choices=[(1, b'Yes'), (0, b'No'), (-1, b'Not Reported'), (-99, b'TBD')]),
            preserve_default=True,
        ),
    ]
