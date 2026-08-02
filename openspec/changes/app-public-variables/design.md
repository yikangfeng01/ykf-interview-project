## Context

当前系统已有 `signature_variables` 表（绑定模板，通过 `template_id` FK 关联）和对应的变量管理页面 `renderVariables()`。本次变更新增一个**不依赖模板**的公共变量池，独立于模板维度存在，侧边栏作为一级菜单项。

数据层复用现有 `auth/db.py` 连接管理，使用 psycopg2 直写 SQL，与项目其他模块技术栈一致。

## Goals / Non-Goals

**Goals:**
- 侧边栏新增一级菜单 "公共变量管理"（`#public-variables`），与项目管理、签字页公共模板管理并列
- 新建 `public_variables` 表，结构等同 `signature_variables` 但去除 `template_id` 外键，`name` 作为唯一约束
- 提供完整 CRUD API：列表查询、新增、更新、删除
- 支持 Excel 批量导入和导入模板下载（复用 openpyxl）
- 前端变量管理页面功能与 `renderVariables()` 完全一致，但无 `templateId` 参数依赖

**Non-Goals:**
- 不修改现有 `signature_variables` 表或 `renderVariables()` 逻辑
- 不建立 public_variables 与模板之间的引用关系（纯变量池，后续按需扩展）
- 不实现变量分页、排序、搜索等高级功能（与现有变量管理保持一致）

## Decisions

### 1. `public_variables` 表结构

| 列 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | SERIAL PRIMARY KEY | 自增 | |
| name | VARCHAR(255) NOT NULL | UNIQUE | 变量名，全局唯一 |
| value | TEXT DEFAULT '' | | 默认值 |
| var_type | VARCHAR(50) NOT NULL DEFAULT 'signature' | | 类型：signature/text/date/checkbox |
| page | INTEGER DEFAULT 1 | | 页码 |
| x | FLOAT DEFAULT 0 | | X 坐标 |
| y | FLOAT DEFAULT 0 | | Y 坐标 |
| width | FLOAT DEFAULT 120 | | 宽度 |
| height | FLOAT DEFAULT 40 | | 高度 |
| font_size | INTEGER DEFAULT 12 | | 字号 |
| font_color | VARCHAR(20) DEFAULT '#000000' | | 字体颜色 |
| required | BOOLEAN DEFAULT true | | 是否必填 |
| created_at | TIMESTAMP DEFAULT NOW() | | 创建时间 |
| updated_at | TIMESTAMP DEFAULT NOW() | | 更新时间 |

与 `signature_variables` 对比：去除 `template_id` 列和 `UNIQUE(template_id, name)` 约束，改为 `UNIQUE(name)`。

### 2. API 端点设计

| 端点 | 方法 | 说明 | 鉴权 |
|---|---|---|---|
| `/api/public-variables` | GET | 获取所有公共变量列表 | token |
| `/api/public-variables` | POST | 新增公共变量 | token |
| `/api/public-variables/<id>` | PUT | 更新公共变量 | token |
| `/api/public-variables/<id>` | DELETE | 删除公共变量 | token |
| `/api/public-variables/import` | POST | Excel 批量导入 | token |
| `/api/public-variables/import-template` | GET | 下载导入 Excel 模板 | token |

鉴权方式与现有 API 一致：请求头 `Authorization: Bearer <token>` 或 JSON body `{"token":"..."}`。

### 3. 数据访问层 `data/public_variables.py`

参考 `data/signature_variables.py` 的结构，提供以下方法：
- `get_all()` — 返回所有公共变量，按 name 排序
- `get_by_id(variable_id)` — 按 ID 查单条
- `create(name, ...)` — 新增（无 template_id 参数）
- `update(variable_id, **kwargs)` — 更新。如果 name 或 value 变更，级联更新 `signature_variables` 和 `project_template_variables` 中 `public_variables_id` 匹配的记录。注意事项：级联 UPDATE 执行后 `cur.description` 变为 `None`，必须在执行级联操作前捕获列信息（`cols = [desc[0] for desc in cur.description]`），否则返回结果构造时抛出 `'NoneType' is not iterable`。
- `delete(variable_id)` — 删除。级联删除 `signature_variables` 和 `project_template_variables` 中 `public_variables_id` 匹配的记录。
- `bulk_create(variables)` — 批量导入（无 template_id 参数）

### 4. 前端路由与侧边栏

在 `render()` 的 switch 中新增 case：

```javascript
case 'public-variables': return renderPublicVariables(params);
```

侧边栏 HTML 新增：

```html
<div class="sidebar-item" data-menu="public-variables" onclick="navigate('public-variables')">公共变量管理</div>
```

`getActiveMenu()` 扩展：

```javascript
if (['public-variables'].includes(view)) return 'public-variables';
```

### 5. `renderPublicVariables()` 渲染函数

结构与 `renderVariables()` 完全相同（变量表单模态框 + 导入模态框 + 表格），差异：
- **无 `templateId` 参数** — 不需要先获取模板名，页面标题直接写死 "公共变量管理"
- **返回链接** — 指向 `#public-variables` 自身（或去掉返回链接）
- **API 调用** — 所有 API 路径用 `/api/public-variables` 替代 `/api/templates/<id>/variables`
- **`saveVar()` / `doImport()` 调用** — 不传 `templateId`

### 6. 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `data/init.sql` | 修改 | 新增 `public_variables` DDL |
| `data/public_variables.py` | 新建 | 数据访问层 |
| `app.py` | 修改 | 新增 6 个 API 路由 |
| `static/index.html` | 修改 | 侧边栏 + 路由 dispatch + `getActiveMenu()` + `renderPublicVariables()` |

## Risks / Trade-offs

- [Risk] `public_variables` 与 `signature_variables` 字段几乎一致，存在重复 → Mitigation：通过代码模板复用保持一致性；后续可考虑统一基表或视图
- [Trade-off] 公共变量不与任何模板关联，暂不提供"引用到模板"的功能 → 后续可通过关联表扩展
- [Risk] `init.sql` 修改后需手动对线上 DB 执行 → Mitigation：tasks 中明确分为 SQL 编写和 DB migration 两步
