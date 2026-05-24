#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


GENERIC_SUFFIXES = ("高保真学习文档", "学习文档", "视频整理")


def load_text(path):
    with open(Path(path).expanduser().resolve(), "r", encoding="utf-8") as handle:
        return handle.read()


def load_json(path):
    if not path:
        return {}
    json_path = Path(path).expanduser().resolve()
    if not json_path.exists() or json_path.stat().st_size == 0:
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


def timestamp_ranges(text):
    pattern = re.compile(r"^#{2,4}\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*[-—–]\s*(\d{1,2}:\d{2}(?::\d{2})?)", re.M)
    return pattern.findall(text)


def seconds(value):
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a YouTube Feishu study document before publishing.")
    parser.add_argument("markdown_file", help="Markdown file")
    parser.add_argument("--source-url", default=None, help="Expected source URL")
    parser.add_argument("--metadata", default=None, help="Metadata JSON from get_youtube_metadata.py")
    parser.add_argument("--warn-only", action="store_true", help="Return 0 even with validation errors")
    args = parser.parse_args()

    text = load_text(args.markdown_file)
    metadata = load_json(args.metadata)
    errors = []
    warnings = []

    first_heading = re.search(r"^#\s+(.+)$", text, re.M)
    title = first_heading.group(1).strip() if first_heading else ""
    if not title:
        errors.append("Missing Markdown H1 title.")
    if any(title.endswith(suffix) or suffix in title for suffix in GENERIC_SUFFIXES):
        errors.append("Title contains a generic suffix; use the translated original video title only.")

    if args.source_url and args.source_url not in text:
        errors.append("Source URL is missing or does not match.")
    if "原视频标题：" not in text:
        errors.append("Missing original video title field.")
    if "说明：" not in text:
        errors.append("Missing processing/copyright note.")
    if "完整字幕/关键原文内容" not in text:
        errors.append("Missing `完整字幕/关键原文内容` subsections.")
    if "三、配置与工作流代码块" not in text:
        errors.append("Missing section `三、配置与工作流代码块`.")
    if "关键底层数据索引" not in text:
        warnings.append("Missing `关键底层数据索引`; add it when the video contains tools, workflows, or examples.")

    ranges = timestamp_ranges(text)
    if len(ranges) < 2:
        errors.append("Too few timestamp sections; coverage is likely incomplete.")
    elif metadata.get("duration"):
        covered_until = max(seconds(end) for _, end in ranges)
        duration = int(metadata["duration"])
        if covered_until < duration * 0.85:
            warnings.append(f"Timestamp coverage ends at {covered_until}s, below 85% of video duration {duration}s.")

    if "```" not in text:
        warnings.append("No Markdown code blocks found; verify the video has no reusable prompts, commands, or configs.")

    minute_count = max(1, int(metadata.get("duration") or 0) // 60)
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if minute_count >= 10 and chinese_chars / minute_count < 120:
        warnings.append("Document is short relative to video duration; check for over-compression.")

    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "timestamp_sections": len(ranges),
        "title": title,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
