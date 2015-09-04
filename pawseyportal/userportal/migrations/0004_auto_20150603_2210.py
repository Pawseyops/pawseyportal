# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userportal', '0003_auto_20150603_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetype',
            name='helpEmail',
            field=models.EmailField(default='t@test.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='allocation',
            name='name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='person',
            name='firstName',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='person',
            name='institutionEmail',
            field=models.EmailField(max_length=64),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='person',
            name='preferredEmail',
            field=models.EmailField(max_length=64),
        ),
        migrations.AlterField(
            model_name='person',
            name='surname',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='project',
            name='code',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='servicetype',
            name='name',
            field=models.CharField(max_length=32),
        ),
    ]
