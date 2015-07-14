# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkplanArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('str_id', models.CharField(max_length=2)),
                ('description', models.CharField(max_length=500)),
            ],
            options={
                'ordering': ['str_id'],
                'db_table': 'workplan_area',
            },
            bases=(models.Model,),
        ),
    ]
