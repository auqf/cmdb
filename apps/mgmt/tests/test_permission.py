"""
表级权限相关测试用例
"""
import json
import time

from django.conf import settings

from django.contrib.auth.models import Permission

from mgmt.models import Table
from mgmt.tests.common import TestClassWithBaseData
from perm.models import UserObjectPermission


class PermTest(TestClassWithBaseData):
    url = '/api/v1/data/'

    @staticmethod
    def create_user_table_perm(user, table, perm):
        """
        创建一个用户的表操作权限
        :param user: user 模型对象
        :param table: table 模型对象
        :param perm: valid in ['change', 'view']
        """
        # 禁用权限缓存
        settings.PERMISSION_CACHE_TIME = 0
        perm_key = f'{perm}_{table.name}'
        perm = Permission.objects.get(codename=perm_key)
        user.user_permissions.add(perm)

    @staticmethod
    def create_user_object_perm(user, table, obj_id, perm):
        """
        创建一个用户的表操作权限
        :param user: user 模型对象
        :param table: table 模型对象
        :param obj_id: 对象id
        :param perm: valid in ['change', 'view']
        """
        # 禁用权限缓存
        settings.PERMISSION_CACHE_TIME = 0
        perm_key = f'{perm}_{table.name}'
        UserObjectPermission.objects.assign_perm(perm_key, user, table, obj_id)

    @staticmethod
    def delete_user_object_perm(user, table, obj_id, perm):
        """
        创建一个用户的表操作权限
        :param user: user 模型对象
        :param table: table 模型对象
        :param obj_id: 对象id
        :param perm: valid in ['change', 'view']
        """
        # 禁用权限缓存
        settings.PERMISSION_CACHE_TIME = 0
        perm_key = f'{perm}_{table.name}'
        UserObjectPermission.objects.remove_perm(perm_key, user, table, obj_id)

    def test_table_perm(self):
        """
        测试表级权限
        """
        # 超级用户a登录
        self.t_user_login(self.test_super_user)

        # 创建表t1
        from mgmt.tests.test_table import TableTest
        table = TableTest.create_table(self)
        table_name = table['name']

        # 创建2个字段
        from mgmt.tests.test_field import FieldTest
        FieldTest.create_field(self, table_name, name='k1', type_=0)

        # 创建1条记录
        from mgmt.tests.test_record import RecordTest
        data = {'k1': 'r1k1'}
        RecordTest.create_record(self, table_name, data)

        # a登出
        self.t_user_logout()

        # 普通用户b登录
        self.t_user_login(self.test_common_user)

        # b查表t1失败
        url = f'{self.url}{table_name}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403, msg=response)

        # 授权b可读t1
        table_obj = Table.objects.get(name=table_name)
        self.create_user_table_perm(self.test_common_user, table_obj, 'view')

        # b查表t1成功
        url = f'{self.url}{table_name}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)

        # b写1条t1表记录失败
        data = {'k1': 'r2k1'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403, msg=response)

        # 授权b可写t1
        self.create_user_table_perm(self.test_common_user, table_obj, 'change')

        # b写1条t1表记录成功
        data = {'k1': 'r3k1'}
        RecordTest.create_record(self, table_name, data)
        time.sleep(1)  # 写ElasticSearch操作较慢，需要等待

        # b查到2条记录
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['total'], 2, msg=content)

        # b登出
        self.t_user_logout()

        # a登录
        self.t_user_login(self.test_super_user)

        # 删除表
        TableTest.delete_table(self, table_name)

    def test_object_perm(self):
        """
        测试对象级权限
        """
        # 超级用户a登录
        self.t_user_login(self.test_super_user)

        # 创建表t1
        from mgmt.tests.test_table import TableTest
        table = TableTest.create_table(self)
        table_name = table['name']
        table_obj = Table.objects.get(name=table_name)

        # 创建2个字段
        from mgmt.tests.test_field import FieldTest
        FieldTest.create_field(self, table_name, name='k1', type_=0)

        # 创建1条记录
        from mgmt.tests.test_record import RecordTest
        data = {'k1': 'r1k1'}
        obj = RecordTest.create_record(self, table_name, data)
        obj_id = obj['_id']

        # a登出
        self.t_user_logout()

        # 普通用户b登录
        self.t_user_login(self.test_common_user)

        # b查表 obj 失败
        url = f'{self.url}{table_name}/{obj_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403, msg=response)

        # 授权b可读 obj
        self.create_user_object_perm(
            self.test_common_user, table_obj, obj_id, 'view')

        # b查表 obj 成功
        url = f'{self.url}{table_name}/{obj_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)

        # b 改写 obj 失败
        data = {'k1': 'r2k1'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403, msg=response)

        # 授权 b 可写 obj
        self.create_user_object_perm(
            self.test_common_user, table_obj, obj_id, 'change')

        # b 改写 obj 成功
        data = {'k1': 'r3k1'}
        RecordTest.update_record(self, table_name, obj_id, data)
        time.sleep(1)  # 写ElasticSearch操作较慢，需要等待

        # 取消授权 b 可写 obj
        self.delete_user_object_perm(
            self.test_common_user, table_obj, obj_id, 'change')

        # b 改写 obj 失败
        data = {'k1': 'r3k1'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403, msg=response)

        # b登出
        self.t_user_logout()

        # a登录
        self.t_user_login(self.test_super_user)

        # 删除表
        TableTest.delete_table(self, table_name)
