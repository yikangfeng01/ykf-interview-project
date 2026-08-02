## Why

当前签字页生成系统缺乏用户登录与身份认证机制，系统功能暴露在无权限管控的状态下。为了后续多用户协作、数据隔离和安全性保障，需要先实现基础的用户登录功能，确保只有合法用户才能访问系统。

## What Changes

- 基于 PostgreSQL 数据库 `ykf-interview-project-db` 存储用户凭证（`users` 表）。
- 后端暴露 `POST /api/login` 端点完成凭证校验并颁发会话令牌。
- 后端暴露 `POST /api/verify` 端点校验令牌有效性（供 SPA 前端路由守卫使用）。
- 后端暴露 `POST /api/logout` 端点清除服务端会话令牌。
- 前端 SPA 壳（`static/index.html`）包含 `#login` 路由视图，登录成功后跳转 `#home`（由 `app-dashboard` 变更实现）。

## Capabilities

### New Capabilities

- `user-login`: 用户登录认证能力，包括凭证验证、令牌校验、登出与 SPA 登录视图。

### Modified Capabilities

- 无现有能力发生需求变更。

## Impact

- 新增数据库：PostgreSQL `ykf-interview-project-db`，`users` 表。
- 新增依赖：`bcrypt`（密码哈希）、`Flask`（Web 框架）、`psycopg2-binary`（PostgreSQL 驱动）。
- 替换前端：`static/login.html` → `static/index.html`（SPA 壳，`#login` 视图）。
- 替换存储：`auth/store.py` JSON 文件读写 → PostgreSQL 直写 SQL。
- 保留：`auth/service.py` 对外接口不变，内部存储调用链切换。
