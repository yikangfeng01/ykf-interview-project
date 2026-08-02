## ADDED Requirements

### Requirement: Project template list with table layout
The system SHALL display project templates in a table with columns: 模板名称, 分类, 描述, 操作, on the `#project/:id/templates` view. The page title SHALL be "签字页模板管理" with current project name shown as context. The table SHALL support empty state when no templates exist.

#### Scenario: Navigate to project template management from project list
- **WHEN** the user clicks "选择模板" in the project list action column
- **THEN** the system navigates to `#project/:id/templates` and displays a table of templates for that project with columns: 模板名称, 分类, 描述, 操作

#### Scenario: Empty template list
- **WHEN** the project has no templates
- **THEN** the system displays an empty state prompt instead of an empty table

### Requirement: Upload project template
The system SHALL allow uploading a PDF template file to a specific project via POST `/api/projects/<pid>/templates` with multipart/form-data containing name, category, description, and file. The file SHALL be stored under `uploads/project_templates/<template_id>/`.

#### Scenario: Successful template upload
- **WHEN** the user uploads a valid PDF file with name "IPO签字页", category "IPO", and optional description
- **THEN** the system creates a new record in `project_templates` table, stores the file, and returns the template data

#### Scenario: Upload template with token via FormData
- **WHEN** the user uploads a template file via multipart/form-data
- **THEN** the token sent through `formData.append('token', currentToken)` is correctly extracted from `request.form`
- **AND** the system authenticates the user successfully without returning 401 "Token is required"

#### Scenario: Upload with missing required fields
- **WHEN** the user submits the upload form without a template name
- **THEN** the system returns a 400 error with an appropriate message

### Requirement: Edit project template metadata
The system SHALL allow editing a project template's name, category, and description via PUT `/api/projects/<pid>/templates/<tid>`.

#### Scenario: Successful template edit
- **WHEN** the user updates a template's category from "IPO" to "并购"
- **THEN** the system updates the record in `project_templates` and returns the updated data

#### Scenario: Edit non-existent template
- **WHEN** the user attempts to edit a template that does not exist in the project
- **THEN** the system returns a 404 error

### Requirement: Delete project template with cascade
The system SHALL delete a project template and all its associated variables (cascade) via DELETE `/api/projects/<pid>/templates/<tid>`. The stored PDF file SHALL also be removed from the filesystem.

#### Scenario: Successful template deletion
- **WHEN** the user confirms deletion of a project template with associated variables
- **THEN** the system deletes the template, its variables, and the stored PDF file from the filesystem

#### Scenario: Confirm before delete in UI
- **WHEN** the user clicks "删除" in the project templates table
- **THEN** the system prompts a confirmation dialog before executing the deletion

### Requirement: SPA project template table action column
The system SHALL display 编辑, 变量管理, and 删除 links in each project template table row's action column.

#### Scenario: Click edit action
- **WHEN** the user clicks "编辑" on a template row
- **THEN** an edit modal opens pre-filled with the template's current name, category, and description

#### Scenario: Click variable management action
- **WHEN** the user clicks "变量管理" on a template row
- **THEN** the system navigates to `#project/:id/templates/:tid/variables`

#### Scenario: Click delete action
- **WHEN** the user clicks "删除" on a template row
- **THEN** a confirmation dialog appears; upon confirmation the template and its variables are deleted and the table refreshes

### Requirement: API response data as JSON objects
All API endpoints returning database rows SHALL serialize each row as a JSON object (key-value pairs), NOT as a JSON array. The frontend JavaScript SHALL be able to access fields by name (e.g. `template.name`, `template.category`).

#### Scenario: Template list returns objects not arrays
- **WHEN** the system queries `GET /api/projects/<pid>/templates`
- **THEN** each element in the response data array is a JSON object with keys `id`, `project_id`, `name`, `category`, `file_path`, `description`
- **AND** no element is a plain JSON array

#### Scenario: Variable list returns objects not arrays
- **WHEN** the system queries `GET /api/projects/<pid>/templates/<tid>/variables`
- **THEN** each element in the response data array is a JSON object with named keys matching column names
- **AND** no element is a plain JSON array

### Requirement: Category filter for project templates
The system SHALL support filtering project templates by category via `?category=` query parameter on GET `/api/projects/<pid>/templates`.

#### Scenario: Filter by category
- **WHEN** the user selects a category filter
- **THEN** only templates matching that category are displayed in the project template table
