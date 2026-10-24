"""Source-line traceability for the requirements baseline.

This tool is NOT part of the challenge solution. It only supports requirements
management (see requirements/README.md). It does four deterministic jobs that
should not be left to an AI:

  split   Cut each baseline input file into source units and write a CSV file
          that Doorstop's own import command turns into SRC items:
              doorstop import <csv> SRC
          With --new-only, only the units that have no SRC item yet are written.
  update  After sources.yml was moved to a new baseline commit: rewrite the text of
          SRC items whose line changed in place, and list what needs a human
          decision (lines added, removed or moved in a file; labels to re-decide;
          new units to import).
  check   Prove that the SRC items reproduce every line of every baseline file
          exactly once and verbatim, and that their classification is consistent.
  views   Write requirements/views/line_map.csv: one row per input line, with its
          SRC item and the CHR and EXT requirements that are linked to that item.

Splitting rule (the only rule, applied the same way every time):
  * a fenced code block (from a line starting with ``` to the next such line)
    is one unit;
  * every other non-blank line is one unit;
  * blank lines belong to no unit.
A unit's ID is SRC-<file code><number of its first line, 4 digits>,
for example SRC-PS0126 = problem_statement.md line 126.

A file marked `units: user-prompts` in sources.yml (log.txt) has units only in its
"User Prompt" sections, which hold the user's own words. Every other line of it was
written by the coding agent and belongs to no unit, by rule.
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
EXT_DIR = ROOT / "requirements" / "ext"
LINE_MAP = ROOT / "requirements" / "views" / "line_map.csv"

DISPOSITIONS = ("requirement", "heading", "formatting", "context", "not-applicable")
CLASSIFIED_BY = ("rule", "ai", "user")
PENDING_REVIEW = "pending-user-review"

FENCE = re.compile(r"^\s*```")
HEADING = re.compile(r"^#{1,6}\s")
HORIZONTAL_RULE = re.compile(r"^\s*---\s*$")
TABLE_DELIMITER = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")

# log.txt (AGENTS.md section 5.2): the user's words are the lines between these two markers.
PROMPT_START = "User Prompt (verbatim, secrets redacted):"
PROMPT_END = "Agent Response Summary:"
LOG_ENTRY = re.compile(r"^## \[")


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


def unit_lines(source, lines):
    """Return the line numbers (1-based) that can belong to a source unit.

    That is every line, except in a `units: user-prompts` file (log.txt): there only the
    lines of the "User Prompt" sections can, because all other lines were written by the
    coding agent.
    """
    if source.get("units") != "user-prompts":
        return set(range(1, len(lines) + 1))
    allowed, inside = set(), False
    for number, line in enumerate(lines, start=1):
        if line == PROMPT_START:
            inside = True
        elif line == PROMPT_END or LOG_ENTRY.match(line):
            inside = False
        elif inside:
            allowed.add(number)
    return allowed


def split_units(lines, allowed):
    """Return (first, last) line numbers (1-based) of every source unit."""
    units = []
    i = 0
    while i < len(lines):
        if i + 1 not in allowed or not lines[i].strip():
            i += 1
        elif FENCE.match(lines[i]):
            end = i + 1
            while end < len(lines) and end + 1 in allowed and not FENCE.match(lines[end]):
                end += 1
            if end == len(lines) or end + 1 not in allowed:
                sys.exit(f"unclosed code fence starting at line {i + 1}")
            units.append((i + 1, end + 1))
            i = end + 1
        else:
            units.append((i + 1, i + 1))
            i += 1
    return units


def structural_rule(path, lines, first, last):
    """Classify a unit by a fixed structural rule. None means: needs judgment."""
    if first != last:
        return None
    line = lines[first - 1]
    if path.endswith(".csv"):
        return ("formatting", "rule: CSV header row") if first == 1 else None
    if not path.endswith(".md"):
        return None
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


def child_links(directory):
    """Return {parent uid: [child uids]} for the links stored in one Doorstop document."""
    children = defaultdict(list)
    for child_id, item in load_items(directory).items():
        for link in item.get("links") or []:
            children[next(iter(link)) if isinstance(link, dict) else str(link)].append(child_id)
    return children


def cmd_split(args):
    commit, files = load_sources()
    existing = set(load_items(SRC_DIR)) if args.new_only else set()
    columns = ["uid", "level", "header", "text", "normative", "reviewed", "file",
               "line_start", "line_end", "disposition", "classified_by", "note"]
    written = 0
    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for source in files:
            path = source["path"]
            lines = to_lines(read_baseline(commit, path))
            for number, (first, last) in enumerate(split_units(lines, unit_lines(source, lines)),
                                                   start=1):
                uid = unit_id(source["code"], first)
                if uid in existing:
                    continue
                rule = structural_rule(path, lines, first, last)
                # Units without a rule result must be classified by judgment before import.
                disposition, classified_by, note = (
                    (rule[0], "rule", rule[1]) if rule else ("unclassified", "", "")
                )
                writer.writerow({
                    "uid": uid,
                    "level": f"{source['level']}.{number}",
                    "header": unit_header(path, first, last),
                    "text": "\n".join(lines[first - 1:last]),
                    "normative": disposition in ("requirement", "unclassified"),
                    "reviewed": "" if rule else PENDING_REVIEW,
                    "file": path,
                    "line_start": first,
                    "line_end": last,
                    "disposition": disposition,
                    "classified_by": classified_by,
                    "note": note,
                })
                written += 1
    print(f"wrote {args.out} ({written} units)")


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
    rule = structural_rule(path, lines, first, last)
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

        allowed = unit_lines(source, lines)
        # The file, rebuilt only from SRC item texts. Lines that cannot hold a unit (the coding
        # agent's lines in log.txt) are copied from the file itself.
        rebuilt = ["" if number in allowed else line for number, line in enumerate(lines, start=1)]
        counts = Counter()
        units = split_units(lines, allowed)
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
        blank = sum(1 for number in allowed if not lines[number - 1].strip())
        agent = len(lines) - len(allowed)
        print(f"\n{path}: {len(lines)} lines ({len(allowed) - blank} non-blank, {blank} blank"
              + (f", {agent} written by the coding agent" if agent else "")
              + f") -> {len(units)} units")
        print("  " + ", ".join(f"{name} {counts[name]}" for name in DISPOSITIONS))
        print(f"  rebuilt from SRC items: {'identical to the baseline file' if identical else 'DIFFERENT'}")
        totals.update(counts)
        totals["lines"] += len(lines)
        totals["blank"] += blank
        totals["agent"] += agent
        totals["units"] += len(units)

        working = ROOT / path
        current = working.read_bytes().replace(b"\r\n", b"\n") if working.exists() else None
        if current is None:
            print("  working tree: file is missing")
        elif current == content:
            print("  working tree: unchanged since the baseline")
        elif current.startswith(content):
            added = current.count(b"\n") - content.count(b"\n")
            print(f"  working tree: {added} lines added at the end since the baseline "
                  "(the baseline is still read from git)")
        else:
            print("  working tree: CHANGED since the baseline (the baseline is still read from git)")

    for uid in sorted(set(items) - expected):
        problems.append(f"{uid}: SRC item does not match any unit of the baseline files")

    print(f"\nTOTAL: {totals['lines']} lines, {totals['blank']} blank, {totals['agent']} written by "
          f"the coding agent, {totals['units']} units: "
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
    print("\nRESULT: PASS - every line of every baseline file is covered by exactly one SRC item, "
          "verbatim, or is blank, or (log.txt only) was written by the coding agent")


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
        units = {unit_id(source["code"], first): (first, last)
                 for first, last in split_units(lines, unit_lines(source, lines))}
        items = items_by_file.pop(path, {})
        new = sorted(set(units) - set(items))
        # Unit IDs contain line numbers. If lines were added or removed, IDs shift and old texts
        # would land on the wrong units, so only files whose existing units kept their lines are
        # updated. Units after the last existing one are new (log.txt only grows at its end).
        last_existing = max((units[uid][1] for uid in items if uid in units), default=0)
        if not set(items) <= set(units) or any(
                str(item.get("line_end")) != str(units[uid][1]) for uid, item in items.items()) or any(
                units[uid][0] <= last_existing for uid in new):
            needs_decision.append(f"{path}: lines were added, removed or moved, so unit IDs shift; "
                                  "units and links must be re-mapped by a person (file left unchanged)")
            continue
        if new:
            needs_decision.append(f"{path}: {len(new)} new units ({new[0]} to {new[-1]}) have no SRC "
                                  "item yet; import them with `split --new-only` and classify them")
        for uid, item in items.items():
            first, last = units[uid]
            text = "\n".join(lines[first - 1:last])
            if item.text == text:
                continue
            item.text = text
            print(f"updated {uid}: text")
            rule = structural_rule(path, lines, first, last)
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
    chr_children, ext_children = child_links(CHR_DIR), child_links(EXT_DIR)

    LINE_MAP.parent.mkdir(parents=True, exist_ok=True)
    with open(LINE_MAP, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "line", "src_uid", "disposition", "chr_uids", "ext_uids", "text"])
        for source in files:
            lines = to_lines(read_baseline(commit, source["path"]))
            allowed = unit_lines(source, lines)
            owner = {}
            for first, last in split_units(lines, allowed):
                for number in range(first, last + 1):
                    owner[number] = unit_id(source["code"], first)
            for number, text in enumerate(lines, start=1):
                uid = owner.get(number, "")
                if uid:
                    disposition = src_items.get(uid, {}).get("disposition", "")
                else:
                    disposition = "blank" if number in allowed else "agent-text"
                writer.writerow([source["path"], number, uid, disposition,
                                 " ".join(sorted(chr_children.get(uid, []))),
                                 " ".join(sorted(ext_children.get(uid, []))), text])
    print(f"wrote {LINE_MAP.relative_to(ROOT).as_posix()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    split = commands.add_parser("split", help="write the Doorstop import CSV for the SRC document")
    split.add_argument("out", help="path of the CSV file to write")
    split.add_argument("--new-only", action="store_true",
                       help="write only the units that have no SRC item yet")
    commands.add_parser("update", help="refresh the SRC items from a new baseline commit")
    commands.add_parser("check", help="verify the SRC items against the baseline files")
    commands.add_parser("views", help="write requirements/views/line_map.csv")
    args = parser.parse_args()
    {"split": cmd_split, "update": cmd_update, "check": cmd_check, "views": cmd_views}[args.command](args)


if __name__ == "__main__":
    main()
