# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MHCActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('str_id', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=500)),
                ('workplan_area', models.ForeignKey(verbose_name=b'Workplan Area', to='mhcdashboardapp.WorkplanArea')),
            ],
            options={
                'ordering': ['str_id'],
                'db_table': 'mhc_activity',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Organization')),
            ],
            options={
                'db_table': 'organization',
            },
            bases=(models.Model,),
        ),
    ]
