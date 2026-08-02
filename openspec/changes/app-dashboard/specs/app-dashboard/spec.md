## ADDED Requirements

### Requirement: Home dashboard displays project list
The system SHALL display the authenticated user's projects on the `#home` view, along with a new project button and a logout icon button in the top-right corner.

#### Scenario: User lands on home after login
- **WHEN** the user successfully logs in and is redirected to `#home`
- **THEN** the system displays a list of projects owned by the current user, a "New Project" button, and a logout icon button in the top-right corner

#### Scenario: Home with no projects
- **WHEN** the user has no projects
- **THEN** the system displays an empty state message and a prominent "New Project" button

#### Scenario: Logout from home
- **WHEN** the user clicks the logout icon button in the top-right corner on `#home`
- **THEN** the system calls `POST /api/logout`, clears the token from `localStorage`, and navigates to `#login`

#### Scenario: Project list shows table column headers
- **WHEN** the user views the project list on `#home`
- **THEN** the system displays a table with column headers: 项目名称, 描述, 状态, 创建时间, 操作

#### Scenario: Project list shows formatted creation time
- **WHEN** the user views the project list on `#home`
- **THEN** each row's 创建时间 column displays the timestamp in `YYYY-MM-DD HH:mm:ss` format (PostgreSQL server timezone is `Asia/Shanghai`, `created_at` is stored as Beijing time directly; frontend formats the string as-is without timezone conversion)

#### Scenario: Project list shows action column with edit, delete, and select-template links
- **WHEN** the user views the project list on `#home`
- **THEN** each project row displays an "操作" column containing 编辑, 删除, and 模板管理 text links

#### Scenario: Click action buttons in project list
- **WHEN** the user clicks 编辑, 删除, or 模板管理 in the action column
- **THEN** the corresponding action executes (edit modal opens, delete confirmation shows, or navigate to template management) without navigating to the project detail page

### Requirement: User can create and manage projects
The system SHALL allow authenticated users to create, view, update, and delete their own projects.

#### Scenario: Create a new project
- **WHEN** the user provides a project name and optionally a description, then submits the new project form
- **THEN** the system creates a project with status `draft`, associates it with the current user, and adds it to the project list

#### Scenario: View project list
- **WHEN** the user navigates to `#home`
- **THEN** the system displays all projects belonging to the current user, showing name, description, status, and creation time

#### Scenario: View project detail
- **WHEN** the user clicks on a project from the list
- **THEN** the system displays the project's full details including name, description, status, and associated template (if any)

#### Scenario: Update project name or description
- **WHEN** the user edits the project name or description on the detail page and submits
- **THEN** the system updates the project and refreshes the display

#### Scenario: Delete a project
- **WHEN** the user confirms deletion of a project
- **THEN** the system removes the project permanently and navigates back to `#home`

#### Scenario: Unauthorized project access
- **WHEN** a user attempts to access a project they do not own
- **THEN** the system returns a 403 error

### Requirement: User can browse and select PDF signature page templates
The system SHALL allow users to browse available templates by category and select one for a project.

#### Scenario: Browse templates by category
- **WHEN** the user navigates to the template selection view for a project
- **THEN** the system displays all available templates, with a category filter allowing the user to narrow results

#### Scenario: Select a template for a project
- **WHEN** the user clicks a template and confirms selection
- **THEN** the system associates the template with the project, updates the project status to `template_selected`, and navigates back to the project detail

#### Scenario: Change selected template
- **WHEN** a project already has a template selected and the user selects a different one
- **THEN** the system updates the project's template association and confirms the change

#### Scenario: Template list is empty
- **WHEN** no templates exist in the database
- **THEN** the system displays a message indicating no templates are available

### Requirement: Backend exposes project management API endpoints
The system SHALL expose RESTful API endpoints for project CRUD operations, all requiring token-based authentication.

#### Scenario: List projects via API
- **WHEN** the client sends `GET /api/projects` with a valid token
- **THEN** the server responds with HTTP 200 and a JSON array of the user's projects

#### Scenario: Create project via API
- **WHEN** the client sends `POST /api/projects` with `{"name": "IPO-2026-001", "description": "2026年度IPO项目签字页"}` and a valid token
- **THEN** the server responds with HTTP 201 and the created project object (including `description`)

#### Scenario: Get project via API
- **WHEN** the client sends `GET /api/projects/:id` with a valid token and owns the project
- **THEN** the server responds with HTTP 200 and the project details

#### Scenario: Update project via API
- **WHEN** the client sends `PUT /api/projects/:id` with `{"name": "Updated Name", "description": "Updated description"}` and a valid token
- **THEN** the server responds with HTTP 200 and the updated project

#### Scenario: Delete project via API
- **WHEN** the client sends `DELETE /api/projects/:id` with a valid token and owns the project
- **THEN** the server responds with HTTP 204 and removes the project

#### Scenario: Create project with empty name
- **WHEN** the client sends `POST /api/projects` with `{"name": ""}` or missing name
- **THEN** the server responds with HTTP 400 and `{"error": "Project name is required"}`

### Requirement: Backend exposes template query API endpoints
The system SHALL expose API endpoints for listing available templates with optional category filtering.

#### Scenario: List all templates via API
- **WHEN** the client sends `GET /api/templates` with a valid token
- **THEN** the server responds with HTTP 200 and a JSON array of all templates

#### Scenario: Filter templates by category
- **WHEN** the client sends `GET /api/templates?category=share_transfer` with a valid token
- **THEN** the server responds with HTTP 200 and only templates matching that category

### Requirement: Template management page disables edit for public-bound templates
The system SHALL disable the edit button on the `#templates` view for project templates where `public_template_id IS NOT NULL`, preventing direct editing of templates bound from public template library.

#### Scenario: Edit button disabled for public-bound template
- **WHEN** the user views the template management page (`#templates`) and a project template record has `public_template_id IS NOT NULL`
- **THEN** the system renders the edit button in a disabled (grayed out, non-clickable) state, with a tooltip on hover: "绑定的公共模板不能修改，只能在签字页公共模板管理修改"

#### Scenario: Edit button enabled for self-created template
- **WHEN** the user views the template management page (`#templates`) and a project template record has `public_template_id IS NULL`
- **THEN** the system renders the edit button in an active (clickable) state, allowing the user to edit template metadata

#### Scenario: Project template list shows public template indicator column
- **WHEN** the user views the project template list on a project detail page
- **THEN** the system displays a "是否公共模板" column before the "描述" column, showing "是" when `public_template_id IS NOT NULL` and "否" when `public_template_id IS NULL`

### Requirement: Backend exposes template selection endpoint
The system SHALL expose an API endpoint to associate a template with a project.

#### Scenario: Select template via API
- **WHEN** the client sends `POST /api/projects/:id/select-template` with `{"template_id": 3}` and a valid token
- **THEN** the server updates the project's `template_id` and `status` to `template_selected`, responds with HTTP 200

#### Scenario: Select non-existent template
- **WHEN** the client sends `POST /api/projects/:id/select-template` with a `template_id` that does not exist
- **THEN** the server responds with HTTP 404 and `{"error": "Template not found"}`

### Requirement: Backend exposes single project template query endpoint
The system SHALL expose an API endpoint to retrieve a single project-scoped template by its ID.

#### Scenario: Get project template via API
- **WHEN** the client sends `GET /api/projects/:project_id/templates/:template_id` with a valid token and the template exists
- **THEN** the server responds with HTTP 200 and the template details (id, project_id, name, category, description, file_path, public_template_id)

#### Scenario: Get non-existent project template
- **WHEN** the client sends `GET /api/projects/:project_id/templates/:template_id` with a template_id that does not exist
- **THEN** the server responds with HTTP 404 and `{"error": "Template not found"}`

### Requirement: Variable management page title shows template name with row index
The system SHALL display the project template's name and row index when the user navigates to the variable management page from the project template list.

#### Scenario: Navigate to variable management from project template list
- **WHEN** the user clicks "变量管理" on a project template row (row index N)
- **THEN** the system navigates to the variable management page, displaying the page title in format `{templateName} #{N}-签字变量`

#### Scenario: Template name fetch falls back on API error
- **WHEN** the `GET /api/projects/:project_id/templates/:template_id` call returns a non-200 status
- **THEN** the system SHALL fall back to displaying `模板 #{templateId}` as the template name portion of the title, so the full title becomes `模板 #{templateId} #{N}-签字变量`

### Requirement: Project template variables support public variable binding
The system SHALL support binding public variables to project template variables via a checkbox-selection modal, with `public_variables_id` connecting to the `public_variables` table.

#### Scenario: project_template_variables table includes public_variables_id column
- **WHEN** a project template variable is created or updated
- **THEN** the system MAY store a `public_variables_id` referencing `public_variables.id` (nullable, ON DELETE SET NULL)

#### Scenario: Open bind public variable modal from project template variable list
- **WHEN** the user clicks "绑定公共变量" on the project template variable management page
- **THEN** a modal displays all public variables with checkboxes (列：选择、名称、变量值、类型), a "全选/取消全选" checkbox below the list, and a "确认绑定" button

#### Scenario: Select all and deselect all in bind modal
- **WHEN** the user clicks the select all checkbox below the list in the bind public variable modal
- **THEN** all row checkboxes are toggled accordingly (checked when select all is checked, unchecked otherwise)

#### Scenario: Skip already-bound public variables
- **WHEN** the user confirms binding but one or more selected public variables already have a binding (same `public_variables_id`) in the current project template
- **THEN** the system skips already-bound entries, creates variables for the remaining selected public variables, and reports a summary indicating how many were created and how many were skipped as duplicates

#### Scenario: Batch bind creates project template variables with public_variables_id
- **WHEN** the user confirms binding with selected public variables
- **THEN** the system creates a project template variable for each selected public variable, copying all fields (including the public variable's value as the template variable's value) and setting `public_variables_id` to the public variable's id

#### Scenario: Variable list shows is-public-variable column
- **WHEN** the user views the project template variable list
- **THEN** the system displays an "是否公共变量" column after the "类型" column, showing "是" when `public_variables_id` is not null and "否" when it is null

#### Scenario: Edit button disabled for public-bound project template variable
- **WHEN** the user views the project template variable list and a variable has `public_variables_id` not null
- **THEN** the system renders the edit button in a disabled (grayed out, non-clickable) state, indicating the variable is bound from a public variable and cannot be edited directly
