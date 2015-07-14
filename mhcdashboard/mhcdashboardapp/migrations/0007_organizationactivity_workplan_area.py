# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0006_organization_abbreviation'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationactivity',
            name='workplan_area',
            field=models.ForeignKey(default=0, verbose_name=b'Workplan Area', to='mhcdashboardapp.WorkplanArea'),
            preserve_default=False,
        ),
    ]
