# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-05-07 20:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0003_auto_20200430_2020'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='table',
            options={'ordering': ['-creation_time'], 'verbose_name': '表', 'verbose_name_plural': '表'},
        ),
        migrations.AlterField(
            model_name='field',
            name='table',
            field=models.ForeignKey(help_text='所属表', on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='mgmt.Table', verbose_name='所属表'),
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together=set([('name', 'table')]),
        ),
    ]