# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0015_auto_20150211_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='output',
            name='output_activity',
        ),
        migrations.AlterField(
            model_name='output',
            name='is_goal',
            field=models.IntegerField(default=-99, verbose_name=b'Goals Reached?', choices=[(1, b'Yes'), (0, b'No'), (-1, b'Not Reported'), (-99, b'TBD')]),
            preserve_default=True,
        ),
    ]
