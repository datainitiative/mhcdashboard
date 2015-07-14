# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0013_auto_20150211_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='output',
            name='is_goal',
            field=models.IntegerField(default=0, verbose_name=b'Goals Reached?', choices=[(1, b'Yes'), (0, b'No'), (-1, b'Not Reported')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='output',
            name='is_shortterm_outcomes',
            field=models.IntegerField(default=0, verbose_name=b'Shor Term Outcome?', choices=[(1, b'Yes'), (0, b'No')]),
            preserve_default=True,
        ),
    ]
