from django.contrib.auth import get_user_model

import _setup_django


def main():
    user_model = get_user_model()

    # 发现安装时创建了2次，暂时还没定位根因，先这样防错
    if user_model.objects.filter(username='admin').exists():
        return

    user_model.objects.create_superuser('admin', '1@x.x', 'cmdbcmdb')


if __name__ == '__main__':
    main()
