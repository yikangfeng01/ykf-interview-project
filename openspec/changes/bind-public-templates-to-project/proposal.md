## Why

项目模板管理页面当前只支持"上传模板"（上传新 PDF 文件），无法复用公共模板管理页面中已配置好的模板及其签字变量。用户需要重新上传相同的 PDF 并手动重新配置变量，效率低下且容易出错。需要提供"绑定公共模板"功能，将公共模板及其变量一键复制到项目中。

## What Changes

- 项目模板列表页新增"绑定公共模板"按钮，点击弹出公共模板选择模态框
- 支持多选公共模板（checkbox），确认后将所选模板及其签字变量**深拷贝**到项目模板空间（独立存储 PDF 文件和变量记录）
- 新增 `POST /api/projects/<pid>/templates/bind` 后端接口，批量处理绑定请求
- 绑定后的项目模板与原公共模板完全独立，互不影响
- 绑定模态框放大尺寸，模板列表以表格形式展示，增加列头（复选框、模板名称、分类、描述），内容不换行，超出区域显示横向/纵向滚动条

## Capabilities

### New Capabilities
- `bind-public-templates`: 项目模板管理页支持从公共模板库多选模板并深拷贝到当前项目，包括模板元数据、PDF 文件、签字变量

### Modified Capabilities
<!-- None - no existing spec-level changes -->

## Impact

- **`static/index.html`**: 项目模板列表页 `renderProjectTemplates` 新增"绑定公共模板"按钮和模态框 UI
- **`app.py`**: 新增 `POST /api/projects/<int:project_id>/templates/bind` 路由
- **`data/project_templates.py`**: 可能需要新增辅助方法（如按名称查重）
- **`data/project_variables.py`**: 需要调用 `bulk_create` 批量复制变量
- **`data/templates.py`**: 需要读取公共模板及变量的完整信息
