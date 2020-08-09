FROM children1987/centos7_python37

WORKDIR /opt
RUN git clone https://gitee.com/shihow/cmdb.git

WORKDIR cmdb
RUN python /opt/cmdb/tools/setup/setup_cmdb.py
