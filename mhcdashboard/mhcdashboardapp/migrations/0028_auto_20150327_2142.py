# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0027_auto_20150303_1339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='output',
            name='is_shortterm_outcomes',
        ),
        migrations.AddField(
            model_name='output',
            name='comment',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='output',
            name='active_quarter',
            field=models.ForeignKey(default=1, verbose_name=b'Reporting Quarter', to='mhcdashboardapp.ActiveQuarter', null=True),
            preserve_default=True,
        ),
    ]
