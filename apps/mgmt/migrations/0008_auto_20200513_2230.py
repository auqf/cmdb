# Generated by Django 3.0.6 on 2020-05-13 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0007_auto_20200513_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='order',
            field=models.IntegerField(default=0, help_text='标识此字段在表中的顺序，越小越靠前', verbose_name='顺序号'),
        ),
    ]