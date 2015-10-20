# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.management import call_command

def load_init_status(apps, schema_editor):
    # Initial Status Data
        fixture = 'initial_data'
        call_command('loaddata', fixture, app_label='userportal') 

class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0011_auto_20150618_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of your email template', max_length=100)),
                ('subject', models.CharField(help_text=b'The subject header for emails sent using this template', max_length=100)),
                ('template', models.CharField(help_text=b'Your email template body in Django templating syntax', max_length=8192, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PersonStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=256, null=True, blank=True)),
            ],
        ),
        migrations.RunPython(load_init_status),
        migrations.RemoveField(
            model_name='person',
            name='suspend',
        ),
        migrations.AddField(
            model_name='person',
            name='accountCreatedEmailOn',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='accountCreatedOn',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='accountEmailHash',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='accountEmailOn',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='status',
            field=models.ForeignKey(default=1, to='userportal.PersonStatus'),
        ),
    ]
