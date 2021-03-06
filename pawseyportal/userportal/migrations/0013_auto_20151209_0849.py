# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command

def load_init_allocation_round(apps, schema_editor):
    # Initial Status Data
    fixture = 'initial_application_round_data'
    call_command('loaddata', fixture, app_label='userportal') 

class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0012_auto_20151020_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('name', models.CharField(max_length=512, null=True, blank=True)),
                ('priority_area', models.ManyToManyField(to='userportal.PriorityArea')),
                ('system', models.ForeignKey(to='userportal.Service')),
            ],
        ),
        migrations.RunPython(load_init_allocation_round),
        migrations.AlterField(
            model_name='allocation',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='project',
            name='title',
            field=models.CharField(max_length=256),
        ),
        migrations.AddField(
            model_name='allocation',
            name='allocation_round',
            field=models.ForeignKey(default=1, to='userportal.AllocationRound'),
            preserve_default=False,
        ),
    ]
