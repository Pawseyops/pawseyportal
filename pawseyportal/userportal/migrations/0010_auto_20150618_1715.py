# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0009_auto_20150618_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectperson',
            name='person',
        ),
        migrations.RemoveField(
            model_name='projectperson',
            name='project',
        ),
        migrations.AddField(
            model_name='allocation',
            name='people',
            field=models.ManyToManyField(to='userportal.Person'),
        ),
        migrations.DeleteModel(
            name='ProjectPerson',
        ),
    ]
