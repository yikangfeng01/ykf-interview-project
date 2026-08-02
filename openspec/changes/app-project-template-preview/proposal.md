## Why

项目模板的 DOCX 文件包含 `${变量名}` 占位符，用户在填写变量值后需要预览最终效果以确认内容正确性。当前缺少在线预览能力，用户必须下载 DOCX 后手动替换变量才能看到结果，流程繁琐且易出错。

## What Changes

- 项目模板列表新增「预览」按钮，点击后在新标签页打开渲染后的 PDF 预览
- 后端新增 `GET /api/projects/{project_id}/templates/{template_id}/preview` 端点
- 读取模板 DOCX 文件，将 `${\变量名\}` 占位符替换为实际变量值（项目变量 + 关联公共模板变量）
- 空值或 null 的变量**保留原始占位符不替换**
- 替换后通过 `docx2pdf`（macOS 依赖 Microsoft Word）转换为 PDF 并返回

## Capabilities

### New Capabilities
- `template-pdf-preview`: 项目模板 DOCX 占位符替换并生成 PDF 在线预览

### Modified Capabilities
<!-- 无已有 spec 需要修改 -->

## Impact

- **后端**: `app.py` — 新增 preview 路由（~70 行）
- **前端**: `static/index.html` — 模板列表新增预览按钮 + `previewProjectTemplate()` JS 函数
- **依赖**: `python-docx>=1.0.0`（DOCX 读写），`docx2pdf>=0.1.8`（DOCX→PDF 转换，macOS 依赖 Microsoft Word）
- **数据流**: `project_template_variables` + `signature_variables` → 合并 → DOCX 替换 → PDF
