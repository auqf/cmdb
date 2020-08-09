from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsAdminCreate(BasePermission):
    def has_permission(self, request, view):
        return view.action not in ["list", "create"] or request.user.is_staff


class IsAdminOrSelfChange(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and request.user.is_staff
        )


class TableLevelPermission(BasePermission):

    @staticmethod
    def get_perm_codename(request, view):
        permission_name = view.__class__.__name__
        if request.method in SAFE_METHODS:
            perm_type = 'view'
        else:
            perm_type = 'change'
        return f'{perm_type}_{permission_name}'

    def has_permission(self, request, view):
        if request.user.is_staff or request.method == "OPTIONS":
            return True
        perms = request.user.get_all_permission_names()
        perm_codename = self.get_perm_codename(request, view)
        return perm_codename in perms


class ObjectLevelPermission(TableLevelPermission):
    """
    The request is authenticated using Django's object-level permissions.
    It requires an object-permissions-enabled backend, such as Django Guardian.

    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete` permissions on the object using .has_perms.

    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.change_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.change_%(model_name)s'],
    }

    def has_permission(self, request, view):
        has_table_level_perm = super().has_permission(request, view)
        if has_table_level_perm:
            return True

        if not view.detail:
            return False

        # 检查对象级权限
        obj_id = view.kwargs[view.lookup_field]
        return self.has_object_permission(request, view, obj_id)

    def get_required_object_permissions(self, method, model_cls):
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def has_object_permission(self, request, view, obj_id):
        perm_codename = self.get_perm_codename(request, view)
        from django.contrib.auth.models import Permission
        perm_obj = Permission.objects.get(codename=perm_codename)
        from perm.models import UserObjectPermission
        if not UserObjectPermission.objects.filter(
                object_pk=obj_id,
                permission=perm_obj,
                user=request.user).exists():
            raise PermissionDenied()
        return True
