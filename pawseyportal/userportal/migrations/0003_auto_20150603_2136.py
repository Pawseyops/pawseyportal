# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0002_auto_20150603_2012'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('permanent', models.BooleanField()),
                ('serviceunits', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PriorityArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('code', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='type',
            field=models.ForeignKey(to='userportal.ServiceType'),
        ),
        migrations.AddField(
            model_name='allocation',
            name='priorityArea',
            field=models.ForeignKey(to='userportal.PriorityArea'),
        ),
        migrations.AddField(
            model_name='allocation',
            name='project',
            field=models.ForeignKey(to='userportal.Project'),
        ),
    ]
