## Why

用户登录后，需要进入一个主控面板（主页），从主页管理签字页项目、选择合适的 PDF 签字页模板。当前系统在登录后没有后续页面，需要搭建系统核心枢纽层。

## What Changes

- 新增 PostgreSQL `projects` 表（项目名称、描述、状态、关联模板、创建者、时间）。
- 新增 PostgreSQL `templates` 表（模板名称、分类、文件路径、描述）。
- 后端暴露项目管理 API：`GET/POST /api/projects`、`GET/PUT/DELETE /api/projects/:id`。
- 后端暴露模板查询 API：`GET /api/templates`、`GET /api/templates?category=xxx`。
- 后端暴露模板选择 API：`POST /api/projects/:id/select-template`（将模板绑定到项目）。
- `project_template_variables` 表新增 `public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE SET NULL` 可为空。
- 项目模板变量管理页新增「绑定公共变量」按钮和弹窗（复选框多选 + 列表下方全选/取消全选复选框 + 重复绑定检查），功能与 `template-management` 绑定公共变量完全一致。
- 前端 SPA 新增壳式布局（顶部标题栏 + 左侧竖向下拉菜单 + 右侧内容区），菜单项「项目管理」「签字页公共模板管理」驱动内容区切换，默认打开项目管理。
- 前端 SPA 追加 `#home` 视图（项目列表 + 退出按钮）、`#project/:id` 视图（项目详情）、`#project/:id/select-template` 视图（模板浏览与选择），均在内容区内渲染。
- 前端 SPA 项目列表页使用表格布局，显示列头（项目名称、描述、状态、创建时间、操作）。
- 前端 SPA 项目列表表格增加「操作」列（编辑、删除、选择模板）。项目详情页移除所有操作按钮，操作统一收敛到列表页操作列。

## Capabilities

### New Capabilities

- `app-dashboard`: 主页仪表盘，含顶部标题栏与侧边栏壳式布局、退出功能、签字页项目管理、签字页模板浏览与绑定。

### Modified Capabilities

- 无（依赖 `user-login` 变更提供的登录与令牌校验能力）。

## Impact

- 新增数据库表：`projects`、`templates`（均位于 `ykf-interview-project-db`）。
- 新增依赖：无额外依赖（复用 psycopg2、Flask）。
- 新增 `app.py` 路由：projects CRUD + templates 查询 + 模板选择。
- 新增 SPA 视图：`#home`、`#project/:id`、`#project/:id/select-template`（追加到 `static/index.html`），签字页公共模板管理页（`#templates`）中对 `public_template_id` 有值的项目模板禁用编辑按钮。
- 新增种子数据：预置若干 PDF 签字页模板记录。
