## 1. Database

- [x] 1.1 Add `project_templates` table to `data/init.sql` (id, project_id FK→projects ON DELETE CASCADE, name, category, file_path, description, is_public BOOLEAN DEFAULT false, public_template_id INTEGER REFERENCES templates(id))
- [x] 1.2 Add `project_template_variables` table to `data/init.sql` (id, template_id FK→project_templates ON DELETE CASCADE, name, var_type, page, x, y, width, height, font_size, font_color, required, created_at, updated_at, UNIQUE(template_id, name))

## 2. Data Access Layer

- [x] 2.1 Create `data/project_templates.py` with `list_all(project_id, category=None)`, `get_by_id(template_id)`, `create(project_id, name, category, description, file_path, is_public=False, public_template_id=None)`, `update(template_id, name, category, description, file_path)`, `delete(template_id)`
- [x] 2.2 Create `data/project_variables.py` with `get_by_template_id(template_id)`, `get_by_id(variable_id)`, `create(template_id, name, var_type, page, x, y, width, height, font_size, font_color, required)`, `update(variable_id, **kwargs)`, `delete(variable_id)`, `bulk_create(template_id, variables)`
- [x] 2.3 Fix `data/project_templates.py` and `data/project_variables.py`: convert all `fetchall()`/`fetchone()` return values from raw psycopg2 tuples to dicts using `columns = [desc[0] for desc in cur.description]; dict(zip(columns, row))` pattern (currently returns tuple arrays, which `jsonify()` serializes as JSON arrays — frontend JS gets `undefined` for all fields like `template.name`)

## 3. API Routes — Project Template CRUD

- [x] 3.1 Add `GET /api/projects/<pid>/templates` handler (list with optional ?category= filter, requires auth)
- [x] 3.2 Add `POST /api/projects/<pid>/templates` handler (multipart upload PDF → store file in `uploads/project_templates/<id>/`, create DB record)
- [x] 3.3 Add `PUT /api/projects/<pid>/templates/<tid>` handler (update name, category, description; require auth)
- [x] 3.4 Add `DELETE /api/projects/<pid>/templates/<tid>` handler (delete DB record + remove PDF file; cascade deletes variables)

## 4. API Routes — Project Template Variables

- [x] 4.1 Add `GET /api/projects/<pid>/templates/<tid>/variables` handler (list variables ordered by page, name)
- [x] 4.2 Add `POST /api/projects/<pid>/templates/<tid>/variables` handler (create variable; return 409 on duplicate name)
- [x] 4.3 Add `PUT /api/projects/<pid>/templates/<tid>/variables/<vid>` handler (update variable fields)
- [x] 4.4 Add `DELETE /api/projects/<pid>/templates/<tid>/variables/<vid>` handler (delete variable)
- [x] 4.5 Add `POST /api/projects/<pid>/templates/<tid>/variables/import` handler (read .xlsx, call bulk_create, return imported/errors summary)
- [x] 4.6 Add `GET /api/projects/<pid>/templates/variables-template` handler (return .xlsx template with column headers matching variable fields)

## 5. SPA — Project Template Management View

- [x] 5.1 Create `renderProjectTemplates(projectId)` function (when binding a public template to the project, set `is_public=true` and `public_template_id=<source_template_id>` on the created record) in `static/index.html` (table layout with columns: 模板名称, 分类, 描述, 操作; title "签字页模板管理" with project name; upload button; category filter; empty state)
- [x] 5.2 Implement upload template modal in `renderProjectTemplates()` (form with name, category, description, file input; POST to `/api/projects/<pid>/templates`)
- [x] 5.3 Implement edit template modal in `renderProjectTemplates()` (pre-filled form; PUT to `/api/projects/<pid>/templates/<tid>`)
- [x] 5.4 Implement delete template action in `renderProjectTemplates()` (confirmation dialog; DELETE `/api/projects/<pid>/templates/<tid>`; refresh table)
- [x] 5.5 Add action column links: 编辑 (opens edit modal), 变量管理 (navigates to `#project/:id/templates/:tid/variables`, passing the template's 1-based display row index), 删除 (confirmation + delete)
- [x] 5.6 Implement return navigation button (← returns to `#home` project list)
- [x] 5.7 Add CSS styles for project-template-table, upload modal, empty state (reuse existing `.project-table`, `.modal-overlay` patterns)

## 6. SPA — Project Template Variable Management View

- [x] 6.1 Create `renderProjectTemplateVariables(projectId, templateId, rowIndex)` function (page title format: "<模板名称> #<序号>-签字变量"; table with columns: 变量名称, 类型, 页码, 坐标, 尺寸, 字体大小, 字体颜色, 操作; back to `#project/:id/templates`)
- [x] 6.2 Implement add variable modal (name(required), type, page, x, y, width, height, font_size, font_color fields; POST to `/api/projects/<pid>/templates/<tid>/variables`)
- [x] 6.3 Implement edit variable modal (pre-filled from current values; PUT)
- [x] 6.4 Implement delete variable with confirmation dialog
- [x] 6.5 Implement download Excel template link (GET `/api/projects/<pid>/templates/variables-template`)
- [x] 6.6 Implement Excel import flow (file input, POST to import endpoint, display imported count + errors); the 批量导入Excel button SHALL be placed after the 下载导入模板 button
- [x] 6.7 Add CSS for variable table and forms (reuse existing variable management styles)

## 7. SPA Route Integration

- [x] 7.1 Update `hashchange` router to parse `#project/:id/templates/:tid/variables` (4 segments → extract rowIndex from context and call `renderProjectTemplateVariables(projectId, templateId, rowIndex)`)
- [x] 7.2 Update `hashchange` router to parse `#project/:id/templates` (3 segments, ends with "templates" → renderProjectTemplates)
- [x] 7.3 Ensure existing `#project/:id` route (2 segments) still works for project detail
- [x] 7.4 Update project list action column "选择模板" link from `navigate('select-template/${p.id}')` to `navigate('project/${p.id}/templates')`
- [x] 7.5 Remove `#select-template/:id` view and its `renderSelectTemplate()` / `selectTemplate()` functions from SPA code

## 8. Labels and Text Updates

- [x] 8.1 Change sidebar link text "模板管理" to "签字页模板管理"
- [x] 8.2 Change `#templates` page title from "模板管理" to "签字页模板管理"

- [x] 9.6 Fix `app.py` `_extract_token()`: insert `request.form.get('token')` check between JSON body and query param checks, so multipart/form-data uploads (via `apiMultipart()`) can correctly authenticate instead of returning 401 "Token is required"

## 9. Testing

- [x] 9.1 Add integration tests for `GET/POST/PUT/DELETE /api/projects/<pid>/templates`
- [x] 9.2 Add integration tests for `GET/POST/PUT/DELETE /api/projects/<pid>/templates/<tid>/variables`
- [x] 9.3 Add integration test for `POST /api/projects/<pid>/templates/<tid>/variables/import` (valid + duplicate scenarios)
- [x] 9.4 Add integration test for `GET /api/projects/<pid>/templates/variables-template`
- [x] 9.5 Add integration test verifying cascade delete: delete project template → variables deleted + file removed
