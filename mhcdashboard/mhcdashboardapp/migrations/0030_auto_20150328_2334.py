# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mhcdashboardapp', '0029_organizationactivity_other_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organization', models.ForeignKey(to='mhcdashboardapp.Organization')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'app_user',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='q1_comment',
            field=models.CharField(max_length=5000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='q2_comment',
            field=models.CharField(max_length=5000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='q3_comment',
            field=models.CharField(max_length=5000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='organizationactivity',
            name='q4_comment',
            field=models.CharField(max_length=5000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='output',
            name='comment',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
