# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0018_auto_20150227_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='Descriptor',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
                ('value', models.TextField(max_length=100, null=True, blank=True)),
                ('algorithm', models.TextField(max_length=500, null=True, blank=True)),
                ('indicator', models.ForeignKey(to='mhcdashboardapp.Indicator')),
            ],
            options={
                'db_table': 'descriptor',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='indicator',
            name='id',
            field=models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True),
            preserve_default=True,
        ),
    ]
