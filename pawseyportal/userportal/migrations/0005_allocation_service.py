# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0004_auto_20150603_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='service',
            field=models.ForeignKey(default=1, to='userportal.Service'),
            preserve_default=False,
        ),
    ]
