# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-03 06:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0007_story'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='move',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='scene',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='story',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
    ]