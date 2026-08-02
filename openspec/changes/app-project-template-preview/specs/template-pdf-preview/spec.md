## ADDED Requirements

### Requirement: User can preview project template as PDF

The system SHALL provide a preview button on the project template list that, when clicked, opens the rendered PDF in a new browser tab.

#### Scenario: Click preview button opens PDF in new tab

- **WHEN** user clicks the「预览」button next to a project template in the template list
- **THEN** the system opens a new browser tab showing the rendered PDF with all `${变量名}` placeholders replaced by their actual values

#### Scenario: Authentication required for preview

- **WHEN** an unauthenticated request is made to the preview endpoint
- **THEN** the system returns HTTP 401 with an error message

#### Scenario: Template not found

- **WHEN** a preview request specifies a non-existent `template_id`
- **THEN** the system returns HTTP 404 with error `"Template not found"`

#### Scenario: DOCX file missing on disk

- **WHEN** a project template record exists but its `file_path` points to a non-existent file
- **THEN** the system returns HTTP 404 with error `"Template DOCX file not found on disk"`

### Requirement: Variable placeholder replacement in DOCX

The system SHALL replace all `${变量名}` tokens in the DOCX template with the corresponding variable values from both project-level and public template variables.

#### Scenario: Project variable replaced

- **WHEN** a template has `project_template_variables` containing `{"公司名称": "腾讯科技"}`
- **THEN** all occurrences of `${公司名称}` in the DOCX are replaced with `"腾讯科技"`

#### Scenario: Merged variables with project priority

- **WHEN** a template has `public_template_id=3` with `signature_variables` containing `{"签署地": "深圳"}`, and `project_template_variables` containing `{"签署地": "北京"}`
- **THEN** `${签署地}` is replaced with `"北京"` (project variable overrides public variable)

#### Scenario: Public variable used when project has none

- **WHEN** a template has `public_template_id=3` with `signature_variables` `{"签署地": "深圳"}`, and `project_template_variables` has no entry for "签署地"
- **THEN** `${签署地}` is replaced with `"深圳"` (falls back to public variable)

#### Scenario: Empty variable value preserves placeholder

- **WHEN** a variable has value `null` or empty string `""`
- **THEN** the original `${变量名}` placeholder is **not replaced** and remains in the output DOCX

#### Scenario: Variables replaced in paragraphs and tables

- **WHEN** the DOCX contains `${变量名}` placeholders inside both body paragraphs and table cells
- **THEN** all occurrences in both locations are replaced

### Requirement: DOCX to PDF conversion

The system SHALL convert the variable-replaced DOCX to PDF format using `docx2pdf` and return the PDF binary with MIME type `application/pdf`.

#### Scenario: PDF returned with correct MIME type

- **WHEN** a valid preview request succeeds
- **THEN** the system returns the PDF file with `Content-Type: application/pdf`

#### Scenario: PDF conversion failure

- **WHEN** the `docx2pdf` conversion step raises an exception
- **THEN** the system cleans up the temporary DOCX file and returns HTTP 500 with error `"PDF conversion failed: <details>"`

#### Scenario: Temporary files cleaned up

- **WHEN** a preview request completes (success or failure)
- **THEN** the temporary `_preview.docx` file is deleted from the template directory
