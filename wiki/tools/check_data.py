#!/usr/bin/env python3
"""Check the wiki's game data against the game's code.

    tools/check_data.py [--neo PATH] [--fix]

Run from wiki/. Checks, at the commit pinned in the data files' meta.neo_commit:

- every data file pins the same commit
- every value has a source, a null value says why in a note, and a derived value has a formula
- every citation, in the data, the pages and the generators, names a file that exists
  and lines that exist in it
- values read straight from the code still match it: weapon script keys
  ("Damage" "12") and ConVar defaults (ConVar x("sv_name", "3.25", ...))

With --fix, values of those two kinds that no longer match are updated from the code.
Exits 1 if anything is wrong.
"""

import argparse
import re
import sys

from neosrc import CITE_RE, DEFAULT_NEO, Neo, cited_files, datasets, parse_lines, records, save, WIKI

SCRIPT_SRC = re.compile(r"(game/neo/scripts/[\w.]+\.txt):(\d+)")
KEYVALUE = re.compile(r'^\s*"([^"]+)"\s+"([^"]*)"')
CONVAR = re.compile(r'ConVar\s+\w+\s*\(\s*"([^"]+)"\s*,\s*(.*)', re.S)
NEO_BRANCH = re.compile(r'^\s*#\s*(?:ifdef\s+NEO\b|if\s+defined\s*\(?\s*NEO\b|elif\s+defined\s*\(?\s*NEO\b).*?\n\s*"([^"]*)"', re.M)


def convar_default(lines, start):
    """(name, default) for the ConVar defined from line `start`, or (name, None) if its
    default isn't a plain string: a macro, say. Handles an `#ifdef NEO` default."""
    m = CONVAR.search("\n".join(lines[start - 1:start + 11]))
    if not m:
        return None, None
    name, rest = m.groups()
    if rest.startswith('"'):
        return name, rest[1:rest.index('"', 1)]
    if rest.lstrip().startswith("#"):
        branch = NEO_BRANCH.search(rest)
        return name, branch.group(1) if branch else None
    return name, None


class Report:
    def __init__(self):
        self.errors, self.warnings, self.fixed, self.unreadable = [], [], [], []

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def same(a, b):
    """Does the data value a equal the code's text b?"""
    if isinstance(a, bool):
        return str(int(a)) == b or str(a).lower() == b.lower()
    if isinstance(a, (int, float)):
        try:
            return abs(float(b) - a) <= 1e-9 * max(1, abs(a))
        except ValueError:
            return False
    return str(a) == b


def as_data(text, like):
    """The code's text as the same type as the data's current value."""
    if isinstance(like, bool):
        return text not in ("0", "false", "")
    if isinstance(like, int):
        return int(float(text))
    if isinstance(like, float):
        return float(text)
    return text


def check_pins(sets, rep):
    pins = {name: d.get("meta", {}).get("neo_commit") for name, d in sets.items()}
    if len(set(pins.values())) != 1:
        rep.error("data", f"files pin different commits: {pins}")
    return next(iter(pins.values()))


def check_records(sets, rep):
    for name, d in sets.items():
        for path, rec in records(d):
            where = f"{name}.json: {'.'.join(path)}"
            if rec.get("value") is None:
                if not (rec.get("note") or rec.get("notes")):
                    rep.error(where, "null value with no note saying why")
            elif not rec.get("source"):
                rep.error(where, "value with no source")
            if rec.get("derived") and not rec.get("formula"):
                rep.error(where, "derived value with no formula")
            if "computed" in rec:
                rep.error(where, "'computed' is the old marker; use \"derived\": true and a \"formula\"")


def check_citations(neo, commit, rep):
    n = 0
    for f in cited_files():
        rel = f.relative_to(WIKI)
        for lineno, text in enumerate(f.read_text().split("\n"), 1):
            for m in CITE_RE.finditer(text):
                n += 1
                path, spec = m.groups()
                lines = neo.lines(commit, path)
                where = f"{rel}:{lineno}"
                if lines is None:
                    rep.error(where, f"{path} doesn't exist at {commit}")
                    continue
                for a, b in parse_lines(spec) if spec else []:
                    if not (1 <= a <= b <= len(lines)):
                        rep.error(where, f"{path}:{spec} is outside the file ({len(lines)} lines) at {commit}")
                        break
    return n


def check_values(sets, neo, commit, rep, fix):
    checked = 0
    changed = set()
    fixed_sources = set()
    for name, d in sets.items():
        for path, rec in records(d):
            src, v = rec.get("source") or "", rec.get("value")
            if v is None or rec.get("derived") or isinstance(v, (dict, list)):
                continue
            where = f"{name}.json: {'.'.join(path)}"
            m = SCRIPT_SRC.fullmatch(src)
            if m:
                lines = neo.lines(commit, m.group(1))
                kv = KEYVALUE.match(lines[int(m.group(2)) - 1]) if lines and int(m.group(2)) <= len(lines) else None
                if not kv:
                    rep.warn(where, f"{src} isn't a \"Key\" \"value\" line, so the value can't be checked")
                    continue
                checked += 1
                if not same(v, kv.group(2)):
                    if fix:
                        rec["value"] = as_data(kv.group(2), v)
                        changed.add(name)
                        rep.fixed.append(f"{where}: {v!r} -> {rec['value']!r} ({src}: \"{kv.group(1)}\")")
                        fixed_sources.add(src)
                    else:
                        rep.error(where, f"is {v!r}, but {src} says \"{kv.group(1)}\" \"{kv.group(2)}\"")
        for i, cv in enumerate(d.get("convars") or []):
            where = f"{name}.json: convars.{cv.get('name', i)}"
            path, _, spec = (cv.get("source") or "").partition(":")
            lines = neo.lines(commit, path)
            if not (lines and spec):
                rep.error(where, f"can't read its source {cv.get('source')!r}")
                continue
            found = [convar_default(lines, a) for a, _ in parse_lines(spec)]
            cv_name, default = next((f for f in found if f[0] == cv["name"]), (None, None))
            if cv_name is None:
                rep.error(where, f"{cv['source']} doesn't define ConVar {cv['name']}")
                continue
            if default is None:
                rep.unreadable.append(f"{where}: {cv['source']} sets the default with a macro")
                continue
            checked += 1
            if default != str(cv.get("default")):
                if fix:
                    rep.fixed.append(f"{where}: default {cv.get('default')!r} -> {default!r}")
                    cv["default"] = default
                    changed.add(name)
                else:
                    rep.error(where, f"default is {cv.get('default')!r}, but {cv['source']} says {default!r}")
    for name, d in sets.items():
        for path, rec in records(d):
            hit = [s for s in fixed_sources if rec.get("derived") and s in (rec.get("source") or "")]
            if hit:
                rep.warn(f"{name}.json: {'.'.join(path)}", f"is derived from {hit[0]}, which was just updated; "
                         f"work it out again ({rec.get('formula')})")
    for name in sorted(changed):
        save(name, sets[name])
    return checked


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--neo", default=DEFAULT_NEO, help=f"neo checkout (default {DEFAULT_NEO})")
    ap.add_argument("--fix", action="store_true", help="update script and ConVar values that no longer match")
    ap.add_argument("-v", "--verbose", action="store_true", help="list the values that can't be read from the code")
    args = ap.parse_args()

    neo, sets, rep = Neo(args.neo), datasets(), Report()
    commit = check_pins(sets, rep)
    check_records(sets, rep)
    n_cites = check_citations(neo, commit, rep)
    n_values = check_values(sets, neo, commit, rep, args.fix)

    for line in rep.fixed:
        print(f"fixed    {line}")
    for line in rep.unreadable if args.verbose else []:
        print(f"skipped  {line}")
    for line in rep.warnings:
        print(f"warning  {line}")
    for line in rep.errors:
        print(f"error    {line}")
    print(f"\n{n_cites} citations and {n_values} values checked at {commit}: "
          f"{len(rep.errors)} errors, {len(rep.warnings)} warnings"
          + (f", {len(rep.fixed)} values updated" if rep.fixed else "")
          + (f"; {len(rep.unreadable)} defaults set by macros can't be checked (-v lists them)" if rep.unreadable else ""))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
