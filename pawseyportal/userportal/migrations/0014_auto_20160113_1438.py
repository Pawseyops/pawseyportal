# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0013_auto_20151209_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='priorityarea',
            name='code',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='priorityarea',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='servicetype',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]
