## ADDED Requirements

### Requirement: Template CRUD management
The system SHALL provide full CRUD operations for DOCX templates, including upload, edit, delete, and list.

#### Scenario: Upload a new template
- **WHEN** the user submits a multipart form with a DOCX file and metadata (name, category, description)
- **THEN** the system creates a new template record in the database, saves the DOCX file to `uploads/templates/<id>/`, and returns the created template object

#### Scenario: List all templates
- **WHEN** the user requests the template list with optional category filter
- **THEN** the system returns all templates ordered by category and name, with their metadata (id, name, category, file_path, description)

#### Scenario: Edit template metadata
- **WHEN** the user updates a template's name, category, description, or file_path via PUT
- **THEN** the system updates the database record, cascades the update to all `project_templates` records where `public_template_id` matches this template ID (synchronizing name, category, description, file_path), and returns the updated template

#### Scenario: Delete a template
- **WHEN** the user deletes a template by ID
- **THEN** the system cascades to delete all `project_templates` records where `public_template_id` matches this template ID, removes the template record and all associated signature variables, deletes the DOCX file from disk, and returns 204 No Content

#### Scenario: Delete non-existent template
- **WHEN** the user attempts to delete a template that does not exist
- **THEN** the system returns a 404 error with message "Template not found"

### Requirement: Template variables management
The system SHALL allow users to manage signature variables for each template, including CRUD operations and bulk Excel import.

#### Scenario: Add a new variable to a template
- **WHEN** the user creates a new variable with name, value (optional, max 1024 chars), var_type, page, coordinates, dimensions, font settings, and required flag
- **THEN** the system validates the variable name uniqueness within the template and returns the created variable

#### Scenario: Add duplicate variable name
- **WHEN** the user attempts to create a variable with a name that already exists in the same template
- **THEN** the system returns a 409 Conflict error

#### Scenario: List variables for a template
- **WHEN** the user requests all variables for a template
- **THEN** the system returns the complete list of variables with all their properties

#### Scenario: Update a variable
- **WHEN** the user updates a variable's properties via PUT
- **THEN** the system validates the target variable exists and updates the database record

#### Scenario: Delete a variable
- **WHEN** the user deletes a variable by ID
- **THEN** the system removes the variable record and returns 204 No Content

#### Scenario: Import variables from Excel
- **WHEN** the user uploads a .xlsx file with columns (name, value, var_type, page, x, y, width, height, font_size, font_color, required)
- **THEN** the system parses the file row by row, inserts valid rows, skips rows that conflict with existing variable names, and returns a summary with `{imported: N, errors: [{row, message}]}`

#### Scenario: Download Excel import template
- **WHEN** the user requests the variables import template
- **THEN** the system returns a downloadable .xlsx file with header row (name, value, var_type, page, x, y, width, height, font_size, font_color, required) and one example row

### Requirement: Template management SPA views
The system SHALL provide dedicated SPA views for template and variable management accessible from the home page.

#### Scenario: Navigate to template management from home
- **WHEN** the user clicks the "模板管理" button on the `#home` view
- **THEN** the system navigates to `#templates` view showing the list of all templates

#### Scenario: View template list
- **WHEN** the `#templates` view loads
- **THEN** the system displays all templates with name, category, description, and action buttons (edit, manage variables, delete)

#### Scenario: Open upload template modal
- **WHEN** the user clicks the "上传模板" button on `#templates`
- **THEN** the system displays a modal with file picker (DOCX only), name input, category input, and description textarea

#### Scenario: Navigate to variable management
- **WHEN** the user clicks the variable management button for a template on `#templates`
- **THEN** the system navigates to `#templates/<id>/variables` showing the variable list for that template

#### Scenario: View variable list
- **WHEN** the `#templates/<id>/variables` view loads
- **THEN** the system displays the template name as page title in format "<模板名称> - 签字变量", and shows all variables in a table with columns (名称, 变量值, 类型, 是否公共变量, 页码, 坐标, 宽高, 字号, 颜色, 必填, 操作); the "是否公共变量" column SHALL display "是" when `public_variables_id` is not null, and "否" otherwise; AND the edit button in the operation column is disabled (rendered as a `<button disabled>` with visual style consistent with the delete button in the same column) for variables where `public_variables_id` is not null

#### Scenario: Variable list refreshes after binding public variables
- **WHEN** the user confirms binding public variables and the creation is successful
- **THEN** the bind modal closes and the variable list reloads to display the newly bound variables
