## 1. Database: public_variables table

- [x] 1.1 Add `CREATE TABLE public_variables` DDL to `data/init.sql` — columns: id (SERIAL PK), name (VARCHAR(255) NOT NULL UNIQUE), value (TEXT), var_type (VARCHAR(50) DEFAULT 'signature'), page (INTEGER DEFAULT 1), x/y/width/height (FLOAT), font_size (INTEGER DEFAULT 12), font_color (VARCHAR(20) DEFAULT '#000000'), required (BOOLEAN DEFAULT true), created_at/updated_at (TIMESTAMP DEFAULT NOW()), UNIQUE(name)

## 2. Data Layer: data/public_variables.py

- [x] 2.1 Create `data/public_variables.py` with `get_all()` method (SELECT all, ORDER BY name)
- [x] 2.2 Add `get_by_id(variable_id)` method (SELECT by id, returns dict or None)
- [x] 2.3 Add `create(**kwargs)` method (INSERT, catch duplicate name → handle at route level, no template_id parameter)
- [x] 2.4 Add `update(variable_id, **kwargs)` method (UPDATE by id)
- [x] 2.4.1 Fix `update()` method: capture `cols = [desc[0] for desc in cur.description]` right after `cur.fetchone()` and BEFORE cascade UPDATEs, to avoid `'NoneType' object is not iterable` caused by cascade UPDATE clearing `cur.description`
- [x] 2.5 Add `delete(variable_id)` method (DELETE by id)
- [x] 2.6 Add `bulk_create(variables_list)` method (executemany INSERT, used by import route, no template_id)

## 3. API Routes: app.py

- [x] 3.1 Add `GET /api/public-variables` — call `public_variables.get_all()`, return JSON array with 200
- [x] 3.2 Add `POST /api/public-variables` — parse JSON body, call `public_variables.create()`, return 201; catch duplicate name → 409
- [x] 3.3 Add `PUT /api/public-variables/<int:variable_id>` — call `public_variables.update()`, return 200; not found → 404
- [x] 3.4 Add `DELETE /api/public-variables/<int:variable_id>` — call `public_variables.delete()`, return 204; not found → 404
- [x] 3.5 Add `POST /api/public-variables/import` — parse uploaded .xlsx (openpyxl), validate header row matches expected columns, call `public_variables.bulk_create()`, return `{"imported": N, "errors": [...]}`; bad format → 400
- [x] 3.6 Add `GET /api/public-variables/import-template` — generate .xlsx with header row + 1 example row using openpyxl, return as attachment
- [x] 3.7 Add `from data.public_variables import public_variables` to app.py imports

## 4. Frontend Sidebar & Navigation: static/index.html

- [x] 4.1 Add sidebar menu item `<div class="sidebar-item" data-menu="public-variables" onclick="navigate('public-variables')">公共变量管理</div>` below the "签字页公共模板管理" item
- [x] 4.2 Extend `getActiveMenu()`: add `if (['public-variables'].includes(view)) return 'public-variables';`

## 5. Frontend Route Dispatch: static/index.html

- [x] 5.1 In `render(view, params)` switch, add `case 'public-variables': return renderPublicVariables();` before the `default` case

## 6. Frontend renderPublicVariables(): static/index.html

- [x] 6.1 Implement `renderPublicVariables()` — page title "公共变量管理" (no template name prefix), action buttons row ("下载导入模板" / "批量导入 Excel" / "+ 新增变量"), variables table with columns (变量名, 变量值, 类型, 页码, X, Y, 宽×高, 必填, 操作)
- [x] 6.2 Implement `loadPublicVariables()` — calls `GET /api/public-variables` and renders table rows with edit/delete buttons
- [x] 6.3 Implement public variable modal (add/edit) — same form fields as `renderVariables` modal: name, value, var_type (dropdown), page, x, y, width, height, font_size, font_color, required; on save calls `POST /api/public-variables` (create) or `PUT /api/public-variables/<id>` (update)
- [x] 6.4 Implement Excel import modal — file input for .xlsx, calls `POST /api/public-variables/import`, shows import result (success count + errors if any)
- [x] 6.5 Implement template download — calls `GET /api/public-variables/import-template`, triggers file download
- [x] 6.6 Implement delete — confirm dialog, calls `DELETE /api/public-variables/<id>`, removes row on success
- [x] 6.7 Reuse existing `esc()`/`escAttr()`/`apiGet()`/`api()`/`apiUrl()`/`apiMultipart()`/`apiDownload()` helpers from renderVariables
