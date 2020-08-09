# Generated by Django 3.0.6 on 2020-05-19 19:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
        ('perm', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupobjectpermission',
            options={'verbose_name': 'Group permissions', 'verbose_name_plural': 'Group permissions'},
        ),
        migrations.AlterModelOptions(
            name='userobjectpermission',
            options={'verbose_name': 'User permissions', 'verbose_name_plural': 'User permissions'},
        ),
        migrations.AlterField(
            model_name='groupobjectpermission',
            name='group',
            field=models.ForeignKey(help_text='Groups', on_delete=django.db.models.deletion.CASCADE, to='auth.Group', verbose_name='Groups'),
        ),
        migrations.AlterField(
            model_name='groupobjectpermission',
            name='permission',
            field=models.ForeignKey(help_text='Permissions', on_delete=django.db.models.deletion.CASCADE, to='auth.Permission', verbose_name='Permissions'),
        ),
        migrations.AlterField(
            model_name='userobjectpermission',
            name='permission',
            field=models.ForeignKey(help_text='Permissions', on_delete=django.db.models.deletion.CASCADE, to='auth.Permission', verbose_name='Permissions'),
        ),
        migrations.AlterField(
            model_name='userobjectpermission',
            name='user',
            field=models.ForeignKey(help_text='user', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
    ]
