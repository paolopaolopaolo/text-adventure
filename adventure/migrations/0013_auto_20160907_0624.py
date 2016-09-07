# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-07 06:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0012_agent_is_boss'),
    ]

    operations = [
        migrations.AddField(
            model_name='scene',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='scene',
            name='unlocking_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unlocking_scenes', to='adventure.Inventory'),
        ),
    ]
