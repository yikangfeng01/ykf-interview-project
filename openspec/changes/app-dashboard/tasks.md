## 1. Database Schema

- [x] 1.1 Add `projects` table DDL to `data/init.sql` (id, name, status, template_id FK, created_by, created_at, updated_at)
- [x] 1.2 Add `templates` table DDL to `data/init.sql` (id, name, category, file_path, description)
- [x] 1.3 Create `data/seed_templates.py` to insert sample template records (e.g., 股权转让签字页、增资协议签字页)

## 2. Data Access Layer

- [x] 2.1 Create `data/projects.py` module: psycopg2 SQL functions (list_by_user, get_by_id, create, update, delete)
- [x] 2.2 Create `data/templates.py` module: psycopg2 SQL functions (list_all, list_by_category, get_by_id)

## 3. Flask API Endpoints

- [x] 3.1 Add auth middleware/helper in `app.py` to extract and verify token from request (body or header)
- [x] 3.2 Register `GET /api/projects` and `POST /api/projects` routes
- [x] 3.3 Register `GET /api/projects/:id`, `PUT /api/projects/:id`, `DELETE /api/projects/:id` routes
- [x] 3.4 Register `GET /api/templates` route with optional `?category=` query param
- [x] 3.5 Register `POST /api/projects/:id/select-template` route

## 4. SPA Views

- [x] 4.1 Implement SPA route parser: extract view and params from `window.location.hash`
- [x] 4.2 Implement `#home` view: fetch project list via API, render list/cards, logout button, new project button
- [x] 4.3 Implement new project dialog/form in `#home`: input name, POST to API, refresh list
- [x] 4.4 Implement `#project/:id` view: fetch project detail, show name/status/template, edit/delete/select-template actions
- [x] 4.5 Implement edit project name inline on `#project/:id`
- [x] 4.6 Implement delete project with confirmation dialog on `#project/:id`
- [x] 4.7 Implement `#project/:id/select-template` view: fetch templates, category filter, select and bind to project

## 5. Integration & Polish

- [x] 5.1 Add CSS styling for `#home`, `#project/:id`, and template selection views (consistent with login view)
- [x] 5.2 Add loading indicators for API calls across all views
- [x] 5.3 Add API integration tests for project CRUD endpoints
- [x] 5.4 Add API integration tests for template listing and selection endpoints
- [x] 5.5 Manually verify end-to-end flow: login → home → create project → select template → view project → delete project → logout

## 6. Sidebar Shell Layout

- [x] 6.1 Refactor CSS: replace centered-card body layout with flexbox three-zone layout (topbar + sidebar + content)
- [x] 6.2 Implement shell creation logic: on post-login, render persistent `.topbar` + `.layout > .sidebar + #content-area` into `#app`, leaving `#login` to render independently without shell
- [x] 6.3 Implement sidebar menu UI: two vertical menu items (项目管理, 签字页公共模板管理), active state driven by current hash via `getActiveMenu()` helper
- [x] 6.4 Refactor all authenticated view render functions (`renderHome`, `renderProjectDetail`, `renderSelectTemplate`, `renderTemplates`, `renderVariables`) to target `#content-area` instead of `#app`
- [x] 6.5 Implement `renderShellIfNeeded()` guard: route dispatcher checks if shell exists; if not (e.g. direct `#home`), create shell before rendering content
- [x] 6.6 Wire sidebar menu click to `navigate()`: clicking 项目管理 → `#home`, 签字页公共模板管理 → `#templates`
- [x] 6.7 Adjust content area inner styles: remove max-width centering, use fluid layout with appropriate padding inside `#content-area`

## 7. Project Description Column

- [x] 7.1a Write `description TEXT` column DDL and `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` migration to `data/init.sql`
- [x] 7.1b Execute the `ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT;` migration against the live database (`psql -d ykf-interview-project-db -c "ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT;"`)
- [x] 7.2 Update `data/projects.py`: add `description` to `list_by_user()` SELECT, `get_by_id()` SELECT, `create()` params, and `update()` allowed fields
- [x] 7.3 Update `POST /api/projects` in `app.py` to parse and pass `description` from request body
- [x] 7.4 Update `PUT /api/projects/:id` in `app.py` to parse and pass `description` from request body
- [x] 7.5 Update `static/index.html` — new project modal: add optional `description` textarea input; wire to create API call
- [x] 7.6 Update `static/index.html` — project list (`loadProjects`): add description column to the table/card (truncated, shown below project name)
- [x] 7.7 Update `static/index.html` — project detail view (`renderProjectDetail`): display description; update edit modal to support editing description alongside name

## 8. Project List Column Headers

- [x] 8.1 Refactor `loadProjects()` in `static/index.html`: replace `<ul>` card layout with `<table>` layout, each row renders project name, description (truncated 80 chars), status badge, creation time
- [x] 8.2 Add `<thead>` row to project table with column headers: 项目名称, 描述, 状态, 创建时间
- [x] 8.3 Add CSS styles for `.project-table`, `.project-table th`, `.project-table td` with consistent spacing, borders, and responsive horizontal scroll
- [x] 8.4 Update empty state handling: when no projects exist, display empty state prompt instead of empty table row
- [x] 8.5 Register custom `ISOJSONProvider` in `app.py` to serialize `datetime` as ISO format (`"2026-08-01T15:28:37"`) instead of Flask's default HTTP-date format (`"Sat, 01 Aug 2026 15:28:37 GMT"`); `formatBeijingTime(dbStr)` in frontend does pure string formatting (`replace('T',' ')` + `substring(0,19)`) since DB stores Beijing time directly

## 9. Action Column & Detail Page De-button

- [x] 9.1 Add "操作" (5th) column to project-table `<thead>` in `loadProjects()`
- [x] 9.2 Render 编辑, 删除, 模板管理 text-link buttons in each row's action cell, with `event.stopPropagation()` to prevent row click navigation
- [x] 9.3 Wire actions: edit opens edit modal (`showEditProjectModal`), delete calls `deleteProject()`, select-template navigates to `#project/:id/select-template`
- [x] 9.4 In `renderProjectDetail()`, remove all action buttons row (edit/select-template/delete) from project detail view
- [x] 9.5 Add CSS for `.action-links` class (inline text links with separator spacing) in `<style>`
- [x] 9.6 Fix `deleteProject()`: replace `navigate('home')` with `loadProjects()` since user is already on `#home` when deleting from list action column (navigating to same hash does not trigger `hashchange`)

## 10. Template Management Edit Restriction (Replace `is_public` with `public_template_id`)

- [x] 10.1 Remove `is_public` column from `project_templates` table: write `ALTER TABLE project_templates DROP COLUMN IF EXISTS is_public` migration in `data/init.sql` and execute against live database
- [x] 10.2 Remove `is_public` parameter and column from `data/project_templates.py` `create()` function
- [x] 10.3 Remove `is_public` from `app.py` project template INSERT statement (upload route line 1056 and RETURNING line 1058)
- [x] 10.4 In `loadProjectTemplates()` frontend (`static/index.html` line 899), replace `t.is_public` with `t.public_template_id` — render "是" when `public_template_id` has a value and "否" otherwise
- [x] 10.5 In `loadProjectTemplates()` frontend (`static/index.html` line 902), disable edit button when `public_template_id` has value (same visual: grayed out, `pointer-events: none`, tooltip "绑定的公共模板不能修改，只能在签字页公共模板管理修改")

## 11. Project Template Single Query & Variable Management Title

- [x] 11.1 Add `GET /api/projects/<project_id>/templates/<template_id>` route handler in `app.py` to return a single project template by id (data layer `project_templates.get_by_id()` already exists)
- [x] 11.2 In `renderProjectTemplateVariables()`, fetch template name via the single template API and display page title as `{templateName} #{rowIndex}-签字变量`, with fallback to `模板 #{templateId}` when API call fails

## 12. Public Variable Binding for Project Template Variables

- [x] 12.1 Add `public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE SET NULL` column DDL and migration to `data/init.sql` for `project_template_variables` table
- [x] 12.2 Update `data/project_variables.py`: support `public_variables_id` in `create()`, `update()`, `bulk_create()`
- [x] 12.3 Add "绑定公共变量" button before "新增变量" on project template variable management page
- [x] 12.4 Implement bind public variable modal — same behavior as template-management: checkbox multi-selection, select all/deselect all checkbox below list, duplicate binding check, batch create with summary report
- [x] 12.5 Add "是否公共变量" column after "类型" in project template variable management table; show "是" when `public_variables_id` is not null, "否" otherwise
- [x] 12.6 Fix bind public variable value: pass `data-value` in checkbox dataset and use it in payload instead of hardcoded empty string; apply to both `doProjectBindPublicVars()` and `doBindPublicVars()`
- [x] 12.7 In project template variable list operation column, disable the edit button when `public_variables_id` is not null (same pattern as template management edit restriction in 10.1)

## 13. System Title Font Enlargement

- [x] 13.1 In `static/index.html` shell rendering, add CSS class `.topbar-title { font-size: 3em; }` (or inline style) to the "签字页项目管理系统" title element in the topbar

## 14. System Title Font Shrink

- [x] 14.1 In `static/index.html`, change `.topbar-title { font-size: 3em }` → `.topbar-title { font-size: 1.5em }` (shrink by 2x)
