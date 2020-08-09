# -*- coding: utf-8 -*-
import os

from setup_utils import cmd, get_config_info


def setup_mysql57(root_pwd):
    """
    通过 docker 安装 mysql5.7
    """
    print("docker安装 mysql5.7 开始")
    '''
    cmd(
        ("docker run --name mysql -d --net=host -e MYSQL_ROOT_PASSWORD={} "
         "-v /var/cmdb/db:/var/lib/mysql mysql:5.7.21 "
         "--character-set-server=utf8mb4 "
         "--collation-server=utf8mb4_unicode_ci").format(root_pwd)
    )
    '''
    print("docker安装 mysql5.7 完成")


def main():
    if os.geteuid() != 0:
        raise Exception("请以root权限运行")

    print('安装 docker')
    cmd_str = 'mkdir tmp_for_setup_docker && yum install -y git && git clone https://gitee.com/shihowcom/setup_docker.git tmp_for_setup_docker/setup_docker && python ./tmp_for_setup_docker/setup_docker/setup_docker.py'
    #cmd(cmd_str)

    config_info = get_config_info()
    root_pwd = config_info['mysql']['root_password']
    #setup_mysql57(root_pwd)
    print(root_pwd)

    print('安装 docker-compose，同时等待mysql启动完成')
    #cmd("python tools/setup/setup_compose.py")

    db_name = 'cmdb'
    print('创建 {} 数据库'.format(db_name))
    '''
    cmd((
        "docker exec -itd mysql mysqladmin -uroot -p'{}' create {} "
        "b3log_symphony default character set utf8mb4"
        "collate utf8mb4_general_ci").format(root_pwd, db_name))
    '''

    #cmd("cd tools/setup && docker-compose up")


if __name__ == '__main__':
    main()
