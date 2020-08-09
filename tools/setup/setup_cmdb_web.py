# -*- coding: utf-8 -*-
"""
@author: children1987
"""

from setup_utils import get_config_info, replace_in_file


def main():
    config_info = get_config_info()
    # 使前端项目在dev模式下可被外部访问
    f = '/opt/cmdb-web/config/index.js'
    replace_in_file(f, "host: 'localhost'", "host: '0.0.0.0'")

    f = '/opt/cmdb-web/src/api/index.js'
    ip = config_info['ip']
    replace_in_file(
        f,
        "baseURL = 'http://127.0.0.1:8000/api/v1/'",
        "baseURL = 'http://{}:8000/api/v1/'".format(ip)
    )


if __name__ == '__main__':
    main()
