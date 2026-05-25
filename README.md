# YouTube 视频转飞书笔记 Skill

<img src="https://raw.githubusercontent.com/zhouxuan3550/youtube-to-feishu-note/main/assets/skill-intro.png" alt="YouTube 视频转飞书笔记 Skill" width="100%">

把 YouTube 视频处理成详尽中文笔记，并保存到飞书云文档。这个 skill 适合把长视频、教程、产品演示、访谈、工作流讲解沉淀成可复习、可检索、可复用的个人知识文档。

## 能做什么

- 自动获取 YouTube 原视频标题、频道、时长、发布日期等元数据。
- 通过 Supadata 抓取带时间戳的字幕。
- 按 3-8 分钟切段，避免长视频整理时漏掉内容。
- 生成中文深度资料，保留操作步骤、工具/API、Prompt、配置、案例和工作流。
- 发布前做质量检查，提醒标题后缀、时间戳覆盖、关键章节、代码块等问题。
- 发布到飞书云文档，并记录已处理视频，减少重复发布。

## 工作流

```text
YouTube 链接
  -> 获取视频元数据
  -> 检查是否已处理
  -> Supadata 抓取字幕
  -> 字幕自动切段
  -> 生成中文资料
  -> 发布前质量检查
  -> 保存到飞书云文档
```

## 使用方式

在 Codex 中直接引用这个 skill，并提供 YouTube 链接：

```text
[$youtube-to-feishu-note] 请处理这个视频，并保存到我的飞书云文档：
https://www.youtube.com/watch?v=VIDEO_ID
```

默认输出标题会使用“原视频标题的自然中文翻译”，不会额外添加“高保真学习文档”“视频整理”等固定后缀。

## 常用命令

获取视频元数据：

```bash
python3 scripts/get_youtube_metadata.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --out metadata.json
```

检查是否已处理：

```bash
python3 scripts/check_processed_video.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata metadata.json
```

抓取字幕：

```bash
python3 scripts/fetch_supadata_transcript.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --out transcript.json
```

切分字幕：

```bash
python3 scripts/prepare_transcript_chunks.py \
  transcript.json \
  --metadata metadata.json \
  --format markdown \
  --out chunks.md
```

发布前检查：

```bash
python3 scripts/validate_study_doc.py \
  "./中文视频标题.md" \
  --source-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata metadata.json
```

发布到飞书：

```bash
python3 scripts/publish_feishu_doc.py \
  "./中文视频标题.md" \
  --title "中文视频标题" \
  --source-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata metadata.json
```

## 环境要求

- `lark-cli`：用于创建和校验飞书云文档。
- Supadata API key：通过 `SUPADATA_API_KEY` 或 `X_API_KEY` 环境变量提供。
- `yt-dlp`：用于获取 YouTube 元数据。脚本内置 oEmbed fallback。

## 输出原则

这个 skill 的目标是“保留底层数据”，但不会逐字复刻完整版权字幕。它会用中文结构化还原视频内容，保留时间戳、操作步骤、演示例子、Prompt、配置方法和工作流逻辑。
