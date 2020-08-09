yum install -y mysql-devel gcc libsasl2-dev python-dev libldap2-dev libssl-dev openldap-devel
pip3 install pipenv -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
/usr/local/python3/bin/pipenv lock -r > requirements.txt
pip3 install -r requirements.txt -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
python3 manage.py test
