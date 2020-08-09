
"""
children1987
2020-05-07
"""
from importlib import import_module, reload

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import clear_url_caches
from elasticsearch import NotFoundError
from rest_framework.routers import SimpleRouter

import data
import deleted_data
import record_data
from mgmt.models import Table
from utils.es import Mapping, indices_client


class DynamicTableManager(object):
    """
    动态表管理器

    核心数据样例：
    _table_info_s = {
        'table_1': {
            'data': {
                'router': <router_obj>,
            },
            'record_data': {
                'router': <router_obj>,
            },
            'deleted_data': {
                'router': <router_obj>,
            },
        },
        ...
    }
    """
    _table_info_s = {}

    @classmethod
    def on_django_start(cls):
        """
        启动时，初始化所有动态表，主要是加载 api
        :return:
        """
        tables = Table.objects.all()
        for table in tables:
            cls._table_info_s[table.name] = {
                'data': {},
                'record_data': {},
                'deleted_data': {},
            }
            cls._update_urls(table)

    @classmethod
    def add_table(cls, table):
        """
        新增一张表
        :param table: Table 模型对象
        :return:
        """
        cls._table_info_s[table.name] = {
            'data': {},
            'record_data': {},
            'deleted_data': {},
        }

        data_mapping = Mapping.generate_data_mapping(table)
        record_mapping = Mapping.generate_record_data_mapping(table)
        delete_mapping = Mapping.generate_deleted_data_mapping(table)
        cls._add_index(table.name, data_mapping)
        cls._add_index(table.name + ".", record_mapping)
        cls._add_index(table.name + "..", delete_mapping)

        # 更新urls
        cls._update_urls(table)
        cls._refresh_urls()

        # 创建ContentType
        ct, _ = ContentType.objects.get_or_create(
            app_label='mgmt', model=table.name)

        # 创建权限
        name_suffixes = table.alias if table.alias else table.name
        Permission.objects.update_or_create(
            codename=f'view_{table.name}',
            defaults={
                'name': f'能查看{name_suffixes}',
                'content_type': ct,
            }
        )
        Permission.objects.update_or_create(
            codename=f'change_{table.name}',
            defaults={
                'name': f'能改写{name_suffixes}',
                'content_type': ct,
            }
        )
        Permission.objects.update_or_create(
            codename=f'add_{table.name}',
            defaults={
                'name': f'能添加{name_suffixes}',
                'content_type': ct,
            }
        )
        Permission.objects.update_or_create(
            codename=f'delete_{table.name}',
            defaults={
                'name': f'能删除{name_suffixes}',
                'content_type': ct,
            }
        )

    @staticmethod
    def _refresh_urls():
        clear_url_caches()
        reload(import_module(settings.ROOT_URLCONF))

    @classmethod
    def del_table(cls, table):
        """
        删除一个动态表
        :param table: Table 模型对象
        :return:
        """
        cls._del_api_s(table)

        # 更新urls
        cls._refresh_urls()

        # 删除ES index
        cls._del_index(table.name)
        cls._del_index(table.name + ".")
        cls._del_index(table.name + "..")

        # 删除ContentType，并级联删除权限
        ContentType.objects.filter(app_label='mgmt', model=table.name).delete()

    @classmethod
    def mod_table(cls, table):
        """
        编辑动态表
        :param table: Table 模型对象
        :return:
        """

    @classmethod
    def add_field(cls, field):
        """
        新增一个字段
        :param field: Field 模型对象
        :return:
        """

        field_mapping = Mapping.generate_field_mapping(field)

        # 主记录
        indices_client.put_mapping(
            doc_type='data',
            index=field.table.name,
            body={"properties": field_mapping}
        )
        data.initialize.update_viewset(field.table)

        # 修改记录
        indices_client.put_mapping(
            doc_type='data',
            index=f'{field.table.name}.',
            body={"properties": field_mapping}
        )
        # record_data.initialize.update_viewset(field.table)

        # 删除记录
        indices_client.put_mapping(
            doc_type='data',
            index=f'{field.table.name}..',
            body={"properties": field_mapping}
        )
        # deleted_data.initialize.update_viewset(field.table)

    @staticmethod
    def del_field(field):
        """
        删除一个字段
        :param field: Field 模型对象
        :return:
        """
        data.initialize.update_viewset(field.table)

    @classmethod
    def mod_field(self, field):
        """
        编辑字段
        :param field: Field 模型对象
        :return:
        """

    @staticmethod
    def _add_index(table_name, mapping):
        body = {
            "settings": {
                "index": {
                    "number_of_shards": 3,
                    "number_of_replicas": 0
                }
            },
            "mappings": {
                "data": {
                    "properties": mapping
                }
            }
        }
        indices_client.create(index=table_name, body=body)

    @staticmethod
    def _del_index(table_name):
        try:
            indices_client.delete(index=table_name)
        except NotFoundError:
            return

    @classmethod
    def _update_url(cls, app, table):
        viewset = app.initialize.get_viewset(table)
        router = SimpleRouter()
        router.register(table.name, viewset, basename=table.name)
        cls._table_info_s[table.name][app.__name__]['router'] = router
        urls = router.urls
        app.urls.urlpatterns.extend(urls)

    @classmethod
    def _update_urls(cls, table):
        """
        更新url
        :param table: Table 模型的对象
        :return: None
        """
        # 未知原因导致 manage.py runserver 时， 2次调用了 on_ready，这里暂时这样处理
        # if table.name in _router_map:
        #     return
        cls._update_url(data, table)
        cls._update_url(record_data, table)
        cls._update_url(deleted_data, table)

    @classmethod
    def _del_api_s(cls, table):
        cls._del_api(data, table)
        cls._del_api(record_data, table)
        cls._del_api(deleted_data, table)

    @classmethod
    def _del_api(cls, app, table):
        try:
            router = cls._table_info_s[table.name][app.__name__]['router']
        except KeyError:
            return

        for url in router.urls:
            app.urls.urlpatterns.remove(url)
