# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0024_auto_20150302_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationactivity',
            name='origin_strid',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
