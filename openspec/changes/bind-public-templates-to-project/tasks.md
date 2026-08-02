## 1. 后端 API

- [x] 1.1 新增 `POST /api/projects/<int:project_id>/templates/bind` 路由，接受 `{"template_ids": [1, 2, ...]}`
- [x] 1.2 实现绑定逻辑：对于每个 `template_id`，从 `templates` 表获取公共模板，检查 `project_templates` 是否已存在同名记录（按 name + project_id），若有则跳过并记录到 skipped 列表
- [x] 1.3 深拷贝模板：在 `project_templates` 表创建新记录，使用 `shutil.copy2` 将公共模板的 PDF 文件复制到 `uploads/project_templates/<new_id>/` 目录
- [x] 1.4 深拷贝变量：从 `signature_variables` 读取公共模板的所有变量，调用 `project_variables.bulk_create` 批量写入 `project_template_variables`
- [x] 1.5 使用数据库事务包裹整个绑定操作，确保原子性（全部成功或全部回滚）
- [x] 1.6 返回响应：`{"bound": [...], "skipped": [...]}`，区分成功绑定和跳过的模板

## 2. 前端 UI

- [x] 2.1 在 `renderProjectTemplates` 的 header-bar 中新增"绑定公共模板"按钮（与"+ 上传模板"按钮并列）
- [x] 2.2 新增 `#ptmpl-bind-modal` 模态框：列出公共模板（调用 `GET /api/templates`），每行展示 checkbox + 模板名称 + 分类
- [x] 2.3 实现 `showProjectBindTemplateModal()` 打开模态框并加载公共模板列表
- [x] 2.4 实现 `confirmBindTemplates()` 收集选中的 template_ids，调用 `POST /api/projects/<pid>/templates/bind`
- [x] 2.5 绑定成功后刷新项目模板列表，并展示绑定结果提示（如"成功绑定 3 个模板，跳过 1 个已存在的模板"）
- [x] 2.6 处理边界情况：未选模板时提示、全选/取消全选辅助操作
- [x] 2.7 放大绑定模态框尺寸（如 `max-width: 800px`）
- [x] 2.8 公共模板列表改为表格布局（`<table>`），增加列头（复选框、模板名称、分类）
- [x] 2.9 表格内容不换行（`white-space: nowrap`），内容区域超出时显示滚动条（`overflow: auto`）
- [x] 2.10 在绑定模态框表格中增加"描述"列，显示模板的 `description` 字段
- [x] 2.11 将全选复选框移到"全选 / 取消全选"文字后面（同行紧邻排列）
- [x] 2.12 修复 `confirmBindTemplates()` 中执行顺序 bug：`closeProjectBindTemplateModal()` 将 `ptmplBindProjectId` 置为 null，导致后续 `loadProjectTemplates()` 拿到空值。修复方式：在调用 `closeProjectBindTemplateModal()` 前将 `ptmplBindProjectId` 保存到局部变量（`const pid = ptmplBindProjectId`），后续 `loadProjectTemplates(pid)` 使用局部变量

## 3. 验证

- [x] 3.1 手动测试：绑定 1 个公共模板到项目，验证项目模板列表显示该模板
- [x] 3.2 手动测试：绑定多个模板，验证所有模板及变量均已复制
- [x] 3.3 手动测试：再次绑定同一模板，验证去重逻辑（skip）
- [x] 3.4 手动测试：验证绑定后的模板与原公共模板独立（删除公共模板后项目模板仍存在）
