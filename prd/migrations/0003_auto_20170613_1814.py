# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-13 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prd', '0002_auto_20170608_1610'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='build',
            options={'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='release',
            options={'ordering': ['-created']},
        ),
        migrations.AlterField(
            model_name='buildrevision',
            name='revision',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Git revision'),
        ),
    ]