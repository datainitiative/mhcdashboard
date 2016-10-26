# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mhcdashboardapp', '0032_auto_20160412_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='has_temp_access',
            field=models.IntegerField(default=0, verbose_name=b'Temporary Access?', choices=[(1, b'Yes'), (0, b'No')]),
        ),
        migrations.AddField(
            model_name='myuser',
            name='temp_access_expire',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='output',
            name='active_quarter',
            field=models.ForeignKey(default=4, verbose_name=b'Reporting Quarter', to='mhcdashboardapp.ActiveQuarter', null=True),
        ),
    ]
