# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-09 03:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0013_auto_20160907_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='found_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='scene_items', to='adventure.Scene'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='agent_items', to='adventure.Agent'),
        ),
    ]