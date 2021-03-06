# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 10:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DBInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=200, verbose_name='Host')),
                ('sid', models.CharField(blank=True, default='SV', max_length=20, null=True, verbose_name='SID')),
                ('port', models.IntegerField(default=1521, verbose_name='Port')),
                ('login', models.CharField(max_length=200, verbose_name='DB Login')),
                ('passwd', models.CharField(max_length=200, verbose_name='DB Password')),
                ('sys_user', models.CharField(blank=True, default='system', max_length=200, null=True, verbose_name='System Login')),
                ('sys_passwd', models.CharField(blank=True, default='SYSTEM1', max_length=200, null=True, verbose_name='System Password')),
                ('weight', models.CharField(choices=[('Big', 'For SmartVista project - 30 Gb'), ('Medium', 'For SMSGate, SSO projects - 5 Gb'), ('Small', 'For other project - less 1 Gb')], max_length=200, verbose_name='Weight')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('release_part', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='prd.ReleasePart')),
            ],
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('inst', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='acm.Institution', verbose_name='Group')),
            ],
        ),
        migrations.CreateModel(
            name='STLNInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=200, verbose_name='Host')),
                ('port', models.IntegerField(default=22, verbose_name='Port')),
                ('user', models.CharField(default='svfe', max_length=200, verbose_name='User')),
                ('passwd', models.CharField(max_length=200, verbose_name='Password')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('release_part', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='prd.ReleasePart')),
            ],
        ),
        migrations.CreateModel(
            name='WEBInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=200, verbose_name='Host')),
                ('port', models.IntegerField(default=7001, verbose_name='Port')),
                ('target_server', models.CharField(max_length=200, verbose_name='Server')),
                ('login', models.CharField(default='weblogic', max_length=200, verbose_name='Login')),
                ('passwd', models.CharField(max_length=200, verbose_name='Password')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('release_part', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='prd.ReleasePart')),
            ],
        ),
    ]
