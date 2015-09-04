# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0006_auto_20150604_1456'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationFilesystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quota', models.IntegerField()),
                ('allocation', models.ForeignKey(to='userportal.Allocation')),
            ],
        ),
        migrations.CreateModel(
            name='Filesystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('quotad', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='allocationfilesystem',
            name='filesystem',
            field=models.ForeignKey(to='userportal.Filesystem'),
        ),
    ]
