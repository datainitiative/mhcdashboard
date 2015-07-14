# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0021_auto_20150302_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicator',
            name='description',
            field=models.TextField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mhcactivity',
            name='description',
            field=models.TextField(max_length=500),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='description',
            field=models.TextField(max_length=500),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workplanarea',
            name='description',
            field=models.TextField(max_length=500),
            preserve_default=True,
        ),
    ]
