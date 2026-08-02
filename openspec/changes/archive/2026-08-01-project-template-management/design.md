## Context

当前系统有两套全局表：`templates`（签字页模板）和 `signature_variables`（签字变量），由侧边栏「模板管理」入口管理。项目列表「选择模板」按钮跳转到 `#select-template/:id`，仅支持从全局模板库中选择并绑定。

本次变更在项目层级新增独立的模板和变量管理体系，数据与全局表完全隔离。

### 相关现有代码

| 层 | 全局版本（现有） | 项目版本（新增） |
|---|---|---|
| 数据库表 | `templates`, `signature_variables` | `project_templates`, `project_template_variables` |
| 数据层 | `data/templates.py`, `data/signature_variables.py` | `data/project_templates.py`, `data/project_variables.py` |
| API | `/api/templates`, `/api/templates/:id/variables` | `/api/projects/:pid/templates`, `/api/projects/:pid/templates/:tid/variables` |
| SPA 视图 | `#templates`, `#templates/:id/variables` | `#project/:id/templates`, `#project/:id/templates/:tid/variables` |

## Goals / Non-Goals

**Goals:**
- 项目列表「选择模板」→ 进入项目专属的签字页模板管理页面（与全局模板管理功能对齐）
- 项目模板和变量数据与全局模板完全隔离，各自独立建表
- 支持上传 PDF 模板、编辑元数据、删除（级联删除变量）
- 支持签字变量的增删改查 + Excel 批量导入/模板下载
- 侧边栏标题「模板管理」→「签字页模板管理」；`#templates` 页标题同步更新

**Non-Goals:**
- 不修改全局 `templates` / `signature_variables` 表结构
- 不修改 `#templates` 的变量管理功能逻辑
- 不在新页面中添加「使用此模板」按钮（当前项目视图仅管理模板和变量）
- 不删除 `#select-template/:id` 的数据库绑定逻辑（projects.template_id 保留，但 SPA 入口移除）

## Decisions

### 1. 独立建表 vs 复用全局表 + project_id 字段

**决策：独立建表**，`project_templates` 和 `project_template_variables` 与全局表镜像结构，通过 `project_id` FK 关联项目。

**理由：**
- 用户明确要求项目模板数据与全局模板隔离，互不干扰
- 独立表避免复杂的权限/可见性逻辑（全局模板对所有人可见，项目模板仅项目成员可见）
- DELETE CASCADE：删除项目时级联清理所有关联模板和变量
- 表结构与全局表一致，数据层代码可参考现有实现快速复制

**替代方案**：在 `templates` 表加 `project_id` nullable FK → 查询复杂度高，混合管理困难。

### 2. 项目模板表结构

`project_templates` 与 `templates` 字段对齐，额外加 `project_id` FK：

```sql
CREATE TABLE project_templates (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    public_template_id INTEGER REFERENCES templates(id)
);
```

### 3. 项目模板变量表结构

`project_template_variables` 与 `signature_variables` 字段对齐，FK 指向 `project_templates`：

```sql
CREATE TABLE project_template_variables (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES project_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    var_type VARCHAR(50) NOT NULL DEFAULT 'signature',
    page INTEGER DEFAULT 1,
    x FLOAT DEFAULT 0,
    y FLOAT DEFAULT 0,
    width FLOAT DEFAULT 120,
    height FLOAT DEFAULT 40,
    font_size INTEGER DEFAULT 12,
    font_color VARCHAR(20) DEFAULT '#000000',
    required BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(template_id, name)
);
```

### 4. API 路由前缀

采用 `/api/projects/<project_id>/templates/...` 前缀，与现有项目相关 API 风格一致（参考 `POST /api/projects/<id>/select-template`）。

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/projects/<pid>/templates` | 列表查询（支持 ?category= 过滤） |
| POST | `/api/projects/<pid>/templates` | 上传模板（multipart/form-data，存储 PDF） |
| PUT | `/api/projects/<pid>/templates/<tid>` | 编辑元数据（name, category, description） |
| DELETE | `/api/projects/<pid>/templates/<tid>` | 删除模板（级联删除变量 + 删除文件） |
| GET | `/api/projects/<pid>/templates/<tid>/variables` | 查询变量列表 |
| POST | `/api/projects/<pid>/templates/<tid>/variables` | 新增变量 |
| PUT | `/api/projects/<pid>/templates/<tid>/variables/<vid>` | 编辑变量 |
| DELETE | `/api/projects/<pid>/templates/<tid>/variables/<vid>` | 删除变量 |
| POST | `/api/projects/<pid>/templates/<tid>/variables/import` | Excel 批量导入 |
| GET | `/api/projects/<pid>/templates/variables-template` | 下载 Excel 导入模板 |

### 5. 文件存储路径

项目模板 PDF 存放在 `uploads/project_templates/<template_id>/`，与全局模板 `uploads/templates/<template_id>/` 隔离。

### 6. SPA 路由处理

在 `hashchange` 路由分发中新增解析逻辑：

```
#project/:id/templates/:tid/variables → renderProjectTemplateVariables(projectId, templateId)
#project/:id/templates              → renderProjectTemplates(projectId)
#select-template/:id                → 移除（不再使用）
```

通过 `split('/')` 解析多段 hash，区分 `#project/:id`（项目详情）、`#project/:id/templates`（项目模板列表）、`#project/:id/templates/:tid/variables`（变量管理）。

### 7. 代码复用策略

数据层和 API 层代码参考现有的 `data/templates.py`、`data/signature_variables.py` 和 `app.py` 中对应的路由处理。结构相同，仅表名和查询条件（项目级需加 `WHERE project_id = %s`）不同。

**关键规则——数据序列化**：所有数据层 `fetchall()`/`fetchone()` 返回值必须使用 `dict(zip(columns, row))` 将 psycopg2 元组转换为字典（参考 `templates.py` 第 22-23 行），否则 `jsonify()` 将输出 JSON 数组而非对象，前端 JS 无法按字段名访问数据（`template.name` 等全部为 `undefined`）。

SPA 视图层：`renderProjectTemplates()` 和 `renderProjectTemplateVariables()` 的 HTML/CSS 结构与 `renderTemplates()` 和 `renderVariables()` 一致，差异点：
- 标题栏显示当前项目名
- 返回按钮回到 `#home`（项目列表）
- API 请求前缀改为 `/api/projects/<pid>/templates`
- 操作列与现有 `#templates` 完全一致：编辑 / 变量管理 / 删除

### 8. 侧边栏标题变更

侧边栏「模板管理」改为「签字页模板管理」；全局模板页 `#templates` 的页面标题同步改为「签字页模板管理」。

### 9. Multipart 请求的 Token 传递

`app.py` 的 `_extract_token()` 经 `apiMultipart()` 通过 FormData 发送 token（`formData.append('token', currentToken)`），但 `_extract_token()` 只检查 `request.get_json()["token"]`、`request.args.get("token")`、`request.headers["Authorization"]`，未检查 `request.form.get("token")`，导致所有 multipart 上传请求返回 401 "Token is required"。

**修复**：在 `_extract_token()` 中 JSON body 检查之后、query param 之前插入 `request.form.get('token')`。

**影响范围**：`POST /api/projects/<pid>/templates` 和 `POST /api/projects/<pid>/templates/<tid>/variables/import` 全部受影响。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|---|---|
| 两套模板表结构重复，后续 schema 变更需双写 | 本次两个表的 schema 已与全局表对齐，短期无需变更 |
| `#project/:id` 路由与 `#project/:id/templates` 路由可能解析混淆 | 在 hash 路由处理中使用参数长度判断（`parts.length === 2` vs `parts.length === 3`） |
| 删除项目时级联删除模板 PDF 文件 | 调用 `os.remove()` 前检查文件是否存在 |
