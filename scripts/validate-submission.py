#!/usr/bin/env python3
"""Validate a student submission file. Exits 0 on success, 1 on any error.

Usage:
    python3 scripts/validate-submission.py students/<pinyin>-<XYZ>.md
"""
import sys
import re
import yaml
from pathlib import Path

REQUIRED_TOP = ['name', 'pinyin', 'student_id_suffix']
REQUIRED_SUB = ['github_repo', 'website', 'writeup', 'description']
URL_FIELDS = ['github_repo', 'website', 'writeup']


def main(path_str: str) -> int:
    path = Path(path_str)
    if not path.exists():
        print(f"::error file={path}::file does not exist")
        return 1

    content = path.read_text(encoding='utf-8')
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"::error file={path}::missing YAML frontmatter (need leading and trailing ---)")
        return 1

    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"::error file={path}::YAML parse error: {e}")
        return 1

    if not isinstance(data, dict):
        print(f"::error file={path}::frontmatter is not a mapping")
        return 1

    errors = []

    for f in REQUIRED_TOP:
        if not data.get(f) or not isinstance(data[f], str):
            errors.append(f"missing or non-string {f}")

    pinyin = data.get('pinyin')
    suffix = data.get('student_id_suffix')
    if pinyin and suffix:
        expected = f"{pinyin}-{suffix}.md"
        if path.name != expected:
            errors.append(f"filename {path.name} does not match expected {expected}")

    submissions = data.get('submissions') or {}
    if not isinstance(submissions, dict):
        errors.append("submissions must be a mapping")
    else:
        for key, sub in submissions.items():
            if not re.match(r'^assignment-[1-4]$', key):
                errors.append(f"invalid assignment key: {key}")
                continue
            if not isinstance(sub, dict):
                errors.append(f"{key}: must be a mapping")
                continue
            for f in REQUIRED_SUB:
                if not sub.get(f):
                    errors.append(f"{key}: missing {f}")
            for f in URL_FIELDS:
                v = sub.get(f)
                if v and not re.match(r'^https?://', v):
                    errors.append(f"{key}.{f}: not an http(s) URL")
            screenshot = sub.get('screenshot')
            if screenshot and not re.match(r'^https?://', screenshot):
                errors.append(f"{key}.screenshot: not an http(s) URL")
            desc = sub.get('description')
            if desc and len(list(desc)) > 80:
                errors.append(f"{key}.description: too long (>80 chars)")

    if errors:
        for e in errors:
            print(f"::error file={path}::{e}")
        return 1

    print(f"::notice file={path}::OK ({len(submissions)} submission(s))")
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: validate-submission.py <path-to-md>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
