from rest_framework import serializers  # 这一行注释掉会引入问题：动态创建表后，动态api文档中无法看到新建的表的api

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets

from utils.es import es
from utils import c_permissions
from . import views


def get_viewset(table):
    deleted_data_index = "{}..".format(table.name)

    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        try:
            res = es.search(index=deleted_data_index, doc_type="deleted-data", size=page_size, from_=(page-1)*page_size)
        except Exception as exc:
            raise exceptions.APIException("内部错误，错误类型： {}".format(type(exc)))
        return Response(res["hits"])

    viewset = type(
        f'{table.name}DeletedViewSet',
        (mixins.ListModelMixin, viewsets.GenericViewSet),
        dict(
            permission_classes=(c_permissions.TableLevelPermission, ),
            list=list,
            filter_backends=[],
        )
    )
    setattr(views, table.name, viewset)
    return viewset
