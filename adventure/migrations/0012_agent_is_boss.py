# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-05 03:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0011_auto_20160904_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='is_boss',
            field=models.BooleanField(default=False),
        ),
    ]
