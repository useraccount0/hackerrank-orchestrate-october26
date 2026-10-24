"""Source-line traceability for the requirements baseline.

This tool is NOT part of the challenge solution. It only supports requirements
management (see requirements/README.md). It does three deterministic jobs that
should not be left to an AI:

  split   Cut each baseline input file into source units and write a CSV file
          that Doorstop's own import command turns into SRC items:
              doorstop import <csv> SRC
  update  After sources.yml was moved to a new baseline commit: rewrite the text of
          SRC items whose line changed in place, and list what needs a human
          decision (lines added, removed or moved in a file; labels to re-decide).
  check   Prove that the SRC items reproduce every line of every baseline file
          exactly once and verbatim, and that their classification is consistent.
  views   Write requirements/views/line_map.csv: one row per input line, with its
          SRC item and the CHR requirements that are linked to that item.

Splitting rule (the only rule, applied the same way every time):
  * a fenced code block (from a line starting with ``` to the next such line)
    is one unit;
  * every other non-blank line is one unit;
  * blank lines belong to no unit.
A unit's ID is SRC-<file code><number of its first line, 4 digits>,
for example SRC-PS0126 = problem_statement.md line 126.
"""

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCES_FILE = ROOT / "requirements" / "sources.yml"
SRC_DIR = ROOT / "requirements" / "src"
CHR_DIR = ROOT / "requirements" / "chr"
LINE_MAP = ROOT / "requirements" / "views" / "line_map.csv"

DISPOSITIONS = ("requirement", "heading", "formatting", "context", "not-applicable")
CLASSIFIED_BY = ("rule", "ai", "user")
PENDING_REVIEW = "pending-user-review"

FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^#{1,6}\s")
HORIZONTAL_RULE = re.compile(r"^\s*---\s*$")
TABLE_DELIMITER = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def load_sources():
    data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8"))
    return data["baseline_commit"], data["files"]


def read_baseline(commit, path):
    """Return the exact bytes of `path` as stored in git at `commit`."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, check=True
    )
    return result.stdout


def to_lines(content):
    """Split file bytes into lines, without the line-ending characters."""
    lines = content.decode("utf-8").split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def split_units(lines):
    """Return (first, last) line numbers (1-based) of every source unit."""
    units = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
        elif FENCE.match(lines[i]):
            end = i + 1
            while end < len(lines) and not FENCE.match(lines[end]):
                end += 1
            if end == len(lines):
                sys.exit(f"unclosed code fence starting at line {i + 1}")
            units.append((i + 1, end + 1))
            i = end + 1
        else:
            units.append((i + 1, i + 1))
            i += 1
    return units


def structural_rule(lines, first, last):
    """Classify a unit by a fixed structural rule. None means: needs judgment."""
    if first != last:
        return None
    line = lines[first - 1]
    if HEADING.match(line):
        return "heading", "rule: Markdown heading"
    if HORIZONTAL_RULE.match(line):
        return "formatting", "rule: horizontal rule"
    if TABLE_DELIMITER.match(line):
        return "formatting", "rule: table delimiter row"
    if line.lstrip().startswith("|") and first < len(lines) and TABLE_DELIMITER.match(lines[first]):
        return "formatting", "rule: table header row"
    return None


def unit_id(code, first):
    return f"SRC-{code}{first:04d}"


def unit_header(path, first, last):
    return f"{path}:{first}" if first == last else f"{path}:{first}-{last}"


def load_items(directory):
    """Read all item files of one Doorstop document as {uid: data}."""
    items = {}
    for path in sorted(directory.glob("*.yml")):
        if not path.name.startswith("."):
            items[path.stem] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return items


def item_text(item):
    return (item.get("text") or "").rstrip("\n")


def cmd_split(args):
    commit, files = load_sources()
    columns = ["uid", "level", "header", "text", "normative", "reviewed", "file",
               "line_start", "line_end", "disposition", "classified_by", "note"]
    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for source in files:
            lines = to_lines(read_baseline(commit, source["path"]))
            for number, (first, last) in enumerate(split_units(lines), start=1):
                rule = structural_rule(lines, first, last)
                # Units without a rule result must be classified by judgment before import.
                disposition, classified_by, note = (
                    (rule[0], "rule", rule[1]) if rule else ("unclassified", "", "")
                )
                writer.writerow({
                    "uid": unit_id(source["code"], first),
                    "level": f"{source['level']}.{number}",
                    "header": unit_header(source["path"], first, last),
                    "text": "\n".join(lines[first - 1:last]),
                    "normative": disposition in ("requirement", "unclassified"),
                    "reviewed": "" if rule else PENDING_REVIEW,
                    "file": source["path"],
                    "line_start": first,
                    "line_end": last,
                    "disposition": disposition,
                    "classified_by": classified_by,
                    "note": note,
                })
    print(f"wrote {args.out}")


def check_item(uid, item, source, lines, first, last, number):
    problems = []
    path = source["path"]
    if item.get("file") != path:
        problems.append(f"{uid}: file is {item.get('file')!r}, expected {path!r}")
    if (str(item.get("line_start")), str(item.get("line_end"))) != (str(first), str(last)):
        problems.append(f"{uid}: lines are {item.get('line_start')}-{item.get('line_end')}, "
                        f"expected {first}-{last}")
    if str(item.get("level")) != f"{source['level']}.{number}":
        problems.append(f"{uid}: level is {item.get('level')}, expected {source['level']}.{number}")
    if str(item.get("header") or "").strip() != unit_header(path, first, last):
        problems.append(f"{uid}: header is not {unit_header(path, first, last)!r}")
    if item_text(item) != "\n".join(lines[first - 1:last]):
        problems.append(f"{uid}: text is not identical to {unit_header(path, first, last)}")

    disposition = item.get("disposition")
    classified_by = item.get("classified_by")
    if disposition not in DISPOSITIONS:
        problems.append(f"{uid}: disposition {disposition!r} is not one of {', '.join(DISPOSITIONS)}")
    if classified_by not in CLASSIFIED_BY:
        problems.append(f"{uid}: classified_by {classified_by!r} is not one of {', '.join(CLASSIFIED_BY)}")
    rule = structural_rule(lines, first, last)
    if classified_by == "rule" and (rule is None or rule[0] != disposition):
        problems.append(f"{uid}: classified_by is 'rule', but the rule gives "
                        f"{rule[0] if rule else 'no result'}")
    if bool(item.get("normative")) != (disposition == "requirement"):
        problems.append(f"{uid}: normative must be true exactly when disposition is 'requirement'")
    if disposition != "requirement" and not item.get("note"):
        problems.append(f"{uid}: a unit that is not a requirement needs a note saying why")
    return problems


def cmd_check(args):
    commit, files = load_sources()
    items = load_items(SRC_DIR)
    problems = []
    expected = set()
    totals = Counter()
    print(f"Baseline commit {commit}")
    for source in files:
        path, code = source["path"], source["code"]
        content = read_baseline(commit, path)
        sha256 = hashlib.sha256(content).hexdigest()
        if sha256 != source["sha256"]:
            problems.append(f"{path}: SHA-256 in git is {sha256}, sources.yml says {source['sha256']}")
        lines = to_lines(content)
        if len(lines) != source["lines"]:
            problems.append(f"{path}: has {len(lines)} lines, sources.yml says {source['lines']}")

        rebuilt = [""] * len(lines)  # the file, rebuilt only from SRC item texts
        counts = Counter()
        units = split_units(lines)
        for number, (first, last) in enumerate(units, start=1):
            uid = unit_id(code, first)
            expected.add(uid)
            item = items.get(uid)
            if item is None:
                problems.append(f"{uid}: no SRC item for {unit_header(path, first, last)}")
                continue
            problems += check_item(uid, item, source, lines, first, last, number)
            for offset, text in enumerate(item_text(item).split("\n")[: last - first + 1]):
                rebuilt[first - 1 + offset] = text
            counts[item.get("disposition")] += 1

        ending = "\n" if content.endswith(b"\n") else ""
        identical = ("\n".join(rebuilt) + ending).encode("utf-8") == content
        if not identical:
            problems.append(f"{path}: rebuilding it from its SRC items does not give the original bytes")
        blank = sum(1 for line in lines if not line.strip())
        print(f"\n{path}: {len(lines)} lines ({len(lines) - blank} non-blank, {blank} blank) "
              f"-> {len(units)} units")
        print("  " + ", ".join(f"{name} {counts[name]}" for name in DISPOSITIONS))
        print(f"  rebuilt from SRC items: {'identical to the baseline file' if identical else 'DIFFERENT'}")
        totals.update(counts)
        totals["lines"] += len(lines)
        totals["blank"] += blank
        totals["units"] += len(units)

        working = ROOT / path
        if not working.exists():
            print("  working tree: file is missing")
        elif working.read_bytes().replace(b"\r\n", b"\n") != content:
            print("  working tree: CHANGED since the baseline (the baseline is still read from git)")
        else:
            print("  working tree: unchanged since the baseline")

    for uid in sorted(set(items) - expected):
        problems.append(f"{uid}: SRC item does not match any unit of the baseline files")

    print(f"\nTOTAL: {totals['lines']} lines, {totals['blank']} blank, {totals['units']} units: "
          + ", ".join(f"{name} {totals[name]}" for name in DISPOSITIONS))
    by_classifier = Counter(item.get("classified_by") for item in items.values())
    pending = sum(1 for item in items.values() if item.get("reviewed") == PENDING_REVIEW)
    print("classified by: " + ", ".join(f"{name} {by_classifier[name]}" for name in CLASSIFIED_BY)
          + f" | SRC items waiting for your review: {pending}")
    if problems:
        print(f"\nRESULT: FAIL ({len(problems)} problems)")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    print("\nRESULT: PASS - every line of every baseline file is covered by exactly one SRC item "
          "(or is blank), verbatim")


def cmd_update(args):
    import doorstop  # only this command writes items, through Doorstop's own API

    doorstop.settings.ADDREMOVE_FILES = False  # save item files without running `git add`
    commit, files = load_sources()
    items_by_file = defaultdict(dict)
    for item in doorstop.build(cwd=str(ROOT)).find_document("SRC"):
        items_by_file[item.get("file")][str(item.uid)] = item
    needs_decision = []
    for source in files:
        path = source["path"]
        lines = to_lines(read_baseline(commit, path))
        units = {unit_id(source["code"], first): (first, last) for first, last in split_units(lines)}
        items = items_by_file.pop(path, {})
        # Unit IDs contain line numbers. If lines were added or removed, IDs shift and old texts
        # would land on the wrong units, so only files with an unchanged line structure are updated.
        if set(units) != set(items) or any(
                str(items[uid].get("line_end")) != str(last) for uid, (_, last) in units.items()):
            needs_decision.append(f"{path}: lines were added, removed or moved, so unit IDs shift; "
                                  "units and links must be re-mapped by a person (file left unchanged)")
            continue
        for uid, (first, last) in units.items():
            item = items[uid]
            text = "\n".join(lines[first - 1:last])
            if item.text == text:
                continue
            item.text = text
            print(f"updated {uid}: text")
            rule = structural_rule(lines, first, last)
            by_rule = item.get("classified_by") == "rule"
            if (by_rule and (rule is None or rule[0] != item.get("disposition"))) or (not by_rule and rule):
                needs_decision.append(f"{uid}: text changed, and its disposition needs a new decision")
    for path in items_by_file:
        needs_decision.append(f"{path}: has SRC items but is not in sources.yml")
    if needs_decision:
        print("\nNeeds a human decision (this tool does not create, delete, move or re-classify items):")
        for line in needs_decision:
            print(f"  - {line}")
        sys.exit(1)
    print("\nSRC items match the baseline. Next: `check`, then `doorstop -F -W`, where every "
          "requirement linked to an updated unit is reported as a 'suspect link'.")


def cmd_views(args):
    commit, files = load_sources()
    src_items = load_items(SRC_DIR)
    linked_from = defaultdict(list)
    for chr_id, item in load_items(CHR_DIR).items():
        for link in item.get("links") or []:
            parent = next(iter(link)) if isinstance(link, dict) else str(link)
            linked_from[parent].append(chr_id)

    LINE_MAP.parent.mkdir(parents=True, exist_ok=True)
    with open(LINE_MAP, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "line", "src_uid", "disposition", "chr_uids", "text"])
        for source in files:
            lines = to_lines(read_baseline(commit, source["path"]))
            owner = {}
            for first, last in split_units(lines):
                for number in range(first, last + 1):
                    owner[number] = unit_id(source["code"], first)
            for number, text in enumerate(lines, start=1):
                uid = owner.get(number, "")
                disposition = src_items.get(uid, {}).get("disposition", "") if uid else "blank"
                chr_ids = " ".join(sorted(linked_from.get(uid, [])))
                writer.writerow([source["path"], number, uid, disposition, chr_ids, text])
    print(f"wrote {LINE_MAP.relative_to(ROOT).as_posix()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    split = commands.add_parser("split", help="write the Doorstop import CSV for the SRC document")
    split.add_argument("out", help="path of the CSV file to write")
    commands.add_parser("update", help="refresh the SRC items from a new baseline commit")
    commands.add_parser("check", help="verify the SRC items against the baseline files")
    commands.add_parser("views", help="write requirements/views/line_map.csv")
    args = parser.parse_args()
    {"split": cmd_split, "update": cmd_update, "check": cmd_check, "views": cmd_views}[args.command](args)


if __name__ == "__main__":
    main()
