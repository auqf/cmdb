"""
测试用例相关公共代码
"""

from rest_framework.test import APITestCase

from mgmt.tests.factories import UserFactory


class TestClassWithBaseData(APITestCase):

    def t_user_login(self, user):
        """
        使用于测试的用户登录
        :param user: UserFactory创建出的用户对象
        :return:
        """
        username = user.username
        response = self.client.post(
            '/api-auth/login/', {'username': username, 'password': '666666'})
        if response.status_code == 302:
            print(f'{user.username}登录成功')
        else:
            print(f'{user.username}登录失败')
        self.login_user = user

    def t_user_logout(self):
        """
        使用于测试的用户登出
        :return:
        """
        response = self.client.get('/api-auth/logout/')
        if response.status_code == 200:
            print(f'{self.login_user.username}退出成功')
        else:
            print(f'{self.login_user.username}退出失败')
        self.login_user = None

    # 添加测试用户
    def setUp(self):
        # 创建一个用于测试的超级用户
        self.test_user = UserFactory(
            username='test_super_user',
            is_staff=True,
        )
        self.test_user.set_password('666666')
        self.test_user.save()
        self.test_super_user = self.test_user

        # 创建一个用于测试的普通用户
        self.test_common_user = UserFactory(
            username='test_common_user',
            is_staff=False,
            is_superuser=False,
        )
        self.test_common_user.set_password('666666')
        self.test_common_user.save()

        self.prepare()

    def prepare(self):
        pass


class TestClassWithLogin(TestClassWithBaseData):
    """
    需要用户登录的测试用例
    """
    def prepare(self):
        self.t_user_login(self.test_super_user)
