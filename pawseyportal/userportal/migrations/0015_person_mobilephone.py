# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0014_auto_20160113_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='mobilePhone',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
