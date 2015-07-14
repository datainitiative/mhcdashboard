# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0008_auto_20150210_0114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizationactivity',
            name='active_quarter',
        ),
        migrations.RemoveField(
            model_name='output',
            name='quarter',
        ),
        migrations.AddField(
            model_name='output',
            name='active_quarter',
            field=models.ForeignKey(verbose_name=b'Active Quarter', to='mhcdashboardapp.ActiveQuarter', null=True),
            preserve_default=True,
        ),
    ]
