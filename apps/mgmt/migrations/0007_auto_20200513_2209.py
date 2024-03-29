# Generated by Django 3.0.6 on 2020-05-13 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0006_auto_20200513_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='是否已删除(默认False)', verbose_name='已删除'),
        ),
        migrations.AlterField(
            model_name='field',
            name='is_multi',
            field=models.BooleanField(default=False, help_text='是否为多值字段(默认False)', verbose_name='多值字段'),
        ),
        migrations.AlterField(
            model_name='field',
            name='required',
            field=models.BooleanField(default=False, help_text='是否必填(默认False)', verbose_name='必填'),
        ),
    ]
