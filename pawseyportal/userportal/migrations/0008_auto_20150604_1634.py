# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0007_auto_20150604_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allocationfilesystem',
            name='quota',
            field=models.IntegerField(blank=True),
        ),
    ]
