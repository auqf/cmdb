from django.contrib import admin

from utils import models as c_models

from . import models


@admin.register(models.Table)
class TableAdmin(admin.ModelAdmin):
    list_display = c_models.get_all_field_name(models.Table)
    list_display_links = ("name",)
    search_fields = ("name", "alias")
    list_per_page = 10


@admin.register(models.Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = c_models.get_all_field_name(models.Field)
    list_display_links = ("id",)
    list_per_page = 10


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = c_models.get_all_field_name(models.User)
    list_display_links = ("id", )
    search_fields = ("username", "name", )
    list_per_page = 10


@admin.register(models.RestPWVerifyCode)
class RestPWVerifyCodeAdmin(admin.ModelAdmin):
    list_display = c_models.get_all_field_name(models.RestPWVerifyCode)
    list_display_links = ("id", )
    search_fields = ("user__username", "user__name", "code")
    list_per_page = 10
