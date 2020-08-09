FROM centos:7

# 安装基础包
RUN yum install -y wget python3 zlib-devel git

WORKDIR /opt

# 安装npm
RUN wget -c https://mirror.tuna.tsinghua.edu.cn/nodejs-release/v8.9.1/node-v8.9.1-linux-x64.tar.xz
RUN tar -xvf node-v8.9.1-linux-x64.tar.xz
RUN mv node-v8.9.1-linux-x64 nodejs
RUN ln -s /opt/nodejs/bin/node /usr/local/bin/node
RUN ln -s /opt/nodejs/bin/npm /usr/local/bin/npm

# 安装cnpm
RUN npm install -g cnpm --registry=https://registry.npm.taobao.org
RUN ln -s /opt/nodejs/bin/cnpm /usr/local/bin/cnpm

RUN git clone https://gitee.com/shihow/cmdb-web.git
WORKDIR /opt/cmdb-web
RUN cnpm i
WORKDIR /opt
RUN git clone https://gitee.com/shihow/cmdb.git
RUN python3 /opt/cmdb/tools/setup/setup_cmdb_web.py
