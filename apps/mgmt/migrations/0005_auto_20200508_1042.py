# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-05-08 10:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0004_auto_20200507_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='alias',
            field=models.CharField(help_text='别名', max_length=20, null=True, unique=True, verbose_name='别名'),
        ),
        migrations.AlterField(
            model_name='table',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='table',
            name='creator',
            field=models.ForeignKey(help_text='创建者', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='table',
            name='name',
            field=models.CharField(help_text='表名', max_length=20, primary_key=True, serialize=False, verbose_name='表名'),
        ),
        migrations.AlterField(
            model_name='table',
            name='readme',
            field=models.TextField(blank=True, default='', help_text='自述', verbose_name='自述'),
        ),
    ]
