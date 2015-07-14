# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0016_auto_20150227_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outputactivity',
            name='orgnization_activity',
        ),
        migrations.DeleteModel(
            name='OutputActivity',
        ),
    ]
