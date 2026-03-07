"""
parsers/sprint.py — Sprint progress parser for Monitor v2 P4 (sprint panel).

Parses active_context.md "❗ 진행 중" section to extract the CURRENT sprint only
(first top-level bullet and its sub-items).
"""

import re
from pathlib import Path

from parsers import get_vault_root

VAULT_ROOT = get_vault_root()
ACTIVE_CONTEXT = VAULT_ROOT / "00_System" / "Prompts" / "Ontology" / "active_context.md"


def parse_sprint() -> dict:
    """Return sprint progress data from active_context.md.

    Only parses the first top-level bullet under "❗ 진행 중" as the current sprint.
    Subsequent top-level bullets are ignored (backlog).
    """
    try:
        text = ACTIVE_CONTEXT.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return {"sprint": _empty()}

    # Find the "❗ 진행 중" section
    sections = re.split(r'^## ', text, flags=re.MULTILINE)
    progress_section = ""
    for sec in sections:
        if sec.startswith("❗") or "진행 중" in sec.split("\n")[0]:
            progress_section = sec
            break

    if not progress_section:
        return {"sprint": _empty()}

    lines = progress_section.strip().splitlines()

    # Find the first top-level bullet (= current sprint header)
    sprint_name = "Current Sprint"
    sprint_start = -1
    for i, line in enumerate(lines):
        m = re.match(r'^- \*\*(.+?)\*\*', line)
        if m:
            sprint_name = m.group(1).strip()
            sprint_start = i
            break

    if sprint_start < 0:
        return {"sprint": _empty()}

    # Collect sub-items until the next top-level bullet
    sub_items = []
    for i in range(sprint_start + 1, len(lines)):
        line = lines[i]
        # Next top-level bullet = end of current sprint scope
        if re.match(r'^- \*\*', line):
            break
        stripped = line.strip()
        if stripped and re.match(r'^-\s+', stripped):
            sub_items.append(stripped)

    # Count items by status
    done = 0
    in_progress = 0
    pending = 0
    recent_done = []

    for item in sub_items:
        if "✅" in item:
            done += 1
            label = _extract_label(item, remove="✅")
            if label:
                recent_done.append(label)
        elif "📌" in item or "🔄" in item:
            in_progress += 1
        elif "🔒" in item:
            pending += 1
        elif re.match(r'^\s*-\s*~~', item):
            done += 1
        else:
            # Unmarked sub-items under a sprint = completed progress notes
            done += 1
            label = _extract_label(item)
            if label:
                recent_done.append(label)

    total = done + in_progress + pending
    progress_pct = round(done / total * 100) if total > 0 else 0

    return {
        "sprint": {
            "name": sprint_name,
            "done": done,
            "in_progress": in_progress,
            "pending": pending,
            "progress_pct": progress_pct,
            "recent_done": recent_done[:5],
        }
    }


def _extract_label(item: str, remove: str | None = None) -> str:
    """Extract a clean label from a bullet item."""
    label = re.sub(r'^\s*-\s*', '', item)
    if remove:
        label = label.replace(remove, '')
    label = re.sub(r'\*\*(.+?)\*\*', r'\1', label)
    label = re.sub(r'\s*—.*$', '', label)
    label = re.sub(r'~~(.+?)~~', r'\1', label)
    label = re.sub(r'`([^`]+)`', r'\1', label)
    return label.strip()


def _empty() -> dict:
    return {
        "name": "No Sprint",
        "done": 0,
        "in_progress": 0,
        "pending": 0,
        "progress_pct": 0,
        "recent_done": [],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(parse_sprint(), indent=2, ensure_ascii=False))
