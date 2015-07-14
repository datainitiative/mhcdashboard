# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0011_auto_20150210_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationactivity',
            name='mhc_activity',
            field=smart_selects.db_fields.ChainedForeignKey(auto_choose=True, to='mhcdashboardapp.MHCActivity', chained_model_field=b'workplan_area', chained_field=b'workplan_area', verbose_name=b'MHC Activity'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='organization',
            field=models.ForeignKey(verbose_name=b'Organization', to='mhcdashboardapp.Organization'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='outputactivity',
            name='deadline',
            field=models.IntegerField(default=-1, verbose_name=b'Deadline', choices=[(0, b'Ongoing'), (1, b'Q1'), (2, b'Q2'), (3, b'Q3'), (4, b'Q4'), (-1, b'No Deadline')]),
            preserve_default=True,
        ),
    ]
