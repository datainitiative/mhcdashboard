# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0025_organizationactivity_origin_strid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workplanarea',
            name='indicator',
        ),
        migrations.AddField(
            model_name='indicator',
            name='workplan_area',
            field=models.ManyToManyField(to='mhcdashboardapp.WorkplanArea', null=True, blank=True),
            preserve_default=True,
        ),
    ]
