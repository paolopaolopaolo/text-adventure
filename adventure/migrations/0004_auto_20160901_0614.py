# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-01 06:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0003_move_special_move'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='effect_magnitude',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='type',
            field=models.CharField(choices=[('HP', 'HP Effect'), ('MP', 'MP Effect'), ('AD', 'Attack Damage Effect'), ('SAD', 'Special Attack Damage Effect')], default='HP', max_length=3),
            preserve_default=False,
        ),
    ]
