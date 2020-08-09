"""
动态表相关测试用例
"""
import json
import uuid

from mgmt.models import Table
from mgmt.tests.common import TestClassWithLogin


class TableTest(TestClassWithLogin):
    url = '/api/v1/mgmt/table/'

    @classmethod
    def create_table(cls, test_obj):
        """
        创建表
        :param test_obj: 用例对象
        :return: 表属性字典
        """
        table_name = f't{uuid.uuid1().hex}'[:20]
        print('table_name =', table_name)
        data = {
            'name': table_name,
            'alias': f'{table_name}',
            'readme': f'readme_{table_name}',
        }
        url = cls.url
        response = test_obj.client.post(url, data=data)
        test_obj.assertEqual(response.status_code, 201, msg=response)
        content = json.loads(response.content)
        test_obj.assertEqual(content['name'], table_name, msg=content)
        return content

    @classmethod
    def delete_table(cls, test_obj, table_name):
        """
        删除表
        :param test_obj: 用例对象
        :param table_name: 待删除表名
        :return:
        """
        url = cls.url
        del_url = f'{url}{table_name}/confirm_delete/?table={table_name}'
        response = test_obj.client.delete(del_url)
        test_obj.assertEqual(response.status_code, 204, msg=response)
        test_obj.assertFalse(Table.objects.filter(name=table_name).exists())

    def test_tables(self):
        # 创建表
        table = self.create_table(self)
        table_name = table['name']

        # 修改表
        data = {
            'name': table_name,
            'alias': 'mod_alias',
            'readme': 'mod_readme'
        }
        url = self.url
        put_url = f'{url}{table_name}/'
        response = self.client.put(put_url, data=data)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['alias'], 'mod_alias', msg=content)

        # 查所有表
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['count'], 1, msg=content)
        self.assertEqual(
            content['results'][0]['readme'], 'mod_readme', msg=content)

        # 删除表
        self.delete_table(self, table_name)

        # 查所有表
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['count'], 0, msg=content)
