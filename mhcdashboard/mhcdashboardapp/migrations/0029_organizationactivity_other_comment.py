# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0028_auto_20150327_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationactivity',
            name='other_comment',
            field=models.CharField(max_length=500, null=True, verbose_name=b'Other Comment', blank=True),
            preserve_default=True,
        ),
    ]
