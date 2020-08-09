"""
用户相关测试用例
"""

import json

from django.contrib.auth import get_user_model

from mgmt.tests.common import TestClassWithLogin
from mgmt.tests.factories import UserFactory


class UserTest(TestClassWithLogin):
    url = '/api/v1/mgmt/user/'

    def test_users_list(self):
        """
        用户列表展示
        """
        # 获取当前用户数
        user_model = get_user_model()
        cur_user_cnt = user_model.objects.all().count()

        # 创建一批用户
        create_user_cnt = 5
        for _ in range(create_user_cnt):
            UserFactory()
        url = self.url
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200, msg=response)
        content = json.loads(response.content)
        self.assertEqual(content['count'], cur_user_cnt+create_user_cnt)
