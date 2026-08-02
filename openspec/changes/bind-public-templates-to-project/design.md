## Context

当前项目模板管理页面（`#project/:id/templates`）只有"上传模板"功能，要求用户手动上传 PDF 文件并填写元信息。公共模板管理页面已有配置好的模板及签字变量，但无法被项目直接引用。两张表（`templates` 和 `project_templates`）数据完全独立，需要提供"绑定"机制将公共模板深拷贝到项目空间。

## Goals / Non-Goals

**Goals:**
- 项目模板列表页新增"绑定公共模板"按钮
- 支持从公共模板列表多选模板
- 绑定操作深拷贝：模板元数据、PDF 文件、签字变量全部复制到项目表
- 已绑定过的模板不应重复绑定（按名称去重提示）
- 绑定后的项目模板与原公共模板完全独立

**Non-Goals:**
- 不支持"同步更新"——绑定后两边的变更互不影响
- 不支持解除绑定、引用链接、软链接等
- 不修改公共模板管理页面的任何功能

## Decisions

### Decision 1: 深拷贝而非引用

**选择**: 绑定操作执行完整深拷贝——复制模板记录到 `project_templates` 表、复制 PDF 文件到 `uploads/project_templates/<id>/`、复制签字变量到 `project_template_variables` 表。

**备选方案**:
- 引用/外键关联：在 `project_templates` 中加 `source_template_id` 字段指向原模板。问题：原模板删除后项目模板会悬空；两个空间的变量管理需要联动，增加复杂度。
- 仅复制元数据不复制变量：用户绑定后仍需手动配变量，没有解决效率问题。

**理由**: 深拷贝保证数据独立性，项目模板可随意编辑/删除而不影响公共模板，符合项目模板管理页面的设计定位。

### Decision 2: 单一批量 API 端点

**选择**: 新增 `POST /api/projects/<pid>/templates/bind`，接受 `{"template_ids": [1, 2, 3]}`，在一个事务中完成所有绑定。

**备选方案**:
- 多个单独调用 `POST /api/projects/<pid>/templates`：前端多次请求，无法保证事务性，部分绑定成功部分失败难以处理。
- 仅接受单个 `template_id`：前端需要循环调用，体验差。

**理由**: 批量接口减少网络往返，事务保证原子性，整体成功或整体失败。

### Decision 3: 按名称 + 项目 ID 去重

**选择**: 在绑定前检查 `project_templates` 表中是否已存在 `(project_id, name)` 相同的记录。已存在的跳过并记录在 `skipped` 列表中返回给前端。

**备选方案**:
- 不允许任何重复（包括不同名称）：过于严格，用户可能需要同名但来自不同公共模板的副本。
- 不去重，允许完全重复：数据混乱，用户困惑。

**理由**: `(project_id, name)` 组合是合理的唯一性约束，既预防误操作，又保留灵活性。

### Decision 4: 模态框交互模式

**选择**: 复用项目模板页现有的 `.modal-overlay` 样式，新增独立的 `#ptmpl-bind-modal` 模态框。模态框放大尺寸（如 `max-width: 800px`）。模板列表以表格形式展示，包含列头（复选框、模板名称、分类、描述），每行不换行。内容区域超出时显示横向/纵向滚动条。表格下方显示"全选 / 取消全选"文字标签，其右侧紧邻放置全选复选框（同行排列）。底部确认/取消按钮。

**备选方案**:
- 跳转到独立页面选择：增加页面跳转，断开上下文。
- 在公共模板管理页面加"绑定到项目"按钮：需要传递目标项目 ID，逆向关系不直观。

**理由**: 在项目上下文中直接选择要绑定的模板更符合用户心智模型。表格布局 + 列头使模板信息更清晰可读，放大模态框可容纳更多内容，滚动条确保大量模板时不被撑开。

### Decision 5: 全局状态变量生命周期

`ptmplBindProjectId` 在 `showProjectBindTemplateModal()` 中设置，在 `closeProjectBindTemplateModal()` 中重置为 `null`。绑定确认流程 `confirmBindTemplates()` 中，必须先捕获 `ptmplBindProjectId` 到局部变量（`const pid = ptmplBindProjectId`），再调用 `closeProjectBindTemplateModal()`，确保后续 `loadProjectTemplates()` 拿到正确的 projectId 而非 `null`。

**理由**: `closeProjectBindTemplateModal()` 会将全局变量清空以干净地销毁模态框状态，但如果在此之前的异步操作或后续刷新逻辑仍需使用该值，则会导致 `loadProjectTemplates(null)` 请求 `/api/projects/null/templates`。

## Risks / Trade-offs

- **[Risk] 大量公共模板时的渲染性能** → 当前模板数量有限（几十个），`GET /api/templates` 一次性返回全量，无需分页。
- **[Risk] PDF 文件复制可能耗时** → 文件通过 Python `shutil.copy2` 复制，在同一文件系统上通常很快（< 1ms），在模板数量不多的情况下总延迟可接受。
- **[Risk] 绑定过程中断（部分文件复制成功但 DB 写入失败）** → API 使用 DB 事务包裹整个绑定过程，失败时 rollback；但已复制到磁盘的 PDF 文件不会被自动清理（文件操作不在事务内）。当前忽略此边缘情况，因为绑定很少失败。如需要，后续可加入文件清理逻辑。
