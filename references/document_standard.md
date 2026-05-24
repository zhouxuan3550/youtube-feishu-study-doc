# Document Standard

Use this structure for YouTube-to-Feishu learning documents:

```markdown
# <原视频标题的自然中文翻译>

来源视频：<url>
原视频标题：<original title>
频道：<channel>
视频时长：<duration>
发布日期：<upload date>

说明：本文按视频时间线整理，目标是保留底层信息、操作步骤、演示案例、工作流逻辑和可复用 Prompt。由于整段字幕属于视频原始版权内容，本文不逐字复刻完整字幕，而采用高保真中文转写、结构化还原和可复制工作流模板。

## 一、视频主旨

...

## 二、按时间戳递进的完整内容整理

### 00:00-03:00｜<section title>

#### 完整字幕/关键原文内容：

...

#### 操作步骤还原：

...

#### 适合复用的 Prompt：

```text
...
```

## 三、配置与工作流代码块

...

## 四、可复用方法论总结

...

## 五、关键底层数据索引

| 时间段 | 主题 | 工具/API | Prompt/指令 | 操作步骤 | 案例/演示 | 产物 |
|---|---|---|---|---|---|---|

## 六、可复用工作流

...
```

Writing rules:

- Use the translated original video title as the document title. Do not add generic suffixes such as `高保真学习文档`.
- Prefer dense, detailed Chinese prose.
- Do not collapse a long demo into a one-line takeaway.
- Preserve concrete UI actions, file/folder names, prompts, APIs, integrations, and validation steps.
- Use code blocks for prompts, CLI commands, automations, and configuration logic.
- Keep timestamp ranges coarse enough to be readable, usually 3-10 minutes per section depending on topic changes.
- Avoid claiming exact words unless quoting a short excerpt.
- For videos longer than 60 minutes, write part files first and then merge into the same final structure.
- Keep the final index structured enough for later retrieval: tools/APIs, prompts, operation steps, examples, decision rules, and reusable workflows.
