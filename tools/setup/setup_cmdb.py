# -*- coding: utf-8 -*-
"""
@author: children1987
"""
from setup_utils import get_config_info, cmd, replace_in_file


def main():
    cmd('yum install -y mysql-devel gcc libsasl2-dev python-dev libldap2-dev libssl-dev openldap-devel')
    cmd('pip3 install pipenv -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com')
    cmd('/usr/local/python3/bin/pipenv lock -r > requirements.txt')
    cmd('pip3 install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com')
    cfg_file = '/opt/cmdb/cmdb/settings.py'

    config_info = get_config_info()
    ip = config_info['ip']
    replace_in_file(
        cfg_file, '"HOST": "127.0.0.1"', '"HOST": "{}"'.format(ip)
    )
    password = config_info['mysql']['root_password']
    replace_in_file(
        cfg_file, '"PASSWORD": "1qaz!QAZ"', '"PASSWORD": "{}"'.format(password)
    )
    #cmd('python3 manage.py migrate')
    cmd('python3 tools/setup/create_superuser.py')


if __name__ == '__main__':
    main()
