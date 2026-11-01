#!/usr/bin/env python3
"""Move the wiki's citations to a newer commit of the game's code.

    tools/repin.py COMMIT [--neo PATH] [--write]

Run from wiki/. Compares the pinned commit (meta.neo_commit) with COMMIT and sorts every
citation in the data, the pages and the generators into:

- unchanged: the cited lines didn't move
- moved: the lines are the same, but code above them was added or removed, so the line
  numbers shift
- changed: code inside the cited lines changed, so the fact needs checking again
- gone: the cited file was deleted

Without --write it only reports. With --write it rewrites the moved citations, gives the
changed ones their nearest new lines, and pins the data files to COMMIT. Then run
tools/check_data.py --fix to update the values read from weapon scripts and ConVars, and
check every value and page in the "changed" list by hand before committing.
"""

import argparse
import sys
from collections import defaultdict

from neosrc import CITE_RE, DEFAULT_NEO, Neo, WIKI, cited_files, datasets, format_lines, parse_lines, strings


def map_line(x, hunks):
    """Where old line x is at the new commit, and whether its own text changed."""
    offset = 0
    for os_, oc, ns, nc in hunks:
        if oc and os_ <= x < os_ + oc:
            return ns + min(x - os_, max(nc - 1, 0)), True
        if (oc and os_ + oc - 1 < x) or (not oc and os_ < x):
            offset += nc - oc
    return x + offset, False


def map_range(a, b, hunks):
    """(new_a, new_b, changed) for the old range a-b."""
    changed = any((oc and os_ <= b and a <= os_ + oc - 1) or (not oc and a <= os_ < b) for os_, oc, ns, nc in hunks)
    (na, _), (nb, _) = map_line(a, hunks), map_line(b, hunks)
    return na, max(na, nb), changed


def where_cited(sets):
    """{citation text: [paths of the data entries that hold it]}. A citation in a record's
    source or note is listed under the record, not the field."""
    out = defaultdict(list)
    for name, d in sets.items():
        for path, text in strings(d):
            if path and path[-1] in ("source", "note", "notes", "formula", "description_source"):
                path = path[:-1]
            for m in CITE_RE.finditer(text):
                out[m.group(0)].append(f"{name}.json: {'.'.join(path)}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("commit", help="the commit to move to")
    ap.add_argument("--neo", default=DEFAULT_NEO, help=f"neo checkout (default {DEFAULT_NEO})")
    ap.add_argument("--write", action="store_true", help="rewrite the citations and the pin")
    args = ap.parse_args()

    neo, sets = Neo(args.neo), datasets()
    pins = {d["meta"]["neo_commit"] for d in sets.values()}
    if len(pins) != 1:
        sys.exit(f"the data files pin different commits ({', '.join(sorted(pins))}); run tools/check_data.py")
    old_pin = pins.pop()
    old, new = neo.resolve(old_pin), neo.resolve(args.commit)
    new_pin = new[:len(old_pin)]
    if old == new:
        sys.exit(f"already pinned to {old_pin}")
    if not neo.is_ancestor(old, new):
        sys.exit(f"{args.commit} isn't newer than the pinned {old_pin}; re-pinning only moves forward")
    diff = neo.diff(old, new)

    counts = defaultdict(int)
    review = defaultdict(list)   # (old citation, new citation, why) -> [places]
    edits = {}                   # file -> new text
    for f in cited_files():
        rel = str(f.relative_to(WIKI))
        lines = f.read_text().split("\n")
        touched = False
        for i, text in enumerate(lines):
            def repl(m):
                nonlocal touched
                path, spec = m.groups()
                new_path, hunks = diff.get(path, (path, []))
                if new_path is None:
                    counts["gone"] += 1
                    review[(m.group(0), None, "file deleted")].append(f"{rel}:{i + 1}")
                    return m.group(0)
                if not spec:
                    counts["unchanged" if new_path == path else "moved"] += 1
                    return new_path
                sep = ", " if ", " in spec else ","
                mapped = [map_range(a, b, hunks) for a, b in parse_lines(spec)]
                cite = f"{new_path}:{format_lines([(a, b) for a, b, _ in mapped], sep)}"
                if any(c for _, _, c in mapped):
                    counts["changed"] += 1
                    review[(m.group(0), cite, "code changed")].append(f"{rel}:{i + 1}")
                elif cite != m.group(0):
                    counts["moved"] += 1
                else:
                    counts["unchanged"] += 1
                if cite != m.group(0):
                    touched = True
                return cite
            lines[i] = CITE_RE.sub(repl, text)
        if f.suffix == ".json":
            for i, text in enumerate(lines):
                if text.strip() == f'"neo_commit": "{old_pin}",':
                    lines[i] = text.replace(old_pin, new_pin)
                    touched = True
        if touched:
            edits[f] = "\n".join(lines)

    total = sum(counts.values())
    print(f"{old_pin} -> {new_pin}: {total} citations. {counts['unchanged']} unchanged, {counts['moved']} moved, "
          f"{counts['changed']} changed, {counts['gone']} in deleted files.")
    if review:
        cited_by = where_cited(sets)
        print("\nCheck these again: the code they cite changed.\n")
        for (was, now, why), places in sorted(review.items()):
            print(f"  {was}" + (f"  ->  {now}" if now and now != was else "") + f"  ({why})")
            recs = sorted(set(cited_by.get(was, [])))
            for r in recs:
                print(f"      {r}")
            pages = sorted({p for p in places if not p.startswith("data/")})
            for p in pages:
                print(f"      {p}")
    if args.write:
        for f, text in edits.items():
            f.write_text(text)
        print(f"\nRewrote {len(edits)} files and pinned the data to {new_pin}. Next: tools/check_data.py --fix, "
              "then check the list above.")
    else:
        print("\nNothing written. Run again with --write to apply.")


if __name__ == "__main__":
    main()
