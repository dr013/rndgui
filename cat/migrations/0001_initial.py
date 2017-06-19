# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TestEnvironment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Name')),
                ('expire', models.CharField(default=120, max_length=200, verbose_name='Expire time')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('env', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='envrnmnt.Environment', verbose_name='Environment')),
                ('prd', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='prd.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='UsageLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('completed', 'Completed'), ('busy', 'Busy'), ('fail', 'Failed')], default='busy', max_length=200, verbose_name='Statuses')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Start time')),
                ('finished_at', models.DateTimeField(blank=True, null=True, verbose_name='Finish time')),
                ('task', models.CharField(blank=True, max_length=200, null=True, verbose_name='Task')),
                ('hash', models.CharField(editable=False, max_length=10, unique=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prd.Release', verbose_name='Release')),
                ('stand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cat.TestEnvironment', verbose_name='Environment')),
            ],
        ),
    ]
