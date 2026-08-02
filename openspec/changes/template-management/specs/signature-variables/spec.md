## ADDED Requirements

### Requirement: Signature variables CRUD operations
The system SHALL support creating, reading, updating, and deleting signature variables associated with a template.

#### Scenario: Create variable with all fields
- **WHEN** the user sends a POST with fields (name, value, var_type, page, x, y, width, height, font_size, font_color, required)
- **THEN** the system validates all fields, checks uniqueness of name within the template, and returns the created variable object

#### Scenario: Read variable list
- **WHEN** the user requests variables for a template ID
- **THEN** the system returns all variables ordered by page and name

#### Scenario: Update variable properties
- **WHEN** the user sends a PUT to update a variable with new field values
- **THEN** the system updates the record and returns the updated variable

#### Scenario: Delete variable from template
- **WHEN** the user sends a DELETE for a variable ID
- **THEN** the system removes the record and returns 204 No Content

### Requirement: Excel bulk import with template download
The system SHALL provide Excel-based bulk import of signature variables and a downloadable template file.

#### Scenario: Download variable import template
- **WHEN** the user requests GET `/api/templates/variables-template`
- **THEN** the system returns a `.xlsx` file with header row: name, value, var_type, page, x, y, width, height, font_size, font_color, required, and one example data row

#### Scenario: Successful bulk import
- **WHEN** the user uploads a valid .xlsx file containing 5 variable rows with unique names
- **THEN** the system imports all 5 rows and returns `{imported: 5, errors: []}`

#### Scenario: Partial import with duplicate names
- **WHEN** the user uploads a .xlsx file where 2 rows have names that already exist in the template
- **THEN** the system imports the non-duplicate rows, skips the duplicates, and returns `{imported: N, errors: [{row: X, message: "Variable name already exists"}]}`

#### Scenario: Invalid file format
- **WHEN** the user uploads a file that is not a valid .xlsx
- **THEN** the system returns a 400 error with message explaining the expected format

### Requirement: Variable field validation
The system SHALL validate variable fields for required values and valid types.

#### Scenario: Missing required fields
- **WHEN** the user submits a variable without a name field
- **THEN** the system returns a 400 error specifying that name is required

#### Scenario: Variable value exceeds max length
- **WHEN** the user submits a variable with a value field longer than 1024 characters
- **THEN** the system returns a 400 error with message "Variable value must not exceed 1024 characters"

#### Scenario: Invalid coordinate type
- **WHEN** the user submits a variable with non-numeric x or y values
- **THEN** the system returns a 400 error specifying the invalid field

#### Scenario: Default values applied
- **WHEN** the user creates a variable without specifying optional fields (page, width, height, font_size, font_color, required, value)
- **THEN** the system applies default values: page=1, width=120, height=40, font_size=12, font_color=#000000, required=true, value=""

### Requirement: Bind public variables to signature variables
The system SHALL allow binding a public variable to a template variable via the `public_variables_id` foreign key.

#### Scenario: Bind multiple public variables via checkbox selection
- **WHEN** the user clicks "绑定公共变量", selects one or more public variables using checkboxes in the modal list, and confirms
- **THEN** the system creates a template variable for each selected public variable, copying all fields from the public variable record and setting `public_variables_id` to the public variable's id; AND the bind modal closes and the variable list refreshes to show the newly created variables

#### Scenario: Select all and deselect all in bind modal
- **WHEN** the user clicks the select all checkbox below the list in the bind public variable modal
- **THEN** all row checkboxes are toggled accordingly (checked when header checkbox is checked, unchecked otherwise)

#### Scenario: Skip already-bound public variables
- **WHEN** the user confirms binding but one or more selected public variables already have a binding (same `public_variables_id`) in the current template
- **THEN** the system skips those already-bound entries, creates variables for the remaining selected public variables, and returns a summary indicating how many were created and how many were skipped as duplicates

#### Scenario: Variable update preserves public_variables_id
- **WHEN** the user edits a variable that was previously bound to a public variable
- **THEN** the system retains the existing `public_variables_id` value unless the user explicitly re-binds to a different public variable

#### Scenario: Variable list shows public variable binding status
- **WHEN** the user views the variable list for a template
- **THEN** the response includes a `public_variables_id` field, and the frontend displays a "是否公共变量" column showing "是" when `public_variables_id` is not null, "否" otherwise

#### Scenario: Edit button disabled for public-bound variable
- **WHEN** the user views the variable list and a variable has `public_variables_id` not null
- **THEN** the system renders the edit button in a disabled state using a `<button disabled>` element with visual style consistent with the adjacent delete button

#### Scenario: Public variable referenced is deleted
- **WHEN** a public variable bound to a template variable is deleted from `public_variables` table
- **THEN** the `public_variables_id` in the template variable is set to NULL (ON DELETE SET NULL), preserving the template variable data unchanged
