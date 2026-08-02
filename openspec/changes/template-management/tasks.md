## 1. Database

- [x] 1.1 Add `signature_variables` table DDL to `data/init.sql`
- [x] 1.2 Execute migration to create table in database
- [x] 1.3 Add `value TEXT DEFAULT ''` column to `signature_variables` table DDL and execute migration

## 2. Data Layer

- [x] 2.1 Create `data/signature_variables.py` with CRUD functions (create, get_by_template, get_by_id, update, delete, bulk_create)
- [x] 2.2 Add `create()` function to `data/templates.py` for template insert
- [x] 2.3 Add `update()` function to `data/templates.py` for template metadata update
- [x] 2.4 Add `delete()` function to `data/templates.py` for template delete
- [x] 2.5 Update `data/signature_variables.py` create/update functions to support `value` parameter

## 3. Backend API — Templates

- [x] 3.1 Add `POST /api/templates` — multipart DOCX upload with metadata
- [x] 3.2 Add `PUT /api/templates/<id>` — edit template metadata, cascade update `project_templates` records where `public_template_id=<id>` with same name, category, description, file_path
- [x] 3.3 Add `DELETE /api/templates/<id>` — delete template, cascade delete `project_templates` records where `public_template_id=<id>`, cascade delete variables, and remove DOCX file
- [x] 3.4 Add `GET /api/templates` — list all templates (enhance existing if needed)

## 4. Backend API — Variables

- [x] 4.1 Add `GET /api/templates/<id>/variables` — list variables for a template
- [x] 4.2 Add `POST /api/templates/<id>/variables` — create a single variable
- [x] 4.3 Add `PUT /api/templates/<id>/variables/<vid>` — update a variable
- [x] 4.4 Add `DELETE /api/templates/<id>/variables/<vid>` — delete a variable
- [x] 4.5 Add `POST /api/templates/<id>/variables/import` — Excel bulk import with openpyxl
- [x] 4.6 Add `GET /api/templates/variables-template` — download Excel import template
- [x] 4.7 Update `POST /api/templates/<id>/variables` and `PUT /api/templates/<id>/variables/<vid>` to support `value` field, validate max 1024 characters

## 5. Frontend — Template Management View

- [x] 5.1 Add "模板管理" navigation button to `#home` view
- [x] 5.2 Implement `#templates` view with template list table/cards
- [x] 5.3 Implement upload template modal (DOCX file picker + name/category/description form)
- [x] 5.4 Implement edit template modal
- [x] 5.5 Implement delete template with confirmation
- [x] 5.6 Add CSS styles for the new views and modals

## 6. Frontend — Variable Management View

- [x] 6.1 Implement `#templates/<id>/variables` view (page title: "模板名称 - 签字变量"; variable table with columns: 变量名称, 类型, 页码, 坐标, ...)
- [x] 6.2 Implement add variable modal
- [x] 6.3 Implement edit variable modal
- [x] 6.4 Implement delete variable with confirmation
- [x] 6.5 Implement Excel bulk import upload UI
- [x] 6.6 Implement Excel template download button
- [x] 6.7 Add back navigation to `#templates`
- [x] 6.8 Add "变量值" textarea (maxlength=1024) to variable add/edit modal in `#templates/<id>/variables` view
- [x] 6.9 Update Excel import template and import logic to include `value` column

## 7. Dependencies & Cleanup

- [x] 7.1 Add `openpyxl` to `requirements.txt`
- [x] 7.2 Install `openpyxl` package (already installed: 3.1.5)
- [x] 7.3 Create `uploads/templates/` directory with `.gitkeep`

## 8. Database: public_variables_id FK

- [x] 8.1 Add `public_variables_id INTEGER REFERENCES public_variables(id) ON DELETE SET NULL` column to `signature_variables` table DDL in `data/init.sql`
- [x] 8.2 Execute ALTER TABLE migration on existing database (if `signature_variables` table already exists with data)

## 9. Backend: public_variables_id support in variable APIs

- [x] 9.1 Update `data/signature_variables.py` `create()` and `update()` to accept optional `public_variables_id` parameter
- [x] 9.2 Update `POST /api/templates/<id>/variables` to accept optional `public_variables_id` field in JSON body
- [x] 9.3 Update `PUT /api/templates/<id>/variables/<vid>` to accept optional `public_variables_id` field
- [x] 9.4 Ensure `GET /api/templates/<id>/variables` response includes `public_variables_id` in each variable record

## 10. Frontend: public variable binding UI

- [x] 10.1 In variable management page, add "绑定公共变量" button before "新增变量" button
- [x] 10.2 Implement bind public variable modal — calls `GET /api/public-variables` to list all public variables with checkboxes for multi-selection; select all/deselect all checkbox placed below the list; on confirm, batch-creates template variables for each selected public variable, copying all fields and setting `public_variables_id`
- [x] 10.2a On bind confirm, check for duplicate `public_variables_id` already bound in the same template; skip duplicates and report summary (`created: N, skipped: M, reasons: [...]`)
- [x] 10.3 Add "是否公共变量" column after "类型" column in variable list table, displaying "是" when `public_variables_id` is not null, "否" otherwise
- [x] 10.4 In variable edit modal, display current `public_variables_id` binding status (e.g., show "已绑定公共变量" indicator)
- [x] 10.5 In variable list operation column, disable the edit button when `public_variables_id` is not null; use `<button disabled>` to keep consistent button style with the adjacent delete button (same pattern as template-row edit restriction in app-dashboard)
- [x] 10.6 In `doBindPublicVars()`, change `loadTemplateVariables(templateId)` to `await loadVariables(templateId)` — wrong function name (`loadTemplateVariables` does not exist) and missing `await` prevent variable list from refreshing after binding
