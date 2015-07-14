# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0007_organizationactivity_workplan_area'),
    ]

    operations = [
        migrations.CreateModel(
            name='Output',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=500, null=True, blank=True)),
                ('is_shortterm_outcomes', models.IntegerField(default=0, verbose_name=b'Shor Term Outcome?', choices=[(1, b'Yes'), (0, b'No')])),
                ('is_goal', models.IntegerField(default=0, verbose_name=b'Goals Reached?', choices=[(1, b'Yes'), (0, b'No')])),
                ('output_value', models.CharField(max_length=500, null=True, verbose_name=b'Output Value', blank=True)),
            ],
            options={
                'db_table': 'output',
                'verbose_name': 'Output',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutputActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('str_id', models.CharField(max_length=30, null=True, verbose_name=b'Output Activity ID')),
                ('description', models.TextField()),
                ('orgnization_activity', models.ForeignKey(verbose_name=b'Organization Activity', to='mhcdashboardapp.OrganizationActivity')),
            ],
            options={
                'ordering': ['str_id'],
                'db_table': 'output_activity',
                'verbose_name': 'Output Activity',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='output',
            name='output_activity',
            field=models.ForeignKey(verbose_name=b'Output Activity', to='mhcdashboardapp.OutputActivity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='output',
            name='quarter',
            field=models.ForeignKey(verbose_name=b'Quarter', to='mhcdashboardapp.ActiveQuarter', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='mhc_activity',
            field=smart_selects.db_fields.ChainedForeignKey(chained_model_field=b'workplan_area', chained_field=b'workplan_area', auto_choose=True, to='mhcdashboardapp.MHCActivity'),
            preserve_default=True,
        ),
    ]
