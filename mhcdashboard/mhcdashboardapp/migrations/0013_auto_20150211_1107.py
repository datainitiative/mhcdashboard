# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0012_auto_20150210_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='output',
            name='is_shortterm_outcomes',
            field=models.IntegerField(default=0, verbose_name=b'Shor Term Outcome?', choices=[(1, b'Yes'), (0, b'No'), (-1, b'Not Reported')]),
            preserve_default=True,
        ),
    ]
