## Why

当前系统仅支持预置的种子模板数据，无法动态管理 DOCX 模板及模板内签字变量。管理员需要一个完整的后台来上传 DOCX 模板、配置每个模板的签字区域变量（支持填写变量值，文本域最长 1024 字符），并支持变量的批量 Excel 导入，以支撑后续签名流程。

## What Changes

- 新增模板 CRUD：上传 DOCX 文件（multipart）、编辑元数据（名称/分类/描述）、删除（级联删除变量）、列表查询
- 新增 `signature_variables` 数据库表，记录每个模板的签字变量（名称、类型、坐标位置、样式属性等），新增 `public_variables_id` 外键列引用 `public_variables` 表实现公共变量绑定，支持复选框多选批量绑定与重复检查
- 新增变量管理 API：单个新增/编辑/删除/查询，以及 Excel 批量导入变量（支持模板下载）
- 新增两个 SPA 视图页面：`#templates`（模板管理列表）和 `#templates/:id/variables`（变量管理）
- 新增依赖 `openpyxl` 用于 Excel 读写

## Capabilities

### New Capabilities

- `template-management`: 模板 DOCX 上传、编辑元数据、删除（级联删除关联变量）、查询列表
- `signature-variables`: 每个模板下的签字变量新增（含变量值字段，最长 1024 字符）、编辑、删除、查询，以及 Excel 批量导入与模板下载

### Modified Capabilities

<!-- No existing main specs to modify. Template management is a new feature not covered by prior changes. -->

## Impact

- **数据库**: 新增 `signature_variables` 表（FK → templates(id) ON DELETE CASCADE）；编辑模板时级联同步 `project_templates` 表中 `public_template_id` 匹配的记录（name, category, description, file_path）
- **API**: 新增 9 个 REST 端点（见设计文档）
- **前端**: 现有 `#home` 页面增加"模板管理"导航入口跳转到 `#templates`；新增两个 SPA 视图页面
- **依赖**: 新增 `openpyxl`（Excel 读写），加入 `requirements.txt`
- **文件系统**: 上传 DOCX 存放于 `uploads/templates/<template_id>/` 目录
