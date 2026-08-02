## Why

当前系统只有模板维度的变量管理（`signature_variables` 通过 `template_id` 外键绑定到特定模板），用户需要一个独立于模板的公共变量池，可以集中管理跨模板复用的签字变量（如"甲方"、"乙方"、"日期"等通用字段），而不必在每个模板下重复创建。

## What Changes

- **新增侧边栏一级菜单"公共变量管理"**，点击切换至 `#public-variables` 路由
- **新增 `public_variables` 数据库表**，结构与 `signature_variables` 一致但去除 `template_id` 外键，`name` 作为唯一约束
- **新增 6 个 REST API 端点**：列表查询、新增、更新、删除、Excel 批量导入、导入模板下载
- **新增数据访问层文件** `data/public_variables.py`，提供 CRUD + 批量创建方法
- **新增前端渲染函数** `renderPublicVariables()`，功能与现有 `renderVariables()` 完全一致（变量 CRUD + Excel 导入/导出），但不依赖 `templateId` 参数
- **更新路由分发**，在 hash 路由 dispatch 中新增 `public-variables` 分支

## Capabilities

### New Capabilities
- `public-variables`: 独立的公共变量池管理，支持变量 CRUD、Excel 批量导入/导出，不绑定任何模板

### Modified Capabilities
<!-- 无现有 spec 被修改 -->

## Impact

| 组件 | 影响 |
|------|------|
| `data/init.sql` | 新增 `public_variables` DDL |
| `data/public_variables.py` | 新文件：数据访问层 |
| `app.py` | 新增 6 个 API 路由 |
| `static/index.html` | 侧边栏菜单项 + 路由 dispatch + `renderPublicVariables()` 渲染函数 |
