# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0003_auto_20150209_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('str_id', models.CharField(max_length=20, verbose_name=b'Organization Activity ID')),
                ('description', models.CharField(max_length=500)),
                ('active_quarter', models.ForeignKey(verbose_name=b'Active Quarter', to='mhcdashboardapp.ActiveQuarter', null=True)),
                ('organization', models.ForeignKey(to='mhcdashboardapp.Organization')),
            ],
            options={
                'db_table': 'organization_activity',
            },
            bases=(models.Model,),
        ),    
        migrations.AlterModelOptions(
            name='organizationactivity',
            options={'ordering': ['str_id'], 'verbose_name': 'Organization Activity'},
        ),
        migrations.AddField(
            model_name='organizationactivity',
            name='mhc_activity',
            field=models.ForeignKey(default=0, verbose_name=b'MHC Activity', to='mhcdashboardapp.MHCActivity'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mhcactivity',
            name='str_id',
            field=models.CharField(max_length=10, null=True, verbose_name=b'MHC Activity ID'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='str_id',
            field=models.CharField(max_length=20, null=True, verbose_name=b'Organization Activity ID'),
            preserve_default=True,
        ),
        migrations.AlterModelTable(
            name='organizationactivity',
            table='organization_activity',
        ),
    ]
