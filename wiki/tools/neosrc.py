"""Shared helpers for the data tools: find citations, and read the game's code at a commit.

Standard library only. The game's code is read with `git show <commit>:<path>` from a local
checkout of NeotokyoRebuild/neo, so the checkout's own state (branch, edits) never matters.
"""

import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

WIKI = Path(__file__).resolve().parent.parent
REPO = WIKI.parent
DATA = WIKI / "data"
DOCS = WIKI / "docs"
DEFAULT_NEO = REPO.parent / "neo"

# Files whose text can hold citations: the data, the pages, and the generators.
def cited_files():
    return [*sorted(DATA.glob("*.json")), *sorted(DOCS.rglob("*.md")), WIKI / "hooks" / "generators.py"]


# A citation: a repo-relative path under src/ or game/, then optionally ':' and lines,
# as a number, a range or a comma-separated list of both ("12", "12-15", "12,20-22").
LINES = r"\d+(?:-\d+)?(?:,\s?\d+(?:-\d+)?)*"
CITE_RE = re.compile(rf"(?<![\w/.\-])((?:src|game)/[\w/.\-]+\.\w+)(?::({LINES}))?")


def parse_lines(spec):
    """'12-15, 20' -> [(12, 15), (20, 20)]"""
    out = []
    for part in re.split(r",\s?", spec):
        a, _, b = part.partition("-")
        out.append((int(a), int(b or a)))
    return out


def format_lines(ranges, sep=","):
    return sep.join(f"{a}" if a == b else f"{a}-{b}" for a, b in ranges)


def load(name):
    return json.loads((DATA / f"{name}.json").read_text())


def datasets():
    return {p.stem: json.loads(p.read_text()) for p in sorted(DATA.glob("*.json"))}


def save(name, data):
    (DATA / f"{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def records(node, path=()):
    """Yield (path, record) for every {"value": ...} record. A list item's path segment is
    its id (or name), as in {{stat:…}} paths."""
    if isinstance(node, dict):
        if "value" in node:
            yield path, node
        for k, v in node.items():
            yield from records(v, (*path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            key = (v.get("id") or v.get("name")) if isinstance(v, dict) else None
            yield from records(v, (*path, str(key or i)))


def strings(node, path=()):
    """Yield (path, text) for every string in a dataset, with list items named as in records()."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v, (*path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            key = (v.get("id") or v.get("name")) if isinstance(v, dict) else None
            yield from strings(v, (*path, str(key or i)))


class Neo:
    """A local checkout of NeotokyoRebuild/neo, read at any commit."""

    def __init__(self, path=DEFAULT_NEO):
        self.path = Path(path)
        if not (self.path / ".git").exists():
            raise SystemExit(f"no neo checkout at {self.path}; pass --neo PATH")

    def git(self, *args, check=True):
        r = subprocess.run(["git", "-C", str(self.path), *args], capture_output=True, text=True)
        if check and r.returncode:
            raise SystemExit(f"git {' '.join(args)}: {r.stderr.strip()}")
        return r

    def resolve(self, commit):
        """The full hash for a commit. The tools never fetch: they leave the checkout alone."""
        r = self.git("rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}", check=False)
        if r.returncode:
            raise SystemExit(f"{self.path} doesn't have commit {commit}; run git -C {self.path} fetch")
        return r.stdout.strip()

    def is_ancestor(self, a, b):
        return self.git("merge-base", "--is-ancestor", a, b, check=False).returncode == 0

    @lru_cache(maxsize=None)
    def lines(self, commit, path):
        """The file's lines at the commit, or None if it doesn't exist there."""
        r = self.git("show", f"{commit}:{path}", check=False)
        return None if r.returncode else r.stdout.split("\n")

    def diff(self, old, new):
        """{old path: (new path or None if deleted, [hunks])} for every file that changed
        between the commits. A hunk is (old_start, old_count, new_start, new_count), from
        `git diff -U0`; a count of 0 means lines were only added (or only removed) there."""
        out, cur = {}, None
        text = self.git("diff", "-U0", "--no-color", "--no-ext-diff", "-M", old, new).stdout
        for line in text.split("\n"):
            if line.startswith("diff --git "):
                a, b = re.match(r"diff --git a/(.+) b/(.+)$", line).groups()
                cur = [a, b, []]
                out[a] = cur
            elif cur is None:
                continue
            elif line.startswith("rename from "):
                cur[0] = line[len("rename from "):]
            elif line.startswith("rename to "):
                cur[1] = line[len("rename to "):]
            elif line == "+++ /dev/null":
                cur[1] = None
            elif line.startswith("@@ "):
                a, b, c, d = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line).groups()
                cur[2].append((int(a), int(b or 1), int(c), int(d or 1)))
        return {a: (b, hunks) for a, b, hunks in out.values()}
