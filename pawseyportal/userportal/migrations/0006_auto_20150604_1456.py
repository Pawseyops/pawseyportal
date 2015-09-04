# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0005_allocation_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='suspend',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='suspend',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='permanent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='institution',
            name='partner',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='person',
            name='student',
            field=models.BooleanField(default=False),
        ),
    ]
