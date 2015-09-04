# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0008_auto_20150604_1634'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=256)),
                ('uidNumber', models.IntegerField()),
                ('gidNumber', models.IntegerField()),
                ('passwordHash', models.CharField(max_length=256, null=True, verbose_name=b'password', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectPerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('person', models.ForeignKey(to='userportal.Person')),
                ('project', models.ForeignKey(to='userportal.Project')),
            ],
        ),
        migrations.AlterField(
            model_name='allocationfilesystem',
            name='quota',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='person',
            name='personAccount',
            field=models.ForeignKey(related_name='person', to='userportal.PersonAccount', null=True),
        ),
    ]
