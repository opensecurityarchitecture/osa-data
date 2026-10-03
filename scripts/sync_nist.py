#!/usr/bin/env python3
"""
Keep what NIST says about a control the same everywhere it is written down.

data/nist/sp800-53-rev5.json is the one source for those facts (see
build_nist_extract.py). They are also written in three other places, because
the website and the people who read these files expect them there:

  - each control file in data/controls/, at the top level and under
    nist_800_53.rev5;
  - data/controls/_manifest.json, the index the website's controls list reads;
  - the control names inside each pattern file.

This script writes the managed facts from the extract into those places.
With --check it writes nothing, lists every difference and exits 1 if there
is one. validate_json.py runs the check, so a copy cannot drift unnoticed.

OSA's own fields are never touched: compliance_mappings, function,
attack_techniques, metadata, and everything in a pattern but a control's name.

MANAGED lists what is in step with NIST so far. A fact is added to it in the
same change that brings the files into line.

Usage:
    python3 scripts/sync_nist.py            # write
    python3 scripts/sync_nist.py --check    # report only
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
EXTRACT = DATA / "nist" / "sp800-53-rev5.json"

MANAGED = ("baselines", "withdrawn", "name")
LEVELS = ("low", "moderate", "high")
MANIFEST_COPIES = ("id", "name", "family", "family_name", "baseline_low", "baseline_moderate", "baseline_high")


def base_ids(targets):
    """A withdrawn control's successors, as controls. The files carry base
    controls only, so an enhancement stands for its control and a family code
    is left out."""
    return sorted({t.split("(")[0] for t in targets if "-" in t})


def wanted(control, nist):
    """The managed facts for one control file, as (path, value) pairs."""
    out = []
    rev5 = ("nist_800_53", "rev5")
    if "name" in MANAGED:
        out.append((("name",), nist["name"]))
        out.append((rev5 + ("name",), nist["name"]))
    if "baselines" in MANAGED:
        for level in LEVELS:
            value = level in nist.get("baselines", [])
            out.append(((f"baseline_{level}",), value))
            out.append((rev5 + (f"baseline_{level}",), value))
        out.append((rev5 + ("baseline_privacy",), "privacy" in nist.get("baselines", [])))
    if "withdrawn" in MANAGED:
        out.append((("nist_800_53", "rev4", "withdrawn"), bool(nist.get("withdrawn"))))
        if nist.get("withdrawn"):
            out.append((("nist_800_53", "rev4", "incorporated_into"), base_ids(nist.get("incorporated_into", []))))
    return out


def get(data, path):
    for key in path:
        if not isinstance(data, dict) or key not in data:
            return None
        data = data[key]
    return data


def put(data, path, value):
    for key in path[:-1]:
        data = data.setdefault(key, {})
    data[path[-1]] = value


def same(current, value):
    """An empty flag counts as false, so a file is not rewritten to say so."""
    if isinstance(value, bool):
        return bool(current) == value
    return current == value


def dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


# A control as a pattern lists it: an object with an id, a name and an emphasis.
PATTERN_CONTROL = re.compile(r'\{[^{}]*?"id":\s*"([A-Z]{2}-\d{2})"[^{}]*?\}')
PATTERN_NAME = re.compile(r'("name":\s*)"((?:[^"\\]|\\.)*)"')


def sync_pattern(path, names, write, differences):
    """Give each control a pattern lists the name the catalogue gives it. The
    file is edited as text, so nothing else in it moves."""
    raw = path.read_text(encoding="utf-8")
    found = []

    def fix(match):
        cid, entry = match.group(1), match.group(0)
        name = PATTERN_NAME.search(entry)
        if cid not in names or '"emphasis"' not in entry or not name:
            return entry
        current = json.loads('"%s"' % name.group(2))
        if current == names[cid]:
            return entry
        found.append(f"{path.name}: {cid} is named {current!r}, the catalogue has {names[cid]!r}")
        return entry[:name.start()] + name.group(1) + json.dumps(names[cid], ensure_ascii=False) + entry[name.end():]

    new = PATTERN_CONTROL.sub(fix, raw)
    if not found:
        return
    # Nothing but those names may have changed.
    before, after = json.loads(raw), json.loads(new)
    for control in before.get("controls", []):
        if control.get("id") in names:
            control["name"] = names[control["id"]]
    assert before == after, f"{path.name}: more than the control names would change"
    differences.extend(found)
    if write:
        path.write_text(new, encoding="utf-8")


def sync(write):
    """Return the differences found. With write, also correct them."""
    nist = json.loads(EXTRACT.read_text(encoding="utf-8"))["controls"]
    controls_dir = DATA / "controls"
    manifest_path = controls_dir / "_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    differences = []

    for entry in manifest["controls"]:
        path = controls_dir / entry["file"]
        control = json.loads(path.read_text(encoding="utf-8"))
        cid = control["id"]
        if cid not in nist:
            differences.append(f"{entry['file']}: {cid} is not a control in NIST's release")
            continue
        changed = False
        for field, value in wanted(control, nist[cid]):
            if not same(get(control, field), value):
                differences.append(f"{entry['file']}: {'.'.join(field)} is {get(control, field)!r}, NIST has {value!r}")
                put(control, field, value)
                changed = True
        if changed and write:
            path.write_text(dump(control), encoding="utf-8")
        copies = {key: control.get(key) for key in MANIFEST_COPIES}
        stale = [key for key in MANIFEST_COPIES if entry.get(key) != copies[key]]
        if stale:
            differences.append(f"_manifest.json: {cid} differs from {entry['file']} in {', '.join(stale)}")
            entry.update(copies)
    if write and any(d.startswith("_manifest.json") for d in differences):
        manifest_path.write_text(dump(manifest), encoding="utf-8")

    if "name" in MANAGED:
        names = {cid: entry["name"] for cid, entry in nist.items()}
        for path in sorted((DATA / "patterns").glob("SP-*.json")):
            sync_pattern(path, names, write, differences)
    return differences


def main():
    write = "--check" not in sys.argv
    differences = sync(write)
    for line in differences:
        print(("corrected: " if write else "differs: ") + line)
    print(f"{len(differences)} difference(s) {'corrected' if write else 'found'}; in step with NIST: {', '.join(MANAGED)}")
    return 1 if differences and not write else 0


if __name__ == "__main__":
    sys.exit(main())
