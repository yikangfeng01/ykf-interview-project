## Why

当前项目列表「选择模板」按钮跳转到轻量级模板选择页（`#select-template/:id`），用户只能从全局模板库中选择模板并绑定。用户需要在项目上下文中独立管理项目专属的签字页模板（上传、编辑、删除）及其签字变量，与全局模板管理数据隔离。

## What Changes

- 新增项目级模板管理 SPA 视图 `#project/:id/templates`，取代原有的 `#select-template/:id` **BREAKING**
- 新增 `project_templates` 数据库表（项目专属模板，FK → projects）
- 新增 `project_template_variables` 数据库表（项目模板下的签字变量，FK → project_templates ON DELETE CASCADE）
- 新增 `data/project_templates.py` 和 `data/project_variables.py` 数据访问层
- 新增项目模板 CRUD API（`GET/POST /api/projects/:id/templates`、`PUT/DELETE /api/projects/:id/templates/:tid`）
- 新增项目模板变量管理 API（CRUD + Excel 批量导入/模板下载）
- 项目列表「选择模板」按钮改为跳转到 `#project/:id/templates`
- 侧边栏「模板管理」标题改为「签字页模板管理」
- 全局模板管理页 `#templates` 标题同步改为「签字页模板管理」

## Capabilities

### New Capabilities

- `project-template-crud`: 项目专属签字页模板上传、编辑元数据、删除（级联删除关联变量）、列表查询
- `project-template-variables`: 项目模板下的签字变量新增、编辑、删除、查询，以及 Excel 批量导入与模板下载

### Modified Capabilities

<!-- No existing main specs to modify. These are new capabilities. -->

## Impact

- **数据库**: 新增 `project_templates` 表（FK → projects(id) ON DELETE CASCADE, 含 `is_public` 标记是否来自公共模板绑定 + `public_template_id` FK → templates(id) 记录源模板）+ `project_template_variables` 表（FK → project_templates(id) ON DELETE CASCADE）
- **API**: 新增 ~10 个 REST 端点（项目模板 CRUD + 变量管理 + Excel 导入导出）
- **前端**: 新增 `#project/:id/templates` SPA 视图 + 变量管理子路由；移除 `#select-template/:id` 视图；项目列表「选择模板」按钮跳转路径变更；侧边栏和 `#templates` 标题更新
- **依赖**: 复用 `openpyxl`（已安装）
- **文件系统**: 上传 PDF 存放于 `uploads/project_templates/<template_id>/` 目录
