import operator
import uuid
import datetime

from elasticsearch.exceptions import NotFoundError, ConflictError
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets

from utils import c_permissions
from utils.es import es
from . import views


def _get_serializer(table):
    fields = table.fields.filter(is_deleted=False)
    attributes = {}
    for field in fields:
        args = {
            "label": field.alias,
            'help_text': field.readme,
            'required': field.required,
        }
        if not field.required:
            args["default"] = None
            args["allow_null"] = True
        if field.type == 3:
            args["format"] = "%Y-%m-%dT%H:%M:%S"
        elif field.type == 6:
            args["protocol"] = "IPv4"

        from mgmt.models import Field
        field_type_map = Field.FIELD_TYPE_MAP
        f = field_type_map[field.type](**args)
        if field.is_multi:
            attributes[field.name] = serializers.ListField(
                child=f, allow_empty=not field.required)
        else:
            attributes[field.name] = f

    #创建者拿到视图aQ!
    attributes["S-creator"] = serializers.CharField(
        read_only=True, default=serializers.CurrentUserDefault())
    attributes["S-creation-time"] = serializers.DateTimeField(
        read_only=True,
        format="%Y-%m-%dT%H:%M:%S",
        default=datetime.datetime.now)
    attributes["S-last-modified"] = serializers.CharField(
        default=None, allow_null=True, read_only=True, label="最后修改人")
    serializer = type(table.name, (Serializer, ), attributes)
    return serializer


def del_viewset(table):
    """
    :param table:
    :return:
    """
    delattr(views, table.name)


def update_viewset(table):
    """
    更新 viewset
    :param table:
    :return:
    """
    serializer_class = _get_serializer(table)
    viewset = getattr(views, table.name)
    viewset.serializer_class = serializer_class


def get_viewset(table):
    data_index = table.name
    record_data_index = "{}.".format(table.name)
    deleted_data_index = "{}..".format(table.name)

    def list(self, request, *args, **kwargs):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        res = es.search(
            index=data_index,
            doc_type="data",
            size=page_size,
            from_=(page-1)*page_size
        )
        return Response(res["hits"])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        data["S-creator"] = request.user.username
        try:
            res = es.create(
                index=data_index,
                doc_type="data",
                id=uuid.uuid1().hex,
                body=data
            )
        except ConflictError as exc:
            raise exceptions.ParseError("Document is exists")
        headers = self.get_success_headers(serializer.data)
        return Response(res, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        try:
            res = es.get(index=data_index, doc_type="data", id=kwargs["pk"])
        except NotFoundError as exc:
            raise exceptions.NotFound(
                "Document {} was not found in Type {} of Index {}".format(
                    kwargs["pk"],"data", data_index))
        return Response(res)

    def update(self, request, *args, **kwargs):
        try:
            res = es.get(index=data_index, doc_type="data", id=kwargs["pk"])
        except NotFoundError as exc:
            raise exceptions.NotFound(
                "Document {} was not found in Type {} of Index {}".format(
                    kwargs["pk"], "data", data_index))
        old_serializer = self.get_serializer(data=res["_source"])
        old_serializer.is_valid()
        old_data = old_serializer.validated_data

        partial = kwargs.get("partial", False)
        delta_serializer = self.get_serializer(
            data=request.data, partial=partial)
        delta_serializer.is_valid(raise_exception=True)

        # 构造待比较的新数据 new_data = old_data + delta_data
        new_data = old_data.copy()
        new_data.update(delta_serializer.validated_data)

        # 新老数据一致时抛异常
        if operator.eq(new_data, old_data):
            raise exceptions.ParseError(detail="No field changed")

        # 保存历史记录
        old_data["S-data-id"] = kwargs["pk"]
        old_data["S-changer"] = request.user.username
        old_data["S-update-time"] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S")
        es.index(
            index=record_data_index,
            doc_type="record-data",
            id=uuid.uuid1().hex,
            body=old_data
        )

        # 构造新数据
        new_data.update({"S-last-modified": request.user.username})

        # 保存新数据
        res = es.index(
            index=data_index,
            doc_type="data",
            id=kwargs["pk"],
            body=new_data
        )
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        try:
            res = es.get(index=data_index, doc_type="data", id=kwargs["pk"])
            data = res["_source"]
            data.pop("S-last-modified")
            data["S-delete-time"] = datetime.datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S")
            data["S-delete-people"] = request.user.username
            res = es.create(
                index=deleted_data_index,
                doc_type="deleted-data",
                id=kwargs["pk"],
                body=data
            )
            es.delete(index=data_index, doc_type="data", id=kwargs["pk"])
            es.delete_by_query(
                index=record_data_index,
                doc_type="record-data",
                body={"query": {"term": {"S-data-id": kwargs["pk"]}}}
            )
        except NotFoundError as exc:
            raise exceptions.ParseError(
                "Document {} was not found in Type {} of Index {}".format(
                    kwargs["pk"],"data", table.name))
        return Response(res, status=status.HTTP_204_NO_CONTENT)

    serializer_class = _get_serializer(table)
    viewset = type(
        table.name,
        (
            mixins.ListModelMixin,
            mixins.CreateModelMixin,
            mixins.RetrieveModelMixin,
            mixins.UpdateModelMixin,
            mixins.DestroyModelMixin,
            viewsets.GenericViewSet
        ),
        dict(
            serializer_class=serializer_class,
            permission_classes=(
                c_permissions.ObjectLevelPermission,
            ),
            list=list,
            create=create,
            retrieve=retrieve,
            update=update,
            destroy=destroy,
            filter_backends=[],
        )
    )
    setattr(views, table.name, viewset)
    return viewset
