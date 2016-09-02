# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-02 06:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0006_auto_20160901_0709'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=100)),
                ('first_scene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adventure.Scene')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
