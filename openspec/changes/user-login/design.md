## Context

项目 `ykf-interview-project` 当前已有 `auth/` 后端认证模块（用户模型、bcrypt 密码哈希）。本次变更将其底层存储从 JSON 文件迁移到 PostgreSQL 数据库 `ykf-interview-project-db`，并重构前端为 SPA 架构：单个 `index.html` 通过客户端 hash 路由实现 `#login` 视图，为后续 `app-dashboard` 变更继续追加 `#home` 等视图奠定基础。

## Goals / Non-Goals

**Goals:**
- 使用 PostgreSQL 数据库 `ykf-interview-project-db` 持久化用户数据，提升并发安全性。
- 后端暴露 `POST /api/login`、`POST /api/verify`、`POST /api/logout` 三个端点。
- 前端实现 SPA 壳（`index.html`），`#login` 为登录视图，登录成功后跳转 `#home`。
- 保留 `auth/service.py` 对外认证接口不变，仅替换底层存储实现。

**Non-Goals:**
- 不实现用户注册、密码重置、账户管理。
- 不实现 OAuth、SSO 等第三方登录。
- 不实现角色权限（RBAC）。
- 不实现 `#home` 主页内容（由 `app-dashboard` 变更负责）。

## Decisions

1. **用户凭证存储使用 PostgreSQL，psycopg2 直写 SQL**  
   原因：PostgreSQL 提供 ACID 事务、并发安全、成熟生态。使用 psycopg2 直写 SQL 避免 ORM 学习成本，SQL 透明可控。  
   替代方案：SQLAlchemy ORM 提供更高抽象但增加学习曲线；继续 JSON 文件在 Web 多请求场景下有并发风险。

2. **密码哈希使用 `bcrypt`**  
   原因：业界标准密码哈希算法，自动加盐、抗暴力破解；Python `bcrypt` 库成熟稳定。  
   替代方案：`hashlib + pbkdf2` 需自行处理盐值管理；`argon2` 是新标准但依赖更重。  
   注：此决策不变，但哈希值存储位置从 JSON 文件改为 PostgreSQL `users.password_hash` 列。

3. **Web 框架选用 Flask**  
   原因：Flask 是 Python 生态中最轻量的 Web 框架，仅需注册路由即可暴露 API，无需额外脚手架。启动一个开发服务器即可运行。  
   替代方案：FastAPI 提供更好的异步支持和自动文档，但对本次 MVP 范围过重。

4. **前端 SPA 架构：单个 `index.html` + 客户端 hash 路由**  
   原因：登录页不再是独立页面，而是 SPA 的一个视图（`#login`）。后续 `app-dashboard` 变更可直接在同一文件中追加 `#home` 等视图，无需新建 HTML 文件。路由逻辑为简单 hashchange 事件监听 + DOM 切换。  
   替代方案：React/Vue 框架功能强大但引入构建工具链、状态管理等代价，MVP 阶段过度设计。

5. **API 端点设计**  

   | 端点 | 方法 | 请求体 | 成功响应 | 失败响应 |
   |------|------|--------|---------|---------|
   | `/api/login` | POST | `{"username":"x","password":"x"}` | 200 `{"token":"<uuid>"}` | 401/400 `{"error":"..."}` |
   | `/api/verify` | POST | `{"token":"<uuid>"}` | 200 `{"username":"x"}` | 401 `{"error":"..."}` |
   | `/api/logout` | POST | `{"token":"<uuid>"}` | 200 `{"message":"ok"}` | 400 `{"error":"..."}` |

   前端将 token 存入 `localStorage`，SPA 加载时调用 `/api/verify` 判断是否跳转 `#login` 或目标视图。登出时调用 `/api/logout` 清除服务端 token + 前端 localStorage。

## Risks / Trade-offs

- [Risk] 令牌明文传输且无过期时间 → Mitigation：后续可引入 HTTPS + JWT 过期机制。
- [Trade-off] 令牌存于 localStorage 存在 XSS 风险 → Mitigation：系统为内部工具，信任用户环境；后续可改为 HttpOnly Cookie。
- [Trade-off] psycopg2 直写 SQL 缺乏 ORM 的自动化迁移能力 → Mitigation：DDL 脚本记录在 `data/` 目录，版本化管理。
