# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0015_person_mobilephone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='mobilePhone',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='personAccount',
            field=models.ForeignKey(related_name='person', blank=True, to='userportal.PersonAccount', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='preferredEmail',
            field=models.EmailField(max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='personaccount',
            name='gidNumber',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='personaccount',
            name='uid',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='personaccount',
            name='uidNumber',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='code',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='summary',
            field=models.TextField(null=True, blank=True),
        ),
    ]
