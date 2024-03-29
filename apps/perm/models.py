from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .compat import user_model_label
from .ctypes import get_content_type
from .managers import GroupObjectPermissionManager, UserObjectPermissionManager


class BaseObjectPermission(models.Model):
    """
    Abstract ObjectPermission class. Actual class should additionally define
    a ``content_object`` field and either ``user`` or ``group`` field.
    """
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, verbose_name=_('Permissions'),
        help_text=_('Permissions')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return '{} | {}'.format(
            str(getattr(self, 'user', False) or self.group),
            str(self.permission.codename))

    # def save(self, *args, **kwargs):
    #     content_type = get_content_type(self.content_object)
    #     if content_type != self.permission.content_type:
    #         raise ValidationError("Cannot persist permission not designed for "
    #                               "this class (permission's type is %r and object's type is %r)"
    #                               % (self.permission.content_type, content_type))
    #     return super().save(*args, **kwargs)


class BaseGenericObjectPermission(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.CharField(_('object ID'), max_length=191)
    content_object = GenericForeignKey(fk_field='object_pk')

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['content_type', 'object_pk']),
        ]


class UserObjectPermissionBase(BaseObjectPermission):
    """
    **Manager**: :manager:`UserObjectPermissionManager`
    """
    user = models.ForeignKey(
        user_model_label, on_delete=models.CASCADE, verbose_name=_('user'),
        help_text=_('user')
    )

    objects = UserObjectPermissionManager()

    class Meta:
        abstract = True
        unique_together = ['user', 'permission', 'content_object']


class UserObjectPermission(UserObjectPermissionBase, BaseGenericObjectPermission):

    class Meta(UserObjectPermissionBase.Meta, BaseGenericObjectPermission.Meta):
        unique_together = ['user', 'permission', 'object_pk']
        verbose_name = _("User permissions")
        verbose_name_plural = verbose_name


class GroupObjectPermissionBase(BaseObjectPermission):
    """
    **Manager**: :manager:`GroupObjectPermissionManager`
    """
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, verbose_name=_('Groups'),
        help_text=_('Groups')
    )

    objects = GroupObjectPermissionManager()

    class Meta:
        abstract = True
        unique_together = ['group', 'permission', 'content_object']


class GroupObjectPermission(GroupObjectPermissionBase, BaseGenericObjectPermission):

    class Meta(GroupObjectPermissionBase.Meta, BaseGenericObjectPermission.Meta):
        unique_together = ['group', 'permission', 'object_pk']
        verbose_name = _("Group permissions")
        verbose_name_plural = verbose_name


setattr(Group, 'add_obj_perm',
        lambda self, perm, obj: GroupObjectPermission.objects.assign_perm(perm, self, obj))
setattr(Group, 'del_obj_perm',
        lambda self, perm, obj: GroupObjectPermission.objects.remove_perm(perm, self, obj))


# TODO: 针对 org 对象级权限
