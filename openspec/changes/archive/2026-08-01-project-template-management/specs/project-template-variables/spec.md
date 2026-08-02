## ADDED Requirements

### Requirement: List project template variables
The system SHALL return all variables for a given project template via GET `/api/projects/<pid>/templates/<tid>/variables`, ordered by page and name.

#### Scenario: View variables for a project template
- **WHEN** the user navigates to the variable management view for a project template
- **THEN** the system displays all variables in a table with columns: 变量名称, 类型, 页码, 坐标, 尺寸, 字体大小, 字体颜色, 操作

#### Scenario: Empty variable list
- **WHEN** the project template has no variables defined
- **THEN** the variable management page shows an empty state prompt

### Requirement: Create project template variable
The system SHALL allow creating a new variable for a project template via POST `/api/projects/<pid>/templates/<tid>/variables`. The variable name MUST be unique within the template.

#### Scenario: Successful variable creation
- **WHEN** the user adds a variable with name "签名", type "signature", page 1, coordinates (100, 200), size 120x40
- **THEN** the system creates the variable in `project_template_variables` and returns the created record

#### Scenario: Duplicate variable name
- **WHEN** the user attempts to create a variable with a name that already exists for the same template
- **THEN** the system returns a 409 error with an appropriate message

### Requirement: Update project template variable
The system SHALL allow updating a project template variable's fields via PUT `/api/projects/<pid>/templates/<tid>/variables/<vid>`.

#### Scenario: Successful variable update
- **WHEN** the user changes a variable's font_size from 12 to 14
- **THEN** the system updates the record and returns the updated data

#### Scenario: Update non-existent variable
- **WHEN** the user attempts to update a variable that does not exist
- **THEN** the system returns a 404 error

### Requirement: Delete project template variable
The system SHALL allow deleting a project template variable via DELETE `/api/projects/<pid>/templates/<tid>/variables/<vid>`.

#### Scenario: Successful variable deletion
- **WHEN** the user clicks delete on a variable and confirms
- **THEN** the system removes the variable record and refreshes the variable table

### Requirement: Excel bulk import for project template variables
The system SHALL support importing variables from an Excel file (.xlsx) via POST `/api/projects/<pid>/templates/<tid>/variables/import`.

#### Scenario: Successful bulk import
- **WHEN** the user uploads a valid Excel file with 5 variable rows for a project template
- **THEN** the system imports all 5 variables, returns the import count, and displays them in the table

#### Scenario: Partial import with errors
- **WHEN** the user uploads an Excel file where some rows have duplicate names
- **THEN** the system imports valid rows, skips duplicates, and returns a summary with counts and error details

### Requirement: Download Excel import template for project variables
The system SHALL provide an Excel template download for project variable import via GET `/api/projects/<pid>/templates/variables-template`.

#### Scenario: Download template
- **WHEN** the user clicks "下载导入模板" on the project template variable management page
- **THEN** the system responds with an .xlsx file containing the correct column headers

### Requirement: SPA variable management for project templates
The system SHALL render a variable management view at `#project/:id/templates/:tid/variables` with add/edit/delete/import functionality. The action buttons SHALL be ordered as: 新增变量, 下载导入模板, 批量导入Excel. The page title SHALL display the template name and its display row index (1-based) in the format "<模板名称> #<序号>-签字变量", e.g. "IPO签字页 #1-签字变量".

#### Scenario: Navigate to project template variables
- **WHEN** the user clicks "变量管理" on a project template row
- **THEN** the system navigates to the variable management view with page title in the format "<templateName> #<rowIndex>-签字变量", showing all variables for that project template

#### Scenario: Add variable via modal
- **WHEN** the user clicks "新增变量" on the project template variable management page
- **THEN** a modal form opens with fields for all variable properties (name(required), type, page, position, size, font, color)

#### Scenario: Back navigation from project variable management
- **WHEN** the user clicks "返回" on the project template variable management page
- **THEN** the system navigates back to `#project/:id/templates`
