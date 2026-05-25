#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch timestamped transcript from Supadata.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--out", default="-", help="Output JSON path, or - for stdout")
    parser.add_argument("--mode", default="auto", help="Supadata transcript mode")
    parser.add_argument("--text", default="false", choices=["true", "false"], help="Return plain text instead of segments")
    parser.add_argument("--api-key", default=None, help="Supadata API key; defaults to SUPADATA_API_KEY or X_API_KEY")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("SUPADATA_API_KEY") or os.environ.get("X_API_KEY")
    if not api_key:
        print("Missing Supadata API key. Set SUPADATA_API_KEY or X_API_KEY.", file=sys.stderr)
        return 2

    query = urllib.parse.urlencode({
        "url": args.url,
        "text": args.text,
        "mode": args.mode,
    })
    request = urllib.request.Request(
        f"https://api.supadata.ai/v1/transcript?{query}",
        headers={
            "x-api-key": api_key,
            "user-agent": "Mozilla/5.0 youtube-to-feishu-note/1.0",
            "accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read().decode("utf-8")
    except Exception as exc:
        print(f"Supadata request failed: {exc}", file=sys.stderr)
        return 1

    try:
        parsed = json.loads(payload)
        payload = json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        pass

    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
        print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
