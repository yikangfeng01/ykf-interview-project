# 项目说明：

### 本项目主要基于codebuddy(限时免费)+模型Hy3+openspec结合开发。复杂项目考虑再+superpowers。

1. 项目依赖数据库为docker安装postgresql，/data/init.sql为数据库表初始sql。
2. 项目登录用户名admin,密码password123，项目数据没做按用户隔离。 
2. 项目测试模板文件在testtemplate目录下，变量配置格式为${张三}、${赵四}、${王五}等。 
3. 项目启动直接运行app.py即可。 
4. history_202608011049.md文件为codebuddy+openspec使用记录。
5. 经实测项目模板变量替换后，生成预览pdf，需依赖本地安装docx2pdf库和安装word。
