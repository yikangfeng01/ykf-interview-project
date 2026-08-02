## Context

项目模板为 DOCX 文件，内含 `${变量名}` 占位符。变量值来源：
- `project_template_variables` 表（项目级变量，按 `template_id` 查询）
- `signature_variables` 表（公共模板变量，通过 `project_templates.public_template_id` 关联）

当前操作系统为 macOS，已安装 Microsoft Word for Mac，因此可使用 `docx2pdf` 进行 DOCX→PDF 转换。

## Goals / Non-Goals

**Goals:**
- 项目模板列表页提供「预览」按钮，点击后新标签页打开 PDF
- 后端读取 DOCX → 替换 `${变量名}` → 转 PDF → 返回二进制流
- 变量合并：项目变量覆盖同名公共变量
- 空值/null 变量保留原占位符不替换

**Non-Goals:**
- 不支持直接编辑 DOCX 内容
- 不支持批量预览（一次只预览一个模板）
- 不添加水印或页码
- 不生成预览历史记录

## Decisions

### 1. DOCX 变量替换：python-docx

选用 `python-docx` 而非直接操作 XML，因为：
- 提供段落/表格/run 级别的高层 API，避免手动解析 OOXML
- 广泛使用，社区成熟
- 已包含在项目依赖中

**两遍替换策略**：
- **Pass 1**: 逐 run 替换 — 处理大多数情况（占位符在单个 run 内）
- **Pass 2**: fallback 跨 run 合并 — 处理 Word 将 `${varName}` 拆到多个 run 的情况，重新构建段落文本后替换

### 2. DOCX→PDF 转换：docx2pdf（依赖 Microsoft Word）

| 方案 | macOS 支持 | 排版保真度 | 依赖 |
|------|-----------|-----------|------|
| `docx2pdf` (JXA → Word) | ✅ | 完美 | Microsoft Word for Mac |
| LibreOffice headless | ✅ | 很好 | `brew install libreoffice` |
| python-docx + weasyprint | ✅ | 差 | 无 |

选择 `docx2pdf`：当前环境已安装 Word，排版保真度最高，无额外安装。

### 3. 认证方式：Query String Token

`window.open` 无法设置 HTTP 请求头，因此将 token 作为 `?token=xxx` 查询参数传递。preview 端点复用 `_require_auth()` 中间件验证。

### 4. 临时文件管理

- 替换后的临时 DOCX 保存在原始模板目录下（`_preview.docx`）
- 转换完成后在 `finally` 块中清理临时 DOCX
- 旧 `preview.pdf` 在每次转换前先删除，避免残留

## Risks / Trade-offs

- **[Word 并发风险]** docx2pdf 调用 Word 非 headless，高并发时可能相互干扰 → 当前项目为单用户场景，风险低
- **[大文件性能]** 大型 DOCX（>10MB）替换和转换可能较慢 → 短期可接受，长期可考虑异步任务队列
- **[占位符残留]** 若变量名包含特殊正则字符可能不匹配 → 使用简单字符串 `replace` 而非 regex，避免转义问题
