"""The NT;RE wiki's MkDocs hooks (loaded fresh each build by ntre.py).

Adds three things on top of plain Markdown, in this order:

  {{table:...}} {{infobox:...}} {{stat:...}} {{weapon:...}}
      Data-driven snippets, expanded by generators.py from data/*.json.
  [[slug]] / [[slug|Label]] / [[slug#anchor|Label]]
      Wiki link. A slug is a page's file name without .md; for an index.md it is
      the folder name. Unknown slugs render as red links and are reported as
      warnings, so `mkdocs build --strict` fails on them.
  [[src:path:line]] / [[src:a:1; b:2]]
      Citation into NeotokyoRebuild/neo at the commit pinned in the data. Becomes
      a numbered footnote, collected under a References heading at the end.

Code spans and fenced blocks are left alone, so the syntax can be documented.
"""

import html
import importlib.util
import logging
import re
from pathlib import Path

from mkdocs.utils import get_relative_url

HOOKS = Path(__file__).resolve().parent


def load_generators():
    """Load generators.py fresh, so `mkdocs serve` picks up edits to it and to data/."""
    spec = importlib.util.spec_from_file_location("ntre_generators", HOOKS / "generators.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = load_generators()

log = logging.getLogger("mkdocs.hooks.ntre")

REPO_URL = "https://github.com/NeotokyoRebuild/neo"
SLUGS = {}  # slug -> mkdocs File
COMMIT = "HEAD"

CODE_RE = re.compile(r"^(?P<fence>```|~~~).*?^(?P=fence)[ \t]*$|(?P<ticks>`+)(?!`).+?(?<!`)(?P=ticks)(?!`)",
                     re.S | re.M)
LINK_RE = re.compile(r"\[\[(.+?)\]\]")


def esc(s):
    return html.escape(str(s), quote=True)


def slug_of(src_uri):
    p = Path(src_uri)
    if p.stem == "index":
        return p.parent.name or "index"
    return p.stem


# ---------------------------------------------------------------- events

def on_config(config):
    global COMMIT, gen
    gen = load_generators()
    COMMIT = gen.data("weapons")["meta"]["neo_commit"]
    config["copyright"] = (
        f'Game data extracted from <a href="{REPO_URL}/tree/{COMMIT}"><code>NeotokyoRebuild/neo@{COMMIT}</code></a>; '
        "footnotes link to the exact source line.<br>"
        "Prototype. All rights reserved."
    )
    return config


def on_env(env, config, files):
    env.globals["nt_mark"] = gen.asset_mark()
    return env


def on_files(files, config):
    SLUGS.clear()
    for f in files.documentation_pages():
        slug = slug_of(f.src_uri)
        if slug in SLUGS:
            log.warning("duplicate slug %r: %s and %s", slug, SLUGS[slug].src_uri, f.src_uri)
        SLUGS[slug] = f
    return files


def on_page_markdown(markdown, page, config, files):
    stash = []

    def protect(m):
        stash.append(m.group(0))
        return f"\x00{len(stash) - 1}\x00"

    def restore(text):
        return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)

    text = CODE_RE.sub(protect, markdown)
    text = gen.expand(text, page.meta, warn=lambda msg: log.warning("%s: %s", page.file.src_uri, msg))
    text = Renderer(page).render(text)
    return restore(text)


THEAD_RE = re.compile(r"<thead>.*?</thead>", re.S)
TH_RE = re.compile(r"(<th\b[^>]*>)(.*?)(</th>)", re.S)


# Modes still in development, their roles and their weapons are named only on their own pages.
WIP_ONLY_ON = {"vip", "juggernaut"}
WIP_TERMS = re.compile(r"\bVIP\b|[Jj]uggernaut|\bJGR\b|\bSMAC\b|\bBALC\b|\bjgr\b|_vip\b|_jgr\b|\bsv_neo_vip|"
                       r"\bsv_neo_jgr|/vip/|/juggernaut/", re.I)


# The one place outside their own pages that may name them: the modes table.
WIP_ALLOWED_IN = {"game-modes": re.compile(r'<table class="wikitable modes">.*?</table>', re.S)}


def check_wip_mentions(html_out, page):
    slug = slug_of(page.file.src_uri)
    if slug in WIP_ONLY_ON:
        return
    if slug in WIP_ALLOWED_IN:
        html_out = WIP_ALLOWED_IN[slug].sub(" ", html_out)
    text = re.sub(r"<[^>]*\bhref=\"([^\"]*)\"[^>]*>", r" \1 ", html_out)   # keep link targets
    text = re.sub(r"<[^>]+>", " ", text)
    for m in WIP_TERMS.finditer(html.unescape(text)):
        ctx = html.unescape(text)[max(0, m.start() - 40):m.end() + 30].replace("\n", " ")
        log.warning("%s: names a mode in development (%r): ...%s...", page.file.src_uri, m.group(0), " ".join(ctx.split()))


INFOBOX_RE = re.compile(r"<aside class=\"infobox[^\"]*\".*?</aside>", re.S)
NUM_TD_RE = re.compile(r"(<td\b[^>]*(?:class=\"[^\"]*\bnum\b[^\"]*\"|text-align: right)[^>]*>)(.*?)(</td>)", re.S)
CITE_SUP_RE = re.compile(r"<sup id=\"fnref[^\"]*\">.*?</sup>", re.S)


def lead_citations(html_out):
    """In numeric (right-aligned) table cells, put citation markers before the value, so the
    numbers line up on their right edge. Infoboxes and text cells are left as they are."""
    boxes = []

    def stash(m):
        boxes.append(m.group(0))
        return f"\x00box{len(boxes) - 1}\x00"

    def cell(m):
        open_tag, inner, close = m.groups()
        sups = CITE_SUP_RE.findall(inner)
        if not sups:
            return m.group(0)
        rest = CITE_SUP_RE.sub("", inner)
        lead = "".join(sups).replace("<sup ", '<sup class="cite-lead" ', len(sups))
        return f"{open_tag}{lead}{rest.strip()}{close}"

    html_out = INFOBOX_RE.sub(stash, html_out)
    html_out = NUM_TD_RE.sub(cell, html_out)
    return re.sub(r"\x00box(\d+)\x00", lambda m: boxes[int(m.group(1))], html_out)


CITE_THEN_UNIT_RE = re.compile(
    r"((?:<sup [^>]*id=\"fnref[^\"]*\"[^>]*>(?:(?!</?sup\b).)*</sup>)+)"
    r"(\s*(?:u/s|/s|ms|min|s|u|m|HP|XP|AUX|°|%|units? per second|milliseconds?|seconds?|minutes?"
    r"|units?|degrees?|metres?|rounds?|points?|shots?|pellets?|players?)(?![\w/]))", re.S)


def keep_units_with_numbers(html_out):
    """A citation never sits between a number and its unit: "5[2] /s" becomes "5 /s[2]".
    Happens when a page writes a unit after {{stat:...}}, whose citation follows the number."""
    return CITE_THEN_UNIT_RE.sub(lambda m: m.group(2) + m.group(1), html_out)


CELL_RE = re.compile(r"(<t[dh]\b[^>]*>)(.*?)(</t[dh]>)", re.S)
CODE_SPAN_RE = re.compile(r"<code\b.*?</code>", re.S)
SPACED_UNIT_RE = re.compile(r"(\d)(?:\s|&nbsp;)+(u/s|/s|ms|min|s|u|m|°)(?![\w/])")


def unspace_units(html_out):
    """In data (table and infobox cells), an abbreviated unit sits right against its number:
    "0.5 s" becomes "0.5s", "5 /s" becomes "5/s". Prose spells units out, so it's left alone,
    and so are code spans. Game terms (HP, XP, RPM) keep their space."""
    def cell(m):
        open_tag, inner, close = m.groups()
        codes = []
        inner = CODE_SPAN_RE.sub(lambda c: codes.append(c.group(0)) or f"\x00code{len(codes) - 1}\x00", inner)
        inner = SPACED_UNIT_RE.sub(r"\1\2", inner)
        inner = re.sub(r"\x00code(\d+)\x00", lambda c: codes[int(c.group(1))], inner)
        return open_tag + inner + close
    return CELL_RE.sub(cell, html_out)


def on_page_content(html_out, page, config, files):
    """Give every table column header a tooltip (from wiki/column-tips.yml), and move
    citations in numeric cells in front of the value."""
    check_wip_mentions(html_out, page)
    html_out = lead_citations(html_out)
    html_out = keep_units_with_numbers(html_out)
    html_out = unspace_units(html_out)
    slug = slug_of(page.file.src_uri)
    data_page = not page.file.src_uri.startswith("about/")

    def th(m):
        open_tag, inner, close = m.groups()
        if "col-tip" in inner:
            return m.group(0)
        label = re.sub(r"\s+", " ", re.sub(r"<sup.*?</sup>|<[^>]+>", "", inner)).strip()
        label = html.unescape(label)
        if not label:
            return m.group(0)
        tip = gen.column_tip(slug, label)
        if not tip:
            if data_page:
                log.warning("%s: column %r has no tooltip; add it to wiki/column-tips.yml",
                            page.file.src_uri, label)
            return m.group(0)
        return f'{open_tag}<span class="col-tip" title="{esc(tip)}">{inner}</span>{close}'

    return THEAD_RE.sub(lambda t: TH_RE.sub(th, t.group(0)), html_out)


# ---------------------------------------------------------------- rendering

class Renderer:
    def __init__(self, page):
        self.page = page
        self.refs = []      # citation specs in order of first use
        self.uses = {}      # spec -> number of times cited so far

    def render(self, text):
        text = LINK_RE.sub(self.link, text)
        if self.refs:
            text = text.rstrip() + "\n\n## References\n\n" + self.references() + "\n"
        return text

    def link(self, m):
        inner = m.group(1).replace("\\|", "|")  # pipe tables escape the separator
        if inner.startswith("src:"):
            return "".join(self.cite(s.strip()) for s in inner[4:].split(";") if s.strip())
        target, _, label = inner.partition("|")
        slug, _, anchor = target.strip().partition("#")
        label = label or target
        frag = f"#{anchor}" if anchor else ""
        if not slug:
            return f'<a href="{frag}">{label}</a>'
        f = SLUGS.get(slug)
        if f is None:
            log.warning("%s: red link [[%s]]", self.page.file.src_uri, inner)
            return f'<a class="new" title="{esc(slug)} (page does not exist)">{label}</a>'
        href = get_relative_url(f.url, self.page.file.url) + frag
        return f'<a href="{esc(href)}">{label}</a>'

    def cite(self, spec):
        # Markup matches Python-Markdown's footnotes, so Material styles them and
        # shows them as tooltips (content.footnote.tooltips).
        if spec not in self.uses:
            self.refs.append(spec)
            self.uses[spec] = 0
        n = self.refs.index(spec) + 1
        self.uses[spec] += 1
        k = self.uses[spec]
        ref_id = f"fnref:{n}" if k == 1 else f"fnref{k}:{n}"
        return f'<sup id="{ref_id}"><a class="footnote-ref" href="#fn:{n}">{n}</a></sup>'

    def source_url(self, spec):
        m = re.match(r"(.+?):(\d+)", spec)
        path, line = (m.group(1), m.group(2)) if m else (spec, None)
        url = f"{REPO_URL}/blob/{COMMIT}/{path}"
        return f"{url}#L{line}" if line else url

    def references(self):
        items = []
        for n, spec in enumerate(self.refs, 1):
            backs = "".join(
                f'&nbsp;<a class="footnote-backref" href="#{"fnref" if k == 1 else f"fnref{k}"}:{n}" '
                f'title="Jump back to citation {n}">&#8617;</a>'
                for k in range(1, self.uses[spec] + 1))
            items.append(f'<li id="fn:{n}"><p><a href="{esc(self.source_url(spec))}"><code>{esc(spec)}</code></a>'
                         f"{backs}</p></li>")
        return f'<div class="footnote references"><ol>{"".join(items)}</ol></div>'
