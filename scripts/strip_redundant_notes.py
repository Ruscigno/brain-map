#!/usr/bin/env python3
"""Remove the `note` field from any node whose only child is a Detail node
(title starts with '**Definition:**'). Those nodes are former leaves whose
original note is now duplicated by the detail child's Definition + Trade-offs.

Internal nodes (parents with multiple real children) keep their notes — they
still provide useful section-level context.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "public" / "mindmap.json"


def is_detail_only(node: dict) -> bool:
    children = node.get("children")
    if not children or len(children) != 1:
        return False
    title = children[0].get("title", "")
    return isinstance(title, str) and title.startswith("**Definition:**")


def walk(node: dict, removed: list[str]) -> None:
    if is_detail_only(node) and "note" in node:
        removed.append(node["title"])
        del node["note"]
    for c in node.get("children", []):
        walk(c, removed)


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    removed: list[str] = []
    walk(data, removed)
    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Removed redundant note from {len(removed)} nodes:")
    for t in removed:
        print(f"  - {t}")


if __name__ == "__main__":
    main()
