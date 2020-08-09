import time
from functools import lru_cache

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from rest_framework import serializers

from utils import fields as c_fields


class User(AbstractUser):

    name = models.CharField(max_length=10, verbose_name="姓名")
    position = models.CharField(blank=True, max_length=20, verbose_name="职位")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def get_all_permissions_no_cache(self):
        perms = [p.codename for p in self.user_permissions.all()]
        perms = set(perms)
        return list(perms)

    @lru_cache()
    def _get_all_permissions_by_cache(self):
        return self.get_all_permissions_no_cache()

    def get_all_permission_names(self):
        if settings.PERMISSION_CACHE_TIME == 0 or settings.DEBUG:
            return self.get_all_permissions_no_cache()
        return self._get_all_permissions_by_cache()


class Table(models.Model):
    """
    动态表
    """
    name = models.CharField(
        primary_key=True, max_length=20, verbose_name="表名", help_text='表名')
    alias = models.CharField(
        max_length=20, unique=True, null=True, verbose_name="别名",
        help_text='别名')
    readme = models.TextField(
        blank=True, default="", verbose_name="自述", help_text='自述')
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name="创建者",
        help_text='创建者')
    creation_time = models.DateTimeField(
        auto_now_add=True, verbose_name="创建时间", help_text="创建时间")
    is_deleted = models.BooleanField(
        default=False, verbose_name='已删除', help_text='是否已删除(默认False)'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "表"
        verbose_name_plural = verbose_name


class Field(models.Model):
    """
    cmdb字段
    """
    FIELD_TYPE_CHOICES = ((0, "string"),
                          (1, "integer"),
                          (2, "floating"),
                          (3, "datetime"),
                          (4, "date"),
                          (5, "boolean"),
                          (6, "ip"),
                          (7, "image"),
                          (8, "attachment"),
                          (9, "text"),
                          )
    FIELD_TYPE_MAP = {
        0: serializers.CharField,
        1: serializers.IntegerField,
        2: serializers.FloatField,
        3: serializers.DateTimeField,
        4: serializers.DateField,
        5: c_fields.BooleanField,
        6: serializers.IPAddressField,
        7: serializers.CharField,
        8: serializers.CharField,
        9: serializers.CharField,
    }

    table = models.ForeignKey(
        Table, related_name="fields", verbose_name="所属表", help_text='所属表',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=20,
        verbose_name="字段名",
        help_text="字段名，规则：[a-z][a-z-0-9]*$"
    )
    type = models.SmallIntegerField(
        choices=FIELD_TYPE_CHOICES, verbose_name="字段类型",
        help_text=f'字段类型({FIELD_TYPE_CHOICES})'
    )
    alias = models.CharField(
        default="", max_length=20, null=True, blank=True, verbose_name="别名",
        help_text='别名(默认"")'
    )
    order = models.IntegerField(
        default=0, verbose_name="顺序号",
        help_text='标识此字段在表中的顺序，越小越靠前'
    )
    readme = models.TextField(
        null=True, blank=True, default="", verbose_name="自述",
        help_text='自述(默认"")'
    )
    required = models.BooleanField(
        default=False, verbose_name="必填", help_text='是否必填(默认False)'
    )
    is_multi = models.BooleanField(
        default=False, verbose_name="多值字段",
        help_text='是否为多值字段(默认False)'
    )
    is_deleted = models.BooleanField(
        default=False, verbose_name='已删除', help_text='是否已删除(默认False)'
    )
    extra_info = models.TextField(
        default=None, null=True, blank=True, verbose_name='额外信息',
        help_text='用于保存字段扩展信息，如可以一个json保存备选项，具体格式不限，与前端约定好即可')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "字段"
        verbose_name_plural = verbose_name
        unique_together = (("name", "table"),)


class RestPWVerifyCode(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    add_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "验证码"
        verbose_name_plural = verbose_name
