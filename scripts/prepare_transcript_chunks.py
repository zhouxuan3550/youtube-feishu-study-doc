#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


def read_json(path):
    with open(Path(path).expanduser().resolve(), "r", encoding="utf-8") as handle:
        return json.load(handle)


def pick_segments(payload):
    if isinstance(payload, list):
        return payload
    for key in ("content", "segments", "transcript", "captions", "subtitles"):
        value = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(value, list):
            return value
    return []


def segment_text(segment):
    for key in ("text", "content", "sentence", "caption"):
        value = segment.get(key)
        if isinstance(value, str):
            return value.strip()
    return ""


def segment_start_ms(segment):
    for key in ("start", "startMs", "offset", "offsetMs"):
        value = segment.get(key)
        if isinstance(value, (int, float)):
            return int(value if value > 1000 else value * 1000)
    return 0


def segment_end_ms(segment):
    for key in ("end", "endMs"):
        value = segment.get(key)
        if isinstance(value, (int, float)):
            return int(value if value > 1000 else value * 1000)
    start = segment_start_ms(segment)
    for key in ("duration", "durationMs"):
        value = segment.get(key)
        if isinstance(value, (int, float)):
            return start + int(value if value > 1000 else value * 1000)
    return start


def fmt(ms):
    seconds = max(0, int(round(ms / 1000)))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def chunk_segments(segments, max_minutes):
    max_ms = max_minutes * 60 * 1000
    chunks = []
    current = []
    chunk_start = None
    for segment in segments:
        text = segment_text(segment)
        if not text:
            continue
        start = segment_start_ms(segment)
        if chunk_start is None:
            chunk_start = start
        if current and start - chunk_start >= max_ms:
            chunks.append(current)
            current = []
            chunk_start = start
        current.append(segment)
    if current:
        chunks.append(current)
    return chunks


def render_markdown(chunks, metadata):
    lines = []
    title = metadata.get("title") or "Untitled YouTube Video"
    lines.append(f"# Transcript Chunks: {title}")
    if metadata:
        lines.append("")
        lines.append(f"- Source: {metadata.get('webpage_url', '')}")
        lines.append(f"- Channel: {metadata.get('channel') or metadata.get('uploader') or ''}")
        duration = metadata.get("duration")
        if duration:
            lines.append(f"- Duration: {fmt(int(duration) * 1000)}")
    lines.append("")
    for index, chunk in enumerate(chunks, 1):
        start = segment_start_ms(chunk[0])
        end = max(segment_end_ms(item) for item in chunk)
        text = " ".join(segment_text(item) for item in chunk)
        lines.append(f"## Chunk {index}: {fmt(start)}-{fmt(end)}")
        lines.append("")
        lines.append("整理提示：请把本段转成高保真中文转写，保留操作步骤、工具名、示例、Prompt、判断标准，不逐字复刻整段字幕。")
        lines.append("")
        lines.append("字幕素材：")
        lines.append("")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_json(chunks):
    result = []
    for index, chunk in enumerate(chunks, 1):
        start = segment_start_ms(chunk[0])
        end = max(segment_end_ms(item) for item in chunk)
        result.append({
            "index": index,
            "start_ms": start,
            "end_ms": end,
            "start": fmt(start),
            "end": fmt(end),
            "text": " ".join(segment_text(item) for item in chunk),
        })
    return json.dumps(result, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Group Supadata transcript segments into reviewable chunks.")
    parser.add_argument("transcript_json", help="Transcript JSON path")
    parser.add_argument("--metadata", default=None, help="Metadata JSON path")
    parser.add_argument("--max-minutes", type=int, default=6, help="Maximum minutes per chunk")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--out", default="-", help="Output path, or - for stdout")
    args = parser.parse_args()

    payload = read_json(args.transcript_json)
    metadata = read_json(args.metadata) if args.metadata else {}
    segments = pick_segments(payload)
    chunks = chunk_segments(segments, args.max_minutes)
    output = render_markdown(chunks, metadata) if args.format == "markdown" else render_json(chunks)

    if args.out == "-":
        print(output, end="")
    else:
        out_path = Path(args.out).expanduser().resolve()
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(output)
        print(out_path)
    return 0 if chunks else 1


if __name__ == "__main__":
    raise SystemExit(main())
