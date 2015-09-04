# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('partner', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstName', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=50)),
                ('institutionEmail', models.EmailField(max_length=50)),
                ('preferredEmail', models.EmailField(max_length=50)),
                ('phone', models.CharField(max_length=20)),
                ('student', models.BooleanField()),
                ('institution', models.ForeignKey(to='userportal.Institution')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('summary', models.TextField()),
                ('principleInvestigator', models.ForeignKey(to='userportal.Person')),
            ],
        ),
    ]
