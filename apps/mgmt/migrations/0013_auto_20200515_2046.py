# Generated by Django 3.0.6 on 2020-05-15 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0012_field_extra_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='departments',
        ),
        migrations.RemoveField(
            model_name='user',
            name='permissions',
        ),
        migrations.DeleteModel(
            name='Department',
        ),
        migrations.DeleteModel(
            name='Permission',
        ),
    ]
