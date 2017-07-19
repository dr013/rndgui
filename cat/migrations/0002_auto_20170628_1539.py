# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-28 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cat', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='releasecarousel',
            options={'ordering': ['-is_active', 'count', 'last_used_at', 'sort'], 'permissions': (('can_order', 'Manual order priority'),)},
        ),
        migrations.AddField(
            model_name='releasecarousel',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active'),
        ),
    ]
