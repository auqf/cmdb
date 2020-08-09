## 1. 本项目解决了什么问题？
- 或者说如何使用本项目？
- 我们虽然提供了一个端到端使用本项目的demo（含快速安装命令，详见本文档稍后章节）。
- 但我们认为，对本项目的正确的使用方式应该是：将本项目作为一个引擎（纯后台）。
- 即，其它项目需要“动态创建表”时，调用本项目的api，本项目作为存储海量数据的“数据中心”。

## 2. 基本功能演示
- 爱奇艺链接: https://www.iqiyi.com/v_19ryamo6j4.html
- 直接下载: https://gitee.com/shihow/cmdb/attach_files

## 3. 安装demo
https://gitee.com/shihow/cmdb/tree/master/tools/setup

## 4. 特性
- 热添加删除表 自定义字段类型
- REST前后端分离架构 开放所有API接口
- 强大的搜索查找能力（后端使用elasticsearch存储数据 ） 可以配合kibana使用
- 支持查看数据修改记录
- 表级权限管理
- 容器快速部署

## 5. 技术栈
### 5.1 前端 -- https://gitee.com/shihow/cmdb-web
- Vue 2.5.2
- Element-ui
- Vue-Router
- Vuex
- Axios

### 5.2 后端 （即本repo）
- Python 3.7
- Django 3.0.6
- Django REST framework
- Elasticsearch 5.6.8
- Mysql 5.7
- Docker

## 6. 接管后的 已完成 && 计划中
- [x] 支持动态新增、删除表字段 __(重大变化)__
- [x] dockerfile，您可自行基于源码部署 __(重大变化)__
- [x] 补齐自动化测试用例 __(重大变化)__
- [x] 升级到Django3.0.6 __(重大变化)__
- [x] url尾部统一加 '/' __(重大变化)__
- [x] 剥离了ldap
- [x] header中api文档链接错误
- [x] 启用pipenv
- [x] on_ready() 会导致makemigration时异常
- [x] 新增基础功能演示视频
- [x] 以 user.is_staff 来判定是否可读写所有表，而不再以 all.read、all.write 判定
- [x] 清理冗余代码
- [x] 表管理页搜索bug
- [x] 动态表的字段支持排序
- [x] Required fields 支持多对多字段
- [x] 支持恢复已被删除的字段；仅支持假删除字段
- [x] 支持恢复已被删除的动态表；支持假删除、真删除表
- [x] bug: 第一条数据修改记录未保存执行用户
- [x] 字段类别支持附件、图片、长文本等类型
- [x] 字段类别支持单选、多选
- [x] 表级权限等效优化 -- 采用django原生，为后续的对象级权限做准备
- [x] 新增支持对象级权限 -- 借鉴guardian
- [ ] 提供一组api，用于访问授权和收回授权
- [ ] 支持第三方应用以token方式安全访问
- [ ] 全局的，Elasticsearch的文档type统一改为'data'。为Elasticsearch v7.x弃用doc_type做准备。 （优先级低）
- [ ] Elasticsearch 升级到 v7.x （优先级低）
- [ ] 在线演示 （优先级低）
- [ ] 国际化 （优先级低）

## 7. QQ群
- 建议优先使用本repo的issue沟通，因为QQ群不便于问题跟踪。
- 1027273209
- 点击链接加入群聊【cmdb】：https://jq.qq.com/?_wv=1027&k=5zUQ2Ks
- ![qq群二维码](https://images.gitee.com/uploads/images/2020/0503/125845_be61c8bd_1333971.png "屏幕截图.png")

## 8. 鸣谢
- 原项目地址: https://github.com/open-cmdb/cmdb
- 感谢原项目作者 tangmingming 的杰出贡献。
- 很遗憾，原项目作者不再维护了。
- 我们决定接管此项目，并在gitee维护。

## 9. 支持开源
开源不易，需要您的支持，支持方式：
### 1. star 本项目
### 2. 贡献代码
1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
### 3. 提bug或需求
- https://gitee.com/shihow/cmdb/issues
- 提issue前请先搜索，避免重复
### 4. 仅仅是使用本项目
### 5. 捐赠
- 1分钱也是支持
- ![捐赠](https://images.gitee.com/uploads/images/2020/0503/125753_287d1c22_1333971.png "屏幕截图.png")
