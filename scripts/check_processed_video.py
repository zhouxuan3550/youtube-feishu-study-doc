#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def video_id_from_url(url):
    parsed = urlparse(url)
    if parsed.netloc.endswith("youtu.be"):
        return parsed.path.strip("/")
    query_id = parse_qs(parsed.query).get("v")
    if query_id:
        return query_id[0]
    match = re.search(r"(?:/shorts/|/embed/)([A-Za-z0-9_-]{6,})", parsed.path)
    return match.group(1) if match else None


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


def registry_paths(workspace):
    return [
        Path(workspace) / ".youtube-to-feishu-note" / "processed_videos.json",
        Path(workspace) / ".youtube-feishu-study-doc" / "processed_videos.json",
        Path.home() / ".codex" / "skills" / "youtube-to-feishu-note" / "data" / "processed_videos.json",
        Path.home() / ".codex" / "skills" / "youtube-feishu-study-doc" / "data" / "processed_videos.json",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether a YouTube URL was already published to Feishu.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--metadata", default=None, help="Metadata JSON from get_youtube_metadata.py")
    parser.add_argument("--workspace", default=".", help="Workspace to check for local registry")
    args = parser.parse_args()

    metadata = load_json(args.metadata)
    candidates = {
        args.url,
        metadata.get("webpage_url"),
        metadata.get("url"),
        metadata.get("id"),
        video_id_from_url(args.url),
    }
    candidates = {item for item in candidates if item}

    matches = []
    for path in registry_paths(args.workspace):
        registry = load_json(path)
        for key, record in registry.items():
            values = {key, record.get("source_url"), record.get("video_id")}
            if candidates & {item for item in values if item}:
                match = dict(record)
                match["_registry"] = str(path)
                matches.append(match)

    print(json.dumps({"processed": bool(matches), "matches": matches}, ensure_ascii=False, indent=2))
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
