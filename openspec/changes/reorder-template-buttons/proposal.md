## Why

项目模板管理页面 header-bar 中"+ 上传模板"和"绑定公共模板"两个按钮顺序不符合操作频率逻辑，且均左对齐不够醒目。需要调整顺序为"绑定公共模板"在前，"+ 上传模板"在后，且两个按钮靠右对齐。

## What Changes

- 项目模板列表页 header-bar：交换两个按钮位置，"绑定公共模板"排在前，"上传模板"排在后
- 两个按钮容器添加 `margin-left: auto` 使其靠右对齐
- 统一两个按钮的样式风格（均使用 `btn-sm`）

## Capabilities

### New Capabilities
<!-- None - pure UI layout adjustment -->

### Modified Capabilities
<!-- None - no spec-level behavior changes -->

## Impact

- **`static/index.html`**: `renderProjectTemplates` 函数中 header-bar 部分的按钮顺序和样式调整
