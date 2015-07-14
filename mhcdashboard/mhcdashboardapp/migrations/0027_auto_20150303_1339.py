# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0026_auto_20150302_1344'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkplanDirection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('str_id', models.CharField(max_length=1, verbose_name=b'Workplan Direction ID')),
                ('description', models.TextField(max_length=500)),
            ],
            options={
                'ordering': ['str_id'],
                'db_table': 'workplan_direction',
                'verbose_name': 'Workplan Direction',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='indicator',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='workplanarea',
            name='workplan_direction',
            field=models.ForeignKey(to='mhcdashboardapp.WorkplanDirection', null=True),
            preserve_default=True,
        ),
    ]
