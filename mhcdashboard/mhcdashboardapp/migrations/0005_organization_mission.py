# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0004_auto_20150209_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='mission',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
