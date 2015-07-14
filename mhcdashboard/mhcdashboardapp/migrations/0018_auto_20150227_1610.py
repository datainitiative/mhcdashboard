# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0017_auto_20150227_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
            ],
            options={
                'db_table': 'indicator',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='workplanarea',
            name='indicator',
            field=models.ForeignKey(default=0, to='mhcdashboardapp.Indicator'),
            preserve_default=False,
        ),
    ]
