"""Set the same version in the plugin manifest and the marketplace catalog entry.

Usage: python scripts/bump_version.py <x.y.z>
Run from the repository root. Updates:
  plugins/executive-team/.claude-plugin/plugin.json  -> version
  .claude-plugin/marketplace.json                    -> plugins[name=executive-team].version
                                                        plugins[name=executive-team-dev].version = <x.y.z>-dev
                                                        metadata.version
Prints the files it changed. Commit, then tag executive-team--v<x.y.z>.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = "executive-team"
FILES = {
    "plugin": os.path.join(ROOT, "plugins", PLUGIN, ".claude-plugin", "plugin.json"),
    "catalog": os.path.join(ROOT, ".claude-plugin", "marketplace.json"),
}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", argv[0]):
        print(__doc__)
        return 2
    version = argv[0]
    plugin = load(FILES["plugin"])
    plugin["version"] = version
    save(FILES["plugin"], plugin)
    catalog = load(FILES["catalog"])
    catalog.setdefault("metadata", {})["version"] = version
    seen = set()
    for entry in catalog["plugins"]:
        if entry["name"] == PLUGIN:
            entry["version"] = version
            seen.add(entry["name"])
        elif entry["name"] == PLUGIN + "-dev":
            entry["version"] = version + "-dev"
            seen.add(entry["name"])
    if PLUGIN not in seen:
        print(f"ERROR: no '{PLUGIN}' entry in marketplace.json")
        return 1
    save(FILES["catalog"], catalog)
    for label, path in FILES.items():
        print(f"updated {label}: {os.path.relpath(path, ROOT)}")
    print(f"next: git commit -am 'release: v{version}' && git tag {PLUGIN}--v{version}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
