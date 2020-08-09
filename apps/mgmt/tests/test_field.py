"""
字段相关测试用例
"""
import json
import uuid

from mgmt.models import Field
from mgmt.tests.common import TestClassWithLogin


class FieldTest(TestClassWithLogin):
    url = '/api/v1/mgmt/field/'

    @classmethod
    def create_field(
            cls, test_obj, table_name, name=None, alias=None, readme='',
            type_=0, is_multi=None, required=None):
        """
        创建1个字段
        :param test_obj: 用例对象
        :param table_name: 所属表表名
        :param name: 字段名
        :param alias: 别名
        :param readme: 自述
        :param type_: 字段类型(((0, 'string'), (1, 'integer'), (2, 'floating'),
            (3, 'datetime'), (4, 'date'), (5, 'boolean'), (6, 'Ip')))
        :param is_multi: 是否为多值字段
        :param required: 是否必填
        :return: 字段属性字典
        """
        if not name:
            name = f'f{uuid.uuid1().hex}'[:20]

        print('field_name =', name)
        data = {
            'name': name,
            'alias': alias if alias else name,
            'readme': readme,
            'type': type_ if type_ else 0,
            'is_multi': is_multi if is_multi else False,
            'required': required if required else False,
            'table': table_name,
        }
        url = cls.url
        response = test_obj.client.post(url, data=data)
        test_obj.assertEqual(response.status_code, 201, msg=response)
        content = json.loads(response.content)
        test_obj.assertEqual(content['name'], name, msg=content)
        return content

    @classmethod
    def delete_field(cls, test_obj, field_id):
        """
        删除字段
        :param test_obj: 用例对象
        :param field_id: 字段id
        :return:
        """
        url = cls.url
        del_url = f'{url}{field_id}/'
        response = test_obj.client.delete(del_url)
        test_obj.assertEqual(response.status_code, 204, msg=response)
        test_obj.assertTrue(Field.objects.get(id=field_id).is_deleted)

    def test_fields(self):
        from mgmt.tests.test_table import TableTest
        # 创建表
        table = TableTest.create_table(self)
        table_name = table['name']

        # 创建7个字段（各类型各一个）
        self.create_field(self, table_name, name='f-ip', type_=6)
        type_cnt = 9
        for i in range(type_cnt)[::-1]:
            field = self.create_field(self, table_name, type_=i)

        # 修改 type=0 的字段
        url = self.url
        field_id = field["id"]
        put_url = f'{url}{field_id}/'
        response = self.client.patch(put_url, data={'readme': 'xxx'})
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['readme'], 'xxx', msg=content)
        self.assertEqual(content['type'], 0, msg=content)

        # 删除 type=0 的字段
        self.delete_field(self, field_id)

        # 查这个表的所有字段
        url = self.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(len(content), type_cnt, msg=content)
        self.assertEqual(
            content[-1]['name'], 'f-ip', msg=content)

        # 删除表
        TableTest.delete_table(self, table_name)
