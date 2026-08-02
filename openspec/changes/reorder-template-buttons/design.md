## Context

项目模板管理页面 `renderProjectTemplates` 的 header-bar 中有两个按钮："+ 上传模板"和"绑定公共模板"。当前顺序为上传模板在前、绑定在后，且均为左对齐。用户希望交换顺序并将按钮靠右对齐，使布局更符合视觉层级。

## Goals / Non-Goals

**Goals:**
- "绑定公共模板"按钮排在"+ 上传模板"按钮之前
- 两个按钮靠 header-bar 右侧对齐

**Non-Goals:**
- 不影响项目模板变量管理页面或其他页面

## Decisions

### Decision 1: 使用 Flexbox `margin-left: auto` 实现右对齐

**选择**: 给按钮容器（或第一个按钮前）添加 `margin-left: auto`，利用 header-bar 已有的 flex 布局将按钮推到右侧。

**理由**: header-bar 已使用 `display: flex; align-items: center` 布局，`margin-left: auto` 是最简洁的右对齐方案，无需修改现有 CSS 类。

### Decision 2: 仅调整 HTML 模板字符串中的按钮顺序和容器

**选择**: 在 `renderProjectTemplates` 的模板字符串中，将 `<button>绑定公共模板</button>` 移到 `<button>+ 上传模板</button>` 之前，并用 `<span style="margin-left: auto; display: flex; gap: 8px;">` 包裹两个按钮。

**理由**: 改动集中在 `static/index.html` 单个文件的单行模板中，影响范围极小，无需修改 CSS 或 JS 逻辑。

### Decision 3: 统一按钮样式为 `btn-sm`

**选择**: 将「绑定公共模板」按钮的样式从 `btn-sm btn-outline` 改为 `btn-sm`，与「+ 上传模板」保持一致。

**理由**: 两个按钮处于同一级别，使用统一样式能增强视觉一致性，避免用户对按钮层级产生困惑。

## Risks / Trade-offs

- 无风险。纯 UI 布局调整，不影响任何业务逻辑或 API。
