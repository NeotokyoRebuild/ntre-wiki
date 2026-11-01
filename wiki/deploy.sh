#!/usr/bin/env bash
# Publish the wiki to wiki/<version>/ on the gh-pages branch of
# sunmachine/ntre-dev and point the `latest` alias at it. This is what a CI
# job on push to main would do, run locally.
#
#   ./deploy.sh                          redeploy the current latest version
#   ./deploy.sh 0.2 "0.2 (prototype)"    deploy a new version and make it latest
#   ./deploy.sh --dry-run [version ...]  do everything except push
#
# It only deploys commits that are already pushed to main in git, from a clean tree.
# The published address is set here and nowhere else (override with
# NTRE_WIKI_URL).
set -euo pipefail
cd "$(dirname "$0")"

DRY_RUN=0
if [[ ${1:-} == --dry-run ]]; then DRY_RUN=1; shift; fi

PAGES_REPO=sunmachine/ntre-dev
REMOTE=ntre-dev
BRANCH=gh-pages
PREFIX=wiki
export NTRE_WIKI_URL=${NTRE_WIKI_URL:-https://sunmachine.github.io/ntre-dev/wiki/}
export NO_MKDOCS_2_WARNING=1
export PATH="$PWD/.venv/bin:$PATH"

say() { printf '\033[1m==> %s\033[0m\n' "$*"; }
die() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }

command -v mike >/dev/null || die "mike not found: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
git remote get-url "$REMOTE" >/dev/null 2>&1 || die "no '$REMOTE' remote: see 'Deploy' in the README"

# 1. Only deploy what's committed and pushed to main in git.
say "Checking the source"
[[ -z $(git status --porcelain) ]] || die "uncommitted changes: commit and push first"
git fetch -q origin main
git merge-base --is-ancestor HEAD origin/main || die "HEAD $(git rev-parse --short HEAD) isn't on origin/main: push it first"
SHA=$(git rev-parse --short HEAD)

# 2. Bring gh-pages up to date; fails rather than overwrite a diverged branch.
say "Fetching $REMOTE/$BRANCH"
git fetch -q "$REMOTE" "$BRANCH:$BRANCH"

# 3. Version and title: from the arguments, or the current latest.
if [[ $# -ge 1 ]]; then
  VERSION=$1
  TITLE=${2:-$1}
else
  read -r VERSION TITLE < <(git show "$BRANCH:$PREFIX/versions.json" | python3 -c '
import json, sys
v = next(v for v in json.load(sys.stdin) if "latest" in v["aliases"])
print(v["version"], v["title"])')
  [[ -n $VERSION ]] || die "no version has the latest alias: pass one, e.g. ./deploy.sh 0.1"
fi

# 4. Build strictly, then commit the build to gh-pages with mike (no push yet).
say "Building $SHA"
# Not --quiet: it hides warnings from --strict, which then passes them.
mkdocs build --strict 2>&1 | { grep -v '^INFO' || true; }
say "Deploying $VERSION ($TITLE) to $BRANCH"
mike deploy --update-aliases --title "$TITLE" \
  -m "Deploy the wiki $VERSION from ntre-wiki $SHA" "$VERSION" latest
mike set-default --template redirect.html \
  -m "Point the wiki at its latest version" latest

# 5. Guard rails: the branch also hosts other pages.
say "Checking the result"
outside=$(git diff --name-only "$REMOTE/$BRANCH" "$BRANCH" | grep -v "^$PREFIX/" || true)
[[ -z $outside ]] || die "deploy touched files outside $PREFIX/: $outside (reset with: git branch -f $BRANCH $REMOTE/$BRANCH)"
links=$(git ls-tree -r "$BRANCH" | awk '$1 == "120000" {print $4}')
[[ -z $links ]] || die "symlinks on $BRANCH, which GitHub Pages rejects: $links"
git merge-base --is-ancestor "$REMOTE/$BRANCH" "$BRANCH" || die "$BRANCH isn't a fast-forward of $REMOTE/$BRANCH"

if (( DRY_RUN )); then
  say "Dry run: not pushing. To discard the local deploy: git branch -f $BRANCH $REMOTE/$BRANCH"
  exit 0
fi

# 6. Publish and wait for GitHub Pages.
say "Pushing to $REMOTE"
git push -q "$REMOTE" "$BRANCH"
if command -v gh >/dev/null; then
  deployed=$(git rev-parse "$BRANCH")
  say "Waiting for GitHub Pages"
  for _ in $(seq 1 30); do
    id=$(gh api "repos/$PAGES_REPO/deployments?sha=$deployed&per_page=1" --jq '.[0].id // empty' 2>/dev/null || true)
    state=${id:+$(gh api "repos/$PAGES_REPO/deployments/$id/statuses" --jq '.[0].state // empty' 2>/dev/null || true)}
    case $state in
      success) break ;;
      failure|error) die "GitHub Pages deploy $state: https://github.com/$PAGES_REPO/deployments" ;;
    esac
    sleep 10
  done
  [[ ${state:-} == success ]] || die "timed out waiting for GitHub Pages: https://github.com/$PAGES_REPO/deployments"
fi
say "Published ${NTRE_WIKI_URL}latest/ ($VERSION from $SHA)"
