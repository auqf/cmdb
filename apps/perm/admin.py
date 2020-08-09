from django.contrib import admin

from . import models


@admin.register(models.UserObjectPermission)
class UserObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'object_pk', 'permission', ]


@admin.register(models.GroupObjectPermission)
class GroupObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'object_pk', 'permission', ]
