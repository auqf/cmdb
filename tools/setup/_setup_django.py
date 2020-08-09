import os
import sys

import django


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# SCRIPT_DIR : C:\repo_git\cmdb\gitee\cmdb\tools\setup

TOOLS_DIR = os.path.dirname(SCRIPT_DIR)
# TOOLS_DIR : C:\repo_git\cmdb\gitee\cmdb\tools

BASE_DIR = os.path.dirname(TOOLS_DIR)
# BASE_DIR : C:\repo_git\cmdb\gitee\cmdb

APPS_DIR = os.path.join(BASE_DIR, 'apps')


# sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, APPS_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmdb.settings")
django.setup()
