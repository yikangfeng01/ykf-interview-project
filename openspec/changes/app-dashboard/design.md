## Context

项目已通过 `user-login` 变更实现 PostgreSQL 用户存储 + SPA 壳 + 登录/验证/登出 API。本次变更在此 SPA 壳上追加主页、项目管理和模板选择三个模块，形成完整的系统核心枢纽。所有数据存储复用同一个 PostgreSQL 数据库 `ykf-interview-project-db`，使用 psycopg2 直写 SQL。

数据库关系：
```
users ──1:N──▶ projects ──N:1──▶ templates
               (created_by)     (template_id FK)
```

## Goals / Non-Goals

**Goals:**
- 主页（`#home`）展示当前用户的项目列表，提供新建项目入口和退出按钮。
- 项目支持 CRUD：创建、查看列表、查看详情、更新名称/状态、删除。
- 模板库：按分类浏览可用 PDF 签字页模板。
- 模板选择：在项目详情中将模板绑定到项目，更新项目状态。
- 所有操作需携带 token 验证身份。

**Non-Goals:**
- 不实现项目内的变量填写、文件生成（后续变更）。
- 不实现模板的新增/编辑/删除管理（由管理员后台另行实现）。
- 不实现多用户之间的项目共享或协作。
- 不实现项目批量操作、导入导出。

## Decisions

1. **数据存储：psycopg2 直写 SQL，与 `user-login` 共享连接管理**  
   原因：与 `user-login` 变更技术栈一致，共用 `auth/db.py` 连接模块，避免碎片化。  
   替代方案：独立 datasource 模块增加复杂度无收益。

2. **`projects` 表结构**  

   | 列 | 类型 | 约束 |
   |---|---|---|
   | id | SERIAL PRIMARY KEY | 自增 |
   | name | VARCHAR(255) NOT NULL | 项目名称 |
   | description | TEXT | 项目描述，可为空 |
   | status | VARCHAR(50) DEFAULT 'draft' | draft / template_selected / variables_filled / generated |
   | template_id | INTEGER | 外键 → templates.id，可为空 |
   | created_by | VARCHAR(255) NOT NULL | 对应用户 username |
   | created_at | TIMESTAMP DEFAULT NOW() | 创建时间 |
   | updated_at | TIMESTAMP DEFAULT NOW() | 更新时间 |

3. **`templates` 表结构**  

   | 列 | 类型 | 约束 |
   |---|---|---|
   | id | SERIAL PRIMARY KEY | 自增 |
   | name | VARCHAR(255) NOT NULL | 模板名称 |
   | category | VARCHAR(100) NOT NULL | 分类（如 `share_transfer`、`capital_increase`） |
   | file_path | VARCHAR(500) NOT NULL | 模板 PDF 文件路径 |
   | description | TEXT | 模板描述 |

4. **`project_template_variables` 表结构**  

   | 列 | 类型 | 约束 |
   |---|---|---|
   | public_variables_id | INTEGER | FK → public_variables.id ON DELETE SET NULL，可为空 |

5. **API 端点设计**  

   | 端点 | 方法 | 说明 | 鉴权 |
   |---|---|---|---|
   | `/api/projects` | GET | 获取当前用户的项目列表 | token |
   | `/api/projects` | POST | 新建项目 `{"name":"...","description":"..."}` | token |
   | `/api/projects/:id` | GET | 获取项目详情 | token |
   | `/api/projects/:id` | PUT | 更新项目 `{"name":"...","description":"...","status":"..."}` | token |
   | `/api/projects/:id` | DELETE | 删除项目 | token |
   | `/api/templates` | GET | 获取模板列表（可选 `?category=xxx`） | token |
   | `/api/projects/:id/select-template` | POST | 绑定模板 `{"template_id":1}` | token |
   | `/api/projects/:id/templates` | GET | 获取项目模板列表（可选 `?category=xxx`） | token |
   | `/api/projects/:id/templates` | POST | 上传项目模板 DOCX 文件 | token |
   | `/api/projects/:id/templates/:tid` | GET | 获取单个项目模板详情 | token |
   | `/api/projects/:id/templates/:tid` | PUT | 更新项目模板元数据 | token |
   | `/api/projects/:id/templates/:tid` | DELETE | 删除项目模板 | token |

   鉴权方式：请求头 `Authorization: Bearer <token>` 或 JSON body `{"token":"..."}`，先读取 body 中的 token 再 fallback Header。所有受保护路由调用 `auth.service.get_current_user(token)` 校验。

5. **SPA 壳式布局（追加到 `index.html`）**  

   登录成功后创建持久壳（顶部栏 + 侧边栏 + 内容区），之后所有视图只更新内容区。

   ```
   ┌─────────────────────────────────────────────────────────┐
   │  🔖  签字页项目管理系统                       [登出]    │  ← 顶部栏（持久）
   ├──────────┬──────────────────────────────────────────────┤
   │ ● 项目管理 │                                            │
   │ 签字页公共模板管理 │         内容区                          │
   │          │        （动态替换，不重建壳）                  │
   └──────────┴──────────────────────────────────────────────┘
   ```

   实现要点:
   - **双容器分离**: `#app` 根容器只放壳（`.topbar` + `.layout > .sidebar + .content`），内容区使用独立 `#content-area` 元素。所有 `renderXxx()` 只改写 `#content-area` 的 innerHTML。
   - **Login 不参与壳**: `#login` 保持独立全屏居中布局，直接渲染到 `#app` 无视壳结构。
   - **Shell 感知切换**: 路由分发时，若当前是 `#login`，走独立渲染；否则确保壳存在后只更新内容区。

6. **侧边栏菜单与导航**

   两个菜单项，hash 驱动高亮:

   | hash | 侧边栏高亮 | 内容区渲染 |
   |---|---|---|
   | `#home` | 项目管理 | `renderHome()` |
   | `#templates` | 签字页公共模板管理 | `renderTemplates()` — 列表内编辑按钮对 `public_template_id IS NOT NULL` 的记录渲染为禁用状态 |
   | `#project/:id` | 项目管理 | `renderProjectDetail()` |
   | `#select-template/:id` | 项目管理 | `renderSelectTemplate()` |
   | `#variables/:id` | 签字页公共模板管理 | `renderVariables()` |
   | `#project/:id/templates/:tid/variables` | 项目管理 | `renderProjectTemplateVariables()` — 页面标题格式: `{模板名} #{行序号}-签字变量` |

   实现: 不引入新的 JS 状态变量，从当前 hash 推导高亮项:

   ```javascript
   function getActiveMenu(hash) {
       if (['home', 'project', 'select-template'].includes(hash)) return 'projects';
       if (['templates', 'variables'].includes(hash)) return 'templates';
       return 'projects';
   }
   ```

   侧边栏点击等价于 `navigate('home')` / `navigate('templates')`，路由系统保持不变。

7. **CSS 布局方案（Flexbox 三区）**

   ```css
   body { display: flex; flex-direction: column; min-height: 100vh; margin: 0; }
   .topbar { height: 56px; flex-shrink: 0; display: flex; align-items: center; }
   .topbar-title { font-size: 1.5em; }  /* 签字页项目管理系统 — 缩小2倍品牌标题 */
   .layout { flex: 1; display: flex; overflow: hidden; }
   .sidebar { width: 220px; flex-shrink: 0; border-right: 1px solid #eee; }
   .content { flex: 1; overflow-y: auto; padding: 24px 32px; }
   ```

   注意: 所有已认证视图的样式从「居中卡片」改为「内容区全宽流式布局」。

8. **项目列表表格列头**: `loadProjects()` 从卡片列表改为表格布局，顶部带 `<thead>` 列头行（项目名称 | 描述 | 状态 | 创建时间）。窄屏场景项目描述可隐藏（responsive 优先保留表格名称、状态和时间），保持表格可横向滚动。空项目时显示空状态提示而非空表格。创建时间列使用独立辅助函数 `formatBeijingTime(dbStr)` 处理：PostgreSQL 服务器时区为 `Asia/Shanghai`，`created_at` 已是北京时间。后端通过自定义 `ISOJSONProvider` 将 Flask 默认的 HTTP-date 序列化（`"Sat, 01 Aug 2026 15:28:37 GMT"`）改为 ISO 格式（`"2026-08-01T15:28:37"`）；`formatBeijingTime` 直接做字符串格式化（`replace('T', ' ')` + `substring(0, 19)`），不经过 `new Date()` 避免时区解析副作用。空值返回 `-`。模板中仅调用 `${formatBeijingTime(p.created_at)}` 避免复杂内联表达式。

9. **项目列表操作列 + 详情页去按钮化**: 项目表格增加「操作」列（项目名称 | 描述 | 状态 | 创建时间 | 操作），每行提供编辑、删除、模板管理三个文本链接按钮。行点击保留跳转详情行为，操作按钮通过 `event.stopPropagation()` 阻止冒泡。项目详情页 `renderProjectDetail()` 移除底部按钮行（编辑/模板管理/删除项目），所有操作收敛到列表页操作列和行点击进入详情查看。

10. **项目模板变量管理页绑定公共变量**: 在「新增变量」按钮前放置「绑定公共变量」按钮，点击弹窗以复选框列表展示所有公共变量（列：选择、名称、变量值、类型），列表下方放置全选/取消全选复选框，确认后批量创建模板变量（复制公共变量的所有字段包括变量值，设置 `public_variables_id`），提交前检查同一模板下是否已存在相同 `public_variables_id` 的绑定（重复跳过并提示），功能与 `template-management` 绑定公共变量完全一致。变量列表表格列顺序：名称、默认值、类型、是否公共变量、页码、坐标/尺寸、字体、必填、操作；其中「是否公共变量」列根据 `public_variables_id` 是否有值显示"是"或"否"。操作列中，当 `public_variables_id` 有值时，「编辑」按钮渲染为禁用状态（置灰、不可点击），提示"公共变量不能直接修改，请在公共变量管理中修改"。

## Risks / Trade-offs

- [Risk] 项目删除为物理删除，不可恢复 → Mitigation：MVP 阶段可接受；后续可加入软删除（`deleted_at` 列）。
- [Trade-off] 无分页 → 模板和项目数量少（<100），全量返回可接受；后续量大再加。
- [Risk] `init.sql` 修改后需要手动对线上 DB 执行 `ALTER TABLE` → Mitigation：在 tasks 中明确拆分为 script 编写和 migration 执行两步，避免仅写文件不执行的问题。
