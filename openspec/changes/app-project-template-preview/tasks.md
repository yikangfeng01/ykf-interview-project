## 1. Dependencies

- [x] 1.1 Add `python-docx>=1.0.0` and `docx2pdf>=0.1.8` to `requirements.txt`
- [x] 1.2 Run `pip install python-docx docx2pdf` to verify both packages install successfully

## 2. Backend: Preview Endpoint

- [x] 2.1 Register `GET /api/projects/<project_id>/templates/<template_id>/preview` route with trailing slash support in `app.py`
- [x] 2.2 Implement `_require_auth()` check — return 401 if unauthenticated
- [x] 2.3 Look up template by `template_id` via `project_templates.get_by_id()` — return 404 if not found
- [x] 2.4 Validate `file_path` exists on disk — return 404 if DOCX file missing
- [x] 2.5 Gather `project_template_variables` by `template_id` — skip null/empty values (to preserve placeholder)
- [x] 2.6 If `public_template_id` is set, gather `signature_variables` — merge with project vars (project overrides public by name)
- [x] 2.7 Open DOCX with `python-docx` and replace `${varName}` placeholders in body paragraphs using two-pass strategy (per-run + cross-run fallback)
- [x] 2.8 Extend placeholder replacement to table cells (iterate all table rows/cells)
- [x] 2.9 Save replaced DOCX to temp file `<template_dir>/_preview.docx`
- [x] 2.10 Delete old `preview.pdf` if exists, then convert via `docx2pdf.convert(temp_docx, preview_pdf)`
- [x] 2.11 Return `send_file(preview_pdf, mimetype="application/pdf")` — clean up temp DOCX in `finally` block (success and error paths)

## 3. Frontend: Preview Button

- [x] 3.1 In `renderProjectTemplates()`, add a「预览」link next to the existing「编辑」and「删除」links in the template list row
- [x] 3.2 Implement `previewProjectTemplate(projectId, templateId)` function — construct preview URL with `token` query param and call `window.open(url, '_blank')`

## 4. Verification

- [x] 4.1 Upload a DOCX template containing `${变量名}` placeholders and set variable values
- [x] 4.2 Click preview — verify PDF opens in new tab with placeholders replaced
- [x] 4.3 Set one variable to empty — verify that placeholder is preserved in the PDF
- [x] 4.4 Bind a public template and verify merged variable values appear correctly in preview
- [x] 4.5 Verify preview still works after project variable overrides public variable
