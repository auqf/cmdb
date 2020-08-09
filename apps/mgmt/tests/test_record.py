"""
记录相关测试用例
"""
import json
import time

from mgmt.tests.common import TestClassWithLogin


class RecordTest(TestClassWithLogin):
    url = '/api/v1/data/'

    @classmethod
    def create_record(
            cls, test_obj, table_name, data):
        """
        创建数据
        :param test_obj: 用例对象
        :param table_name: 所属表表名
        :param data: 记录数据(dict), key=字段key, value=字段值
        :return: 字段属性字典
        """

        url = f'{cls.url}{table_name}/'
        response = test_obj.client.post(url, data=data)
        test_obj.assertEqual(response.status_code, 201, msg=response)
        content = json.loads(response.content)
        test_obj.assertEqual(content['result'], 'created', msg=content)
        return content

    @classmethod
    def delete_record(cls, test_obj, table_name, record_id):
        """
        删除数据
        :param test_obj: 用例对象
        :param table_name: 表名
        :param record_id: 记录id
        """
        record_url = f'{cls.url}{table_name}/{record_id}/'

        # 删除前查，应该可以查到
        response = test_obj.client.get(record_url)
        test_obj.assertEqual(response.status_code, 200, msg=response)

        response = test_obj.client.delete(record_url)
        test_obj.assertEqual(response.status_code, 204, msg=response)

        # 再查data，此时应该查不到
        response = test_obj.client.get(record_url)
        test_obj.assertEqual(response.status_code, 404, msg=response)

        # 查删除记录，应该可以查到
        record_history_url = f'/api/v1/deleted-data/{table_name}/'
        response = test_obj.client.get(record_history_url)
        test_obj.assertEqual(response.status_code, 200, msg=response)

    @classmethod
    def update_record(cls, test_obj, table_name, record_id, data,
                      status_code=200, partial=False):
        """
        更新数据
        :param test_obj: 用例对象
        :param table_name: 表名
        :param record_id: 记录id
        :param data: 数据
        :param status_code: 修改api调用后，应该获取的 status_code
        :param partial: 是否部分修改
        """
        record_url = f'{test_obj.url}{table_name}/{record_id}/'
        if partial:
            response = test_obj.client.patch(record_url, data=data)
        else:
            response = test_obj.client.put(record_url, data=data)
        test_obj.assertEqual(response.status_code, status_code, msg=response)
        time.sleep(1)  # 写ElasticSearch操作较慢，需要等待

        # 查修改后的记录
        record_url = f'{test_obj.url}{table_name}/{record_id}/'
        response = test_obj.client.get(record_url)
        test_obj.assertEqual(response.status_code, 200, msg=response)

        if partial:
            return

        content = json.loads(response.content)
        db_data = content['_source']
        check_data = {}
        for k, v in db_data.items():
            if not k.startswith('S-'):
                check_data[k] = v
        test_obj.assertEquals(check_data, data, msg=content)

    def test_records(self):
        """
        数据相关基础功能验证
        """
        from mgmt.tests.test_table import TableTest
        # 创建表
        table = TableTest.create_table(self)
        table_name = table['name']

        # 创建2个字段
        from mgmt.tests.test_field import FieldTest
        FieldTest.create_field(self, table_name, name='k1', type_=0)
        FieldTest.create_field(self, table_name, name='k2', type_=0)

        # 创建3条记录
        data = {'k1': 'r1k1', 'k2': 'r1k2'}
        r1 = self.create_record(self, table_name, data)
        r1_id = r1['_id']
        data = {'k1': 'r1k1', 'k2': 'r1k2'}
        self.create_record(self, table_name, data)
        data = {'k1': 'r1k1', 'k2': 'r1k2'}
        self.create_record(self, table_name, data)

        # 修改第1条记录
        data = {'k1': 'r1k1_mod', 'k2': 'r1k2_mod'}
        self.update_record(self, table_name, r1_id, data)

        # 查所有记录
        url = f'{self.url}{table_name}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['total'], 3, msg=content)

        # 查记录的修改历史
        record_history_url = f'/api/v1/record-data/{table_name}/{r1_id}/'
        response = self.client.get(record_history_url)
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['total'], 1, msg=content)

        # 删除上述记录
        self.delete_record(self, table_name, r1_id)

        # 删除表
        TableTest.delete_table(self, table_name)

    def test_mod_after_add_field(self):
        """
        在新增一个字段之后，修改数据
        """
        # 创建一个表t
        from mgmt.tests.test_table import TableTest
        # 创建表
        t = TableTest.create_table(self)
        t_name = t['name']

        # 对t创建一个字段f1
        # 创建2个字段
        from mgmt.tests.test_field import FieldTest
        FieldTest.create_field(self, t_name, name='f0', type_=0)
        FieldTest.create_field(self, t_name, name='f1', type_=3, is_multi=True)

        # 创建一条记录r
        data = {
            'f0': 'r1f0',
            'f1': [
                '2019-05-06T12:36:45',
                '2019-05-06T12:36:48',
            ],
        }
        r1 = self.create_record(self, t_name, data)
        r1_id = r1['_id']

        # 修改内容与原内容一致，应该失败
        self.update_record(self, t_name, r1_id, data, status_code=400)

        # 部分修改内容与原内容一致，应该失败
        data.pop('f0')
        self.update_record(
            self, t_name, r1_id, data, status_code=400, partial=True)

        # 部分修改
        data = {'f0': 'r1f0_1'}
        self.update_record(self, t_name, r1_id, data, partial=True)

        # 对a创建一个字段f2
        FieldTest.create_field(self, t_name, name='f2', type_=0)

        # 修改记录r，对r.f2赋值
        data = {
            'f0': 'r1f0_mod',
            'f1': [
                '2019-05-06T12:36:45',
                '2019-05-06T12:55:48',
            ],
            'f2': 'r1f2_new',
        }
        self.update_record(self, t_name, r1_id, data)
