# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0010_output_orgnization_activity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='outputactivity',
            name='deadline',
            field=models.ForeignKey(verbose_name=b'Deadline', to='mhcdashboardapp.ActiveQuarter', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='output',
            name='description',
            field=models.CharField(max_length=500),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='outputactivity',
            name='description',
            field=models.CharField(max_length=500),
            preserve_default=True,
        ),
    ]
