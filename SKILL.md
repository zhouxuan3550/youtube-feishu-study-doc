---
name: youtube-feishu-study-doc
description: Create high-fidelity Chinese study documents from YouTube videos and save them to Feishu/Lark cloud docs. Use when the user asks to process, extract, transcribe, summarize, study, archive, or save a YouTube video to Feishu/Lark, especially with requirements like "拒绝高度概括", "保留底层数据", "按时间戳", "完整字幕/关键原文内容", "配置与工作流代码块", or "保存到飞书云文档".
---

# YouTube Feishu Study Doc

## Overview

Use this workflow to turn a YouTube video into a detailed Chinese learning document, then publish it to Feishu with `lark-cli`.

Important boundary: do not publish a full verbatim transcript of copyrighted video content. Produce a high-fidelity learning document instead: timestamped Chinese paraphrase, detailed operation steps, examples, key short quotes when necessary, and reusable prompts/config/workflow blocks.

## Workflow

1. Get video metadata and check duplicates.
   - Run `scripts/get_youtube_metadata.py` first when possible.
   - Use the original title, channel, duration, upload date, and video ID in the document metadata.
   - Translate the original video title into a natural Chinese title for the Markdown H1, Feishu title, and local filename.
   - Run `scripts/check_processed_video.py URL --metadata metadata.json` before republishing the same URL.

2. Extract a timestamped transcript.
   - Prefer `scripts/fetch_supadata_transcript.py`.
   - Use Supadata via `SUPADATA_API_KEY` or `X_API_KEY`.
   - If no API key is in the environment, inspect the current shell/config context or ask the user for the key.

3. Prepare transcript chunks before writing.
   - Run `scripts/prepare_transcript_chunks.py transcript.json --metadata metadata.json --format markdown --out chunks.md`.
   - Use 3-8 minute sections by default. For videos longer than 60 minutes, write in multiple parts and merge before publishing.
   - Use chunks as coverage scaffolding so every part of the video is represented.

4. Build a Markdown study document.
   - Follow `references/document_standard.md`.
   - Use the translated video title directly as the Markdown H1 and Feishu title. Do not append generic suffixes such as `高保真学习文档`, `学习文档`, or `视频整理` unless the user explicitly asks.
   - Use timestamp sections. Keep operational detail, tool names, UI paths, commands, prompts, configs, and examples.
   - Preserve "底层数据" as structured facts and steps, not as full verbatim transcript.
   - Include a section named `三、配置与工作流代码块`.

5. Save the local Markdown in the current workspace before publishing.
   - Use a descriptive filename based on the translated video title: `<translated-video-title>.md`.
   - Include source URL and a short note about transcript/copyright handling.
   - For organization, prefer a stable workspace folder such as `youtube-feishu-docs/` when processing many videos.

6. Validate before publishing.
   - Run `scripts/validate_study_doc.py document.md --source-url URL --metadata metadata.json`.
   - Fix errors before publishing. Warnings are acceptable only when the video lacks relevant prompts, commands, or workflows.

7. Publish to Feishu.
   - Prefer `scripts/publish_feishu_doc.py`.
   - Default parent position is `my_library`.
   - Use `--as user` unless the user asks for bot identity.
   - Pass `--source-url URL --metadata metadata.json` so duplicate records are updated.
   - Verify by fetching the outline after creation.

8. Report only the useful result.
   - Provide the Feishu document URL.
   - Provide the local backup path.
   - Mention any limitation, such as unavailable transcript or failed upload.

## Commands

Fetch transcript:

```bash
python3 /Users/oliverchow/.codex/skills/youtube-feishu-study-doc/scripts/get_youtube_metadata.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --out metadata.json

python3 /Users/oliverchow/.codex/skills/youtube-feishu-study-doc/scripts/check_processed_video.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata metadata.json

python3 /Users/oliverchow/.codex/skills/youtube-feishu-study-doc/scripts/fetch_supadata_transcript.py \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --out transcript.json

python3 /Users/oliverchow/.codex/skills/youtube-feishu-study-doc/scripts/prepare_transcript_chunks.py \
  transcript.json \
  --metadata metadata.json \
  --format markdown \
  --out chunks.md
```

Publish Markdown to Feishu:

```bash
python3 /Users/oliverchow/.codex/skills/youtube-feishu-study-doc/scripts/validate_study_doc.py \
  "./video-study.md" \
  --source-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata metadata.json

python3 /Users/oliverchow/.codex/skills/youtube-feishu-study-doc/scripts/publish_feishu_doc.py \
  "./video-study.md" \
  --title "中文视频标题" \
  --source-url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata metadata.json
```

## Quality Checklist

Before publishing, ensure the document has:

- Source URL and processing note.
- Original video title, channel, duration, and upload date when available.
- Timestamped sections throughout the video.
- `完整字幕/关键原文内容：` under each timestamp, written as high-fidelity Chinese paraphrase plus short necessary quotes only.
- Detailed operation steps, not just conclusions.
- Tool names and object names retained, such as Codex, Figma, Vercel, Typefully, Supabase, Remotion, TestFlight.
- A dedicated `三、配置与工作流代码块` section with copyable prompts/workflows.
- A final structured index/table with tools/APIs, prompts, operation steps, examples, decision rules, and reusable workflows when present.
- No generic title suffix unless explicitly requested.

## Failure Handling

- If Supadata returns no transcript, try `mode=auto` and check available languages. If still unavailable, explain that the video has no accessible transcript.
- If `lark-cli` is missing, tell the user the local Markdown is ready and ask them to install or expose the CLI.
- If `lark-cli docs +create` reports `--content is required`, use v2 syntax: `--doc-format markdown --content @./file.md`.
- If `@file` path validation fails, run the command from the Markdown file's directory and use a relative path.
- If the URL was processed before, show the existing Feishu URL and local file, then only regenerate when the user asks.
