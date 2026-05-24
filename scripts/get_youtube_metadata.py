#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def safe_filename(value):
    value = re.sub(r"[\\/:*?\"<>|]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:120] or "youtube-video"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch YouTube metadata with yt-dlp.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--out", default="-", help="Output JSON path, or - for stdout")
    args = parser.parse_args()

    data = {}
    cmd = ["yt-dlp", "-J", "--skip-download", "--no-warnings", args.url]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
    else:
        sys.stderr.write(result.stderr)
        query = urllib.parse.urlencode({"url": args.url, "format": "json"})
        try:
            with urllib.request.urlopen(f"https://www.youtube.com/oembed?{query}", timeout=30) as response:
                fallback = json.loads(response.read().decode("utf-8"))
            data = {
                "id": None,
                "title": fallback.get("title"),
                "channel": fallback.get("author_name"),
                "uploader": fallback.get("author_name"),
                "webpage_url": args.url,
            }
        except Exception as exc:
            print(f"Metadata fallback failed: {exc}", file=sys.stderr)
            return result.returncode
    metadata = {
        "id": data.get("id"),
        "title": data.get("title"),
        "channel": data.get("channel") or data.get("uploader"),
        "uploader": data.get("uploader"),
        "duration": data.get("duration"),
        "duration_string": data.get("duration_string"),
        "upload_date": data.get("upload_date"),
        "timestamp": data.get("timestamp"),
        "webpage_url": data.get("webpage_url") or args.url,
        "description": data.get("description"),
        "language": data.get("language"),
        "suggested_filename_source": safe_filename(data.get("title") or data.get("id") or "youtube-video"),
    }
    payload = json.dumps(metadata, ensure_ascii=False, indent=2)

    if args.out == "-":
        print(payload)
    else:
        out_path = Path(args.out).expanduser().resolve()
        with open(out_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
        print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
