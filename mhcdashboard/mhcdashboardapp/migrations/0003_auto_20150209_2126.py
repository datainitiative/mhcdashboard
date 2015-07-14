# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0002_mhcactivity_organization'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveQuarter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quarter', models.IntegerField()),
            ],
            options={
                'db_table': 'active_quarter',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='mhcactivity',
            options={'ordering': ['str_id'], 'verbose_name': 'MHC Activity'},
        ),
        migrations.AlterModelOptions(
            name='workplanarea',
            options={'ordering': ['str_id'], 'verbose_name': 'Workplan Area'},
        ),
        migrations.AlterField(
            model_name='mhcactivity',
            name='str_id',
            field=models.CharField(max_length=10, verbose_name=b'MHC Activity ID'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workplanarea',
            name='str_id',
            field=models.CharField(max_length=2, verbose_name=b'Workplan Area ID'),
            preserve_default=True,
        ),
    ]
