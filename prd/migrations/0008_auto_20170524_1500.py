# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-24 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prd', '0007_auto_20170524_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotfix',
            name='jira',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Jira task for hotfix'),
        ),
    ]