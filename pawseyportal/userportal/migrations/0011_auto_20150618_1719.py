# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0010_auto_20150618_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allocation',
            name='people',
        ),
        migrations.AddField(
            model_name='project',
            name='people',
            field=models.ManyToManyField(to='userportal.Person'),
        ),
        migrations.AlterField(
            model_name='project',
            name='principalInvestigator',
            field=models.ForeignKey(related_name='pi', to='userportal.Person'),
        ),
    ]
