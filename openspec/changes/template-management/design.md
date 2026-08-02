## Context

当前系统通过 `data/templates.py` 仅支持对预置种子模板的只读查询，`app-dashboard` design.md 第 22 行明确将模板的增删改管理列为 Non-Goal。随着业务发展，需要管理员能够动态上传 DOCX 模板并管理每个模板的签字变量，以支撑后续签名流程。

现有基础设施：
- `app.py`：Flask 应用，路由 pattern 为 `/api/<resource>`，JWT token 认证
- `data/`：数据访问层，使用 psycopg2 直连 PostgreSQL
- `static/index.html`：SPA 单页应用，hash 路由（`#login`, `#home`, `#project/:id`, `#select-template/:id`）
- `data/init.sql`：DDL 脚本，已有 `templates` 表（id, name, category, file_path, description）

## Goals / Non-Goals

**Goals:**
- 实现模板 DOCX 上传、编辑元数据（名称/分类/描述）、删除（级联删除变量及关联的 project_templates 记录）
- 实现 `signature_variables` 数据表及完整的 CRUD 操作
- 支持变量的 Excel 批量导入（模板下载）
- 新增 `#templates` 和 `#templates/:id/variables` 两个 SPA 视图页面
- 现有 `#home` 页面增加"模板管理"导航入口

**Non-Goals:**
- 不实现权限控制（忽略权限模型）
- 不修改项目中的模板选择功能（用户选模板流程不动）
- 不实现 DOCX 预览/渲染
- 不实现签字功能本身

## Decisions

### 1. 数据库设计：新增 `signature_variables` 表

```sql
CREATE TABLE IF NOT EXISTS signature_variables (
    id          SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,
    value       TEXT DEFAULT '',
    var_type    VARCHAR(50)  NOT NULL DEFAULT 'signature',
    page        INTEGER DEFAULT 1,
    x           FLOAT DEFAULT 0,
    y           FLOAT DEFAULT 0,
    width       FLOAT DEFAULT 120,
    height      FLOAT DEFAULT 40,
    font_size   INTEGER DEFAULT 12,
    font_color  VARCHAR(20) DEFAULT '#000000',
    required    BOOLEAN DEFAULT true,
    public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(template_id, name)
);
```

- 使用 `ON DELETE CASCADE` 确保删除模板时自动清理变量
- `UNIQUE(template_id, name)` 防止同一模板下变量名重复
- Excel 导入列：`name, value, var_type, page, x, y, width, height, font_size, font_color, required`

### 2. 文件上传策略

- DOCX 文件存储于 `uploads/templates/<template_id>/<original_filename>.docx`
- 使用 Flask `request.files` 处理 multipart/form-data 上传
- 上传先插入数据库记录获取 ID，再保存文件到对应目录
- 删除模板时同步删除文件系统上的 DOCX 文件

### 3. API 设计

复用现有 `data/` 数据访问层模式，新增 `data/signature_variables.py`：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/templates` | GET | 列表查询（现有，不变） |
| `/api/templates` | POST | 上传 DOCX + 元数据（multipart） |
| `/api/templates/<id>` | PUT | 编辑名称/分类/描述/文件路径，并级联同步 `project_templates` 中 `public_template_id=<id>` 的对应字段 |
| `/api/templates/<id>` | DELETE | 删除 + 级联删除 project_templates 中 public_template_id=<id> 的记录 + 级联删变量 + 删除文件 |
| `/api/templates/<id>/variables` | GET | 查询变量列表 |
| `/api/templates/<id>/variables` | POST | 新增单个变量 |
| `/api/templates/<id>/variables/<vid>` | PUT | 编辑变量 |
| `/api/templates/<id>/variables/<vid>` | DELETE | 删除变量 |
| `/api/templates/<id>/variables/import` | POST | Excel 批量导入 |
| `/api/templates/variables-template` | GET | 下载 Excel 导入模板 |

### 4. 前端 SPA 视图

新增两个视图和路由：

- `#templates`：模板管理列表页
  - 表格/卡片展示所有模板（名称、分类、描述、创建时间）
  - [+ 上传模板] 按钮 → 弹窗（选择 DOCX + 填写元数据）
  - 每个模板行：编辑、变量管理（跳转变量页）、删除按钮
- `#templates/:id/variables`：变量管理页
  - 返回按钮（回 `#templates`）
  - 变量列表表格（名称、变量值、类型、是否公共变量、页码、坐标、尺寸、必填、操作）；操作列中，当 `public_variables_id` 有值时，「编辑」按钮渲染为禁用状态（使用 `<button disabled>` 标签，视觉风格与同操作列的删除按钮保持一致）
  - [绑定公共变量] 按钮 → 弹窗以复选框列表展示 `GET /api/public-variables` 的所有公共变量（列：选择、名称、变量值、类型），列表下方放置全选/取消全选复选框；确认后自动为每个选中的公共变量创建模板变量并设置 `public_variables_id`；提交前检查同一模板下是否已存在相同 `public_variables_id` 的绑定（重复绑定跳过并提示）；绑定成功后自动关闭弹窗并刷新变量列表
  - [+ 新增变量] 按钮 → 弹窗（含变量值 textarea，最长 1024 字符）
  - [批量导入] 按钮 → 上传 .xlsx 文件
  - [下载模板] 按钮 → 下载 Excel 模板文件
- `#home` 增加 `[模板管理]` 按钮，跳转到 `#templates`

### 5. 依赖

新增 `openpyxl` 到 `requirements.txt`，用于：
- 生成 Excel 导入模板文件
- 解析上传的 Excel 文件批量提取变量数据

### 6. 数据访问层

新增 `data/signature_variables.py`，遵循现有 `data/templates.py` 的模式：
- 使用 `auth.db.get_connection()` 获取数据库连接
- 返回 `List[dict]` 或 `Optional[dict]`

## Risks / Trade-offs

- **DOCX 文件与数据库记录不一致**：删除操作先删 project_templates 级联记录，再删 signature_variables（CASCADE 自动清理变量），最后删文件系统文件。若文件删除失败，已无 DB 记录引用 → **Accept**，残留在磁盘上不影响功能
- **Excel 导入错误处理**：按行处理，遇到错误行跳过并记录，成功行继续 → 返回 `{imported: N, errors: [{row, message}]}`
- **大文件上传**：暂不限制文件大小 → **后续优化**，Flask 默认限制足够应对 DOCX 模板场景
- **并发冲突**：变量名唯一约束，并发插入同名变量会抛 IntegrityError → 前端弹窗提示
