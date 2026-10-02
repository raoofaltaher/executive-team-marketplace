"""Keep the plugin version identical in every location .version-bump.json declares.

Usage:
  python scripts/bump_version.py <x.y.z>            write the version into every declared field
  python scripts/bump_version.py --check            print every declared location; fail on drift
  python scripts/bump_version.py --audit            --check, then fail if the version appears in an undeclared tracked file
  python scripts/bump_version.py ... --root <dir>   operate on another checkout (tests use this)

A declared entry may carry "suffix": the stored value is <version><suffix> and
comparisons strip it. The audit skips the paths under audit.exclude.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def load_config(root=ROOT):
    with open(os.path.join(root, ".version-bump.json"), encoding="utf-8") as fh:
        return json.load(fh)


def declared_locations(root=ROOT):
    return [(e["path"], e["field"], e.get("suffix", "")) for e in load_config(root)["files"]]


def _descend(data, parts):
    for p in parts:
        data = data[int(p)] if isinstance(data, list) else data[p]
    return data


def _load_json(root, path):
    with open(os.path.join(root, path), encoding="utf-8") as fh:
        return json.load(fh)


def _save_json(root, path, data):
    with open(os.path.join(root, path), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def read_versions(root=ROOT):
    rows = []
    for path, field, suffix in declared_locations(root):
        try:
            raw = str(_descend(_load_json(root, path), field.split(".")))
        except (KeyError, IndexError, TypeError):
            raise ValueError(f"{path}: field {field} is missing")
        if suffix and not raw.endswith(suffix):
            raise ValueError(f"{path}: field {field} should end with {suffix}, found {raw}")
        rows.append((path, field, raw, raw[: len(raw) - len(suffix)] if suffix else raw))
    return rows


def write_version(version, root=ROOT):
    written = set()
    for path, field, suffix in declared_locations(root):
        data = _load_json(root, path)
        parts = field.split(".")
        parent = _descend(data, parts[:-1])
        key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
        parent[key] = version + suffix
        _save_json(root, path, data)
        written.add(path)
    return sorted(written)


def check(root=ROOT):
    rows = read_versions(root)
    for path, field, raw, _ in rows:
        print(f"{path} {field} = {raw}")
    distinct = sorted({v for _, _, _, v in rows})
    if len(distinct) != 1:
        print(f"ERROR: version drift across declared locations: {distinct}")
        return None
    return distinct[0]


def audit(root=ROOT):
    version = check(root)
    if version is None:
        return None, []
    excluded = [e.rstrip("/") for e in load_config(root).get("audit", {}).get("exclude", [])]
    declared = {p for p, _, _ in declared_locations(root)}
    tracked = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout.splitlines()
    hits = []
    for f in tracked:
        if not f or f in declared or any(f == e or f.startswith(e + "/") for e in excluded):
            continue
        try:
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    if version in line:
                        hits.append(f"{f}:{n}: {line.strip()}")
        except (UnicodeDecodeError, OSError):
            continue
    for h in hits:
        print("ERROR: version string outside declared files:", h)
    return version, hits


def main(argv):
    root = ROOT
    if "--root" in argv:
        i = argv.index("--root")
        root = os.path.abspath(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if argv == ["--check"]:
        try:
            return 0 if check(root) else 1
        except ValueError as e:
            print("ERROR:", e)
            return 1
    if argv == ["--audit"]:
        try:
            version, hits = audit(root)
        except ValueError as e:
            print("ERROR:", e)
            return 1
        if version is None or hits:
            return 1
        print(f"All clear: {version}")
        return 0
    if len(argv) == 1 and VERSION_RE.match(argv[0]):
        for path in write_version(argv[0], root):
            print(f"updated {path}")
        print(f"next: git commit -am 'release: v{argv[0]}' && git tag v{argv[0]}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
