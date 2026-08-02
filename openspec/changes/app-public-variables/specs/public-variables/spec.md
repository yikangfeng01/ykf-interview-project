## ADDED Requirements

### Requirement: Backend exposes public variables CRUD API

The system SHALL expose REST API endpoints for managing public variables that are not bound to any template.

#### Scenario: List all public variables
- **WHEN** the client sends `GET /api/public-variables` with a valid token
- **THEN** the server responds with HTTP 200 and a JSON array of all public variable records, ordered by name

#### Scenario: Create a new public variable
- **WHEN** the client sends `POST /api/public-variables` with a valid token and JSON body containing `name` and optional fields (`value`, `var_type`, `page`, `x`, `y`, `width`, `height`, `font_size`, `font_color`, `required`)
- **THEN** the server responds with HTTP 201 and the created variable record

#### Scenario: Create duplicate public variable name
- **WHEN** the client sends `POST /api/public-variables` with a `name` that already exists
- **THEN** the server responds with HTTP 409 and `{"error": "Variable name already exists"}`

#### Scenario: Update a public variable
- **WHEN** the client sends `PUT /api/public-variables/<variable_id>` with a valid token and JSON body containing fields to update
- **THEN** the server responds with HTTP 200 and the updated variable record

#### Scenario: Update non-existent public variable
- **WHEN** the client sends `PUT /api/public-variables/<variable_id>` with a variable_id that does not exist
- **THEN** the server responds with HTTP 404 and `{"error": "Variable not found"}`

#### Scenario: Delete a public variable
- **WHEN** the client sends `DELETE /api/public-variables/<variable_id>` with a valid token and the variable exists
- **THEN** the server responds with HTTP 204 and removes the variable from the database

### Requirement: Backend supports bulk import and template download for public variables

The system SHALL support Excel-based bulk import and template download for public variables.

#### Scenario: Import public variables from Excel
- **WHEN** the client sends `POST /api/public-variables/import` with a valid token and an `.xlsx` file containing required columns (`name`, `value`, `var_type`, `page`, `x`, `y`, `width`, `height`, `font_size`, `font_color`, `required`)
- **THEN** the server responds with HTTP 200 and `{"imported": <count>, "errors": [...]}`

#### Scenario: Import Excel with wrong format
- **WHEN** the client sends `POST /api/public-variables/import` with a file whose header row does not match the expected column names
- **THEN** the server responds with HTTP 400 and `{"error": "Invalid Excel format..."}`

#### Scenario: Download import template
- **WHEN** the client sends `GET /api/public-variables/import-template` with a valid token
- **THEN** the server responds with an `.xlsx` file containing the correct header row and one example row

### Requirement: Sidebar includes public variables management menu item

The system SHALL display a "公共变量管理" menu item in the sidebar navigation, as a first-level menu alongside "项目管理" and "签字页公共模板管理".

#### Scenario: Public variables menu item visible
- **WHEN** the user is authenticated and the shell layout is rendered
- **THEN** the sidebar SHALL display three menu items: "项目管理", "签字页公共模板管理", and "公共变量管理"

#### Scenario: Click public variables menu item
- **WHEN** the user clicks "公共变量管理" in the sidebar
- **THEN** the system navigates to `#public-variables` and the "公共变量管理" item is highlighted as active

#### Scenario: Active menu state for public-variables route
- **WHEN** the current hash is `#public-variables`
- **THEN** the `getActiveMenu()` function SHALL return `'public-variables'`, causing the sidebar to highlight the "公共变量管理" item

### Requirement: Public variables management page supports full variable CRUD

The system SHALL render a variable management page at `#public-variables` with the same functionality as the template-scoped variable management page (`renderVariables`), but without requiring a template ID.

#### Scenario: Render public variables page
- **WHEN** the user navigates to `#public-variables`
- **THEN** the system renders a page with title "公共变量管理", action buttons ("下载导入模板", "批量导入 Excel", "+ 新增变量"), and a table listing all public variables with columns: name, value, type, page, required, and actions (edit/delete)

#### Scenario: Add a new public variable
- **WHEN** the user clicks "+ 新增变量" on the public variables page, fills in the modal form, and clicks "保存"
- **THEN** the system sends `POST /api/public-variables` and refreshes the variable list on success

#### Scenario: Edit an existing public variable
- **WHEN** the user clicks "编辑" on a variable row, modifies fields in the modal form, and clicks "保存"
- **THEN** the system sends `PUT /api/public-variables/<id>` and refreshes the variable list on success

#### Scenario: Delete a public variable
- **WHEN** the user clicks "删除" on a variable row and confirms the action
- **THEN** the system sends `DELETE /api/public-variables/<id>` and removes the row from the table on success

### Requirement: Public variables import and template download work via Excel

The system SHALL support Excel import and template download on the public variables page.

#### Scenario: Bulk import via Excel
- **WHEN** the user clicks "批量导入 Excel", selects a valid `.xlsx` file, and clicks "导入"
- **THEN** the system sends `POST /api/public-variables/import`, displays the count of successfully imported rows, and shows any errors per row

#### Scenario: Download import template
- **WHEN** the user clicks "下载导入模板"
- **THEN** the system downloads an `.xlsx` file via `GET /api/public-variables/import-template` with correct headers and one example row

### Requirement: Public variables table has UNIQUE constraint on name only

The system database SHALL enforce uniqueness of public variable names globally, without requiring a template context.

#### Scenario: Insert duplicate name fails
- **WHEN** inserting a public variable with a `name` that already exists in `public_variables`
- **THEN** the database SHALL reject the insert with a unique constraint violation

#### Scenario: Same name is allowed across public_variables and signature_variables
- **WHEN** a variable named "甲方签字" exists in `public_variables` and a separate variable also named "甲方签字" is inserted into `signature_variables` (under a specific template)
- **THEN** both inserts SHALL succeed because the tables are independent
