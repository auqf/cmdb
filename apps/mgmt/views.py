
import logging
import datetime

from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import viewsets, serializers
from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import filters

from utils.serializers import EmptySerializer
from utils.verify_code import EmailVerifyCode
from utils.c_permissions import IsAdminCreate, IsAdminOrSelfChange, IsAdminOrReadOnly
from utils.c_pagination import CPageNumberPagination
from utils import c_permissions

from . import app_serializers
from . import models
from utils.es import es
from .service import DynamicTableManager


User = get_user_model()
email_verify_code = EmailVerifyCode()
logger = logging.getLogger("default")

# 验证码过期时间（秒）
MAX_AGE = settings.MAX_AGE


class TableViewset(viewsets.ModelViewSet):
    """
    动态表ViewSet
    list:
        查多条记录
    create:
        添加记录
    retrieve:
        查单条记录
    update:
        更新当前id记录
    partial_update:
        更新当前id部分记录
    delete:
        假删除
    reorder_fields:
        对表中的字段重新排序
    confirm_delete:
        #### 真删除
        此操作不可逆，仅超级用户可执行
        Query Parameters:
        table: 表name
    """
    queryset = models.Table.objects.filter(is_deleted=False).order_by(
        '-creation_time')
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = CPageNumberPagination
    search_fields = ['name', 'alias', 'readme', ]

    def get_serializer_class(self):
        if self.action == 'reorder_fields':
            return app_serializers.ReorderFieldsSerializer
        else:
            return app_serializers.TableSerializer

    def list(self, request, *args, **kwargs):
        has_read_perm = request.query_params.get("has_read_perm")
        if not has_read_perm:
            return super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        has_perm_tables = []
        perms = self.request.user.get_all_permission_names()
        for item in queryset:
            if item.name + ".read" in perms:
                has_perm_tables.append(item)
        data = {
            "count": len(has_perm_tables),
            "results": self.get_serializer(has_perm_tables, many=True).data
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        table = serializer.save()
        # initialize.add_table(table, create_index=True)
        DynamicTableManager.add_table(table)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=['post'])
    def reorder_fields(self, request, pk=None):
        fields = request.data.get('fields')

        field_qs = models.Field.objects.filter(table_id=pk)
        fields_cnt = field_qs.count()
        assert fields_cnt == len(fields), (
            f'必须传入全部字段，如：{list(field_qs.values_list("id", flat=True))}'
        )

        for i, field_id in enumerate(fields, start=1):
            models.Field.objects.filter(id=field_id).update(order=i*10)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def confirm_delete(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        table = request.query_params.get("table")
        if not table:
            raise exceptions.ParseError("此操作不可逆！请确认要删除的动态表name")
        instance = self.get_object()
        if table != instance.name:
            return Response(
                {"table": "动态表name错误"}, status=status.HTTP_400_BAD_REQUEST)
        DynamicTableManager.del_table(instance)
        logger.info(f"{request.user.username}删除了表{instance.name}")
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        models.Table.objects.filter(name=pk).update(is_deleted=False)
        return Response(status=status.HTTP_200_OK)


class UserViewset(viewsets.ModelViewSet):
    serializer_class = app_serializers.UserSerializer
    queryset = User.objects.all().order_by('-id')
    permission_classes = (
        permissions.IsAuthenticated, IsAdminCreate, IsAdminOrSelfChange)
    pagination_class = CPageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ("username", "email")

    def get_serializer_class(self):
        # if(settings.AUTH_LDAP_SERVER_URI and self.action!="get_my_info"):
        #     raise exceptions.ParseError("Please operate on LDAP server")
        if self.action == "change_password":
            return app_serializers.ChangePWSerializer
        elif self.action == "reset_password_admin":
            return app_serializers.RestPWAdminSerializer
        elif self.action == "reset_password_email":
            return app_serializers.RestPWEmailSerializer
        elif self.action == "send_verify_code":
            return app_serializers.SendVerifyCodeSerializer
        elif self.action == "get_my_info":
            return super().get_serializer_class()
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_superuser:
            raise exceptions.ParseError("Super user can not delete")
        if instance.table_set.exists():
            raise exceptions.ParseError("该用户创建过表 无法删除 请将其设置为禁用")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='change-password')
    def change_password(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, context={"request", request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Successfully modified!"})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='reset-password-admin')
    def reset_password_admin(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, context={"request", request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Reset successfully"})

    @action(detail=False, methods=['post'], permission_classes=[], url_path="send-verify-code")
    def send_verify_code(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, context={"request", request})
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        try:
            verify_code_inst = models.RestPWVerifyCode.objects.get(user__username=username)
        except models.RestPWVerifyCode.DoesNotExist:
            pass
        else:
            if datetime.datetime.now() - verify_code_inst.add_time < datetime.timedelta(seconds=60):
                raise exceptions.ParseError("Less than 60 seconds from last sent")
            verify_code_inst.delete()
        user = User.objects.get(username=username)
        if not user.email:
            raise exceptions.ParseError(f"{username} user does not have a email, please contact the administrator to"
                                        f" reset password")
        try:
            code = email_verify_code.send_verifycode(user.email)
        except Exception as exc:
            raise exceptions.ParseError("send failed, please try again later！")
        reset_pw_verify_code = models.RestPWVerifyCode(user=user, code=code)
        reset_pw_verify_code.save()
        return Response({"detail": "send successfully", "email": user.email})

    @action(detail=False, methods=['post'], permission_classes=[], url_path="reset-password-email")
    def reset_password_email(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, context={"request", request})
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        user = User.objects.get(username=username)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Reset successfully"})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path="get-my-info")
    def get_my_info(self, request, pk=None):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='reset-password-by-admin')
    def reset_password_by_admin(self, request, pk=None):
        instance = self.get_object()
        new_password = request.data.get("password")
        if not new_password:
            raise exceptions.ParseError("新密码不能为空")
        instance.set_password(new_password)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='update-password')
    def update_password(self, request, pk=None):
        instance = request.user
        new_password = request.data.get("password")
        if not new_password:
            raise exceptions.ParseError("新密码不能为空")
        instance.set_password(new_password)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="my-permission-names")
    def my_permission_names(self, request):
        perms = self.request.user.get_all_permission_names()
        data = {
            "count": len(perms),
            "results": perms
        }
        return Response(data)


class LdapUserViewset(viewsets.GenericViewSet):
    serializer_class = app_serializers.UserSerializer
    queryset = User.objects.all().order_by('-id')

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path="get-my-info")
    def get_my_info(self, request, pk=None):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class FieldViewSet(viewsets.ModelViewSet):
    """
    字段ViewSet
    list:
        查多条
    create:
        添加
    retrieve:
        查单条
    update:
        更新
    partial_update:
        部分更新
    delete:
        #### 删除
        请忽略下文中的 "Query Parameters"
    restore:
        还原（删除的逆操作)
    """
    # queryset = models.Field.objects.filter(is_deleted=False).order_by(
    queryset = models.Field.objects.all().order_by(
        'order', '-id')
    permission_classes = (c_permissions.IsAdminOrReadOnly, )
    filterset_fields = ['table', 'type', 'required', 'is_multi', 'is_deleted']
    search_fields = ['name', 'alias', 'readme', ]

    def get_serializer_class(self):
        if self.action in ['destroy', 'restore']:
            return EmptySerializer
        else:
            return app_serializers.FieldSerializer

    def perform_create(self, serializer):
        field = serializer.save()
        DynamicTableManager.add_field(field)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        DynamicTableManager.del_field(instance)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        models.Field.objects.filter(id=pk).update(is_deleted=False)
        return Response(status=status.HTTP_200_OK)
