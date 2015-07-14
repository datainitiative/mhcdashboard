# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0022_auto_20150302_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationactivity',
            name='q1_comment',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationactivity',
            name='q2_comment',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationactivity',
            name='q3_comment',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationactivity',
            name='q4_comment',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
