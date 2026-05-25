#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def load_json(path):
    if not path:
        return {}
    json_path = Path(path).expanduser().resolve()
    if not json_path.exists():
        return {}
    with open(json_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def update_registry(workspace, record):
    paths = [
        Path(workspace) / ".youtube-to-feishu-note" / "processed_videos.json",
        Path.home() / ".codex" / "skills" / "youtube-to-feishu-note" / "data" / "processed_videos.json",
    ]
    for registry_path in paths:
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        if registry_path.exists():
            try:
                with open(registry_path, "r", encoding="utf-8") as handle:
                    registry = json.load(handle)
            except json.JSONDecodeError:
                registry = {}
        else:
            registry = {}
        key = record.get("video_id") or record.get("source_url") or record.get("document_id")
        registry[key] = record
        with open(registry_path, "w", encoding="utf-8") as handle:
            json.dump(registry, handle, ensure_ascii=False, indent=2)
            handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a Markdown file to Feishu/Lark docs with lark-cli.")
    parser.add_argument("markdown_file", help="Local Markdown file")
    parser.add_argument("--title", default=None, help="Document title")
    parser.add_argument("--source-url", default=None, help="Source video URL for duplicate tracking")
    parser.add_argument("--metadata", default=None, help="Metadata JSON from get_youtube_metadata.py")
    parser.add_argument("--parent-position", default="my_library", help="Feishu parent position")
    parser.add_argument("--as-identity", default="user", choices=["user", "bot"], help="lark-cli identity")
    parser.add_argument("--no-verify", action="store_true", help="Skip outline verification")
    args = parser.parse_args()

    md_path = Path(args.markdown_file).expanduser().resolve()
    if not md_path.exists():
        print(f"Markdown file not found: {md_path}", file=sys.stderr)
        return 2

    metadata = load_json(args.metadata)
    title = args.title or md_path.stem
    cmd = [
        "lark-cli", "docs", "+create",
        "--api-version", "v2",
        "--as", args.as_identity,
        "--parent-position", args.parent_position,
        "--title", title,
        "--doc-format", "markdown",
        "--content", f"@./{md_path.name}",
    ]

    result = run(cmd, cwd=str(md_path.parent))
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.stderr.write(result.stdout)
        return result.returncode

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(result.stdout)
        return 0

    document = data.get("data", {}).get("document", {})
    doc_id = document.get("document_id")
    url = document.get("url")

    if not doc_id or not url:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 1

    if not args.no_verify:
        verify = run([
            "lark-cli", "docs", "+fetch",
            "--api-version", "v2",
            "--as", args.as_identity,
            "--doc", doc_id,
            "--format", "pretty",
            "--scope", "outline",
        ], cwd=os.getcwd())
        if verify.returncode != 0:
            print(f"Created but verification failed: {url}", file=sys.stderr)
            sys.stderr.write(verify.stderr)
        else:
            print(verify.stdout[:2000], file=sys.stderr)

    print(json.dumps({
        "ok": True,
        "title": title,
        "document_id": doc_id,
        "url": url,
        "local_file": str(md_path),
    }, ensure_ascii=False, indent=2))

    if args.source_url or metadata:
        record = {
            "source_url": args.source_url or metadata.get("webpage_url") or metadata.get("url"),
            "video_id": metadata.get("id"),
            "original_title": metadata.get("title"),
            "translated_title": title,
            "channel": metadata.get("channel") or metadata.get("uploader"),
            "duration": metadata.get("duration"),
            "upload_date": metadata.get("upload_date"),
            "document_id": doc_id,
            "url": url,
            "local_file": str(md_path),
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
        update_registry(md_path.parent, record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
