#!/usr/bin/env bash
# leak-check.sh - block private identifiers from entering the repo.
# Usage: leak-check.sh [--staged | --tree | --history]   (default: --staged)
# Checks: home-directory paths, IPv4 literals, non-noreply emails, denylist terms
# (file at $RESEARCH_KIT_DENYLIST, default ~/.config/research-kit/denylist; one
# case-insensitive fixed string per line, '#' comments). Runs gitleaks if installed.
# Prints label:line for hits; exit 1 on any hit, 0 otherwise.
set -u
mode=staged
case "${1:-}" in
  ""|--staged) mode=staged ;;
  --tree) mode=tree ;;
  --history) mode=history ;;
  *) echo "usage: $0 [--staged|--tree|--history]" >&2; exit 2 ;;
esac
git rev-parse --git-dir >/dev/null 2>&1 || { echo "leak-check: not a git repository" >&2; exit 2; }
cd "$(git rev-parse --show-toplevel)" || exit 2

denylist="${RESEARCH_KIT_DENYLIST:-$HOME/.config/research-kit/denylist}"
if [ ! -f "$denylist" ]; then
  echo "leak-check: no denylist at $denylist - skipping denylist layer" >&2
  denylist=""
fi

# Reads unified diff on stdin, emits "label<TAB>added-line".
diff_to_stream() {
  awk '
    /^commit [0-9a-f]+/ { commit = substr($2, 1, 10); next }
    /^\+\+\+ / { f = substr($0, 7); if ($0 ~ /^\+\+\+ \/dev\/null/) f = ""; next }
    /^--- / { next }
    /^@@ / { match($0, /\+[0-9]+/); ln = substr($0, RSTART + 1, RLENGTH - 1) + 0; next }
    /^\+/ && f != "" {
      label = (commit != "" ? commit ":" : "") f ":" ln
      print label "\t" substr($0, 2); ln++
    }'
}

tree_stream() {
  git ls-files -co --exclude-standard | while IFS= read -r f; do
    [ -f "$f" ] || continue
    grep -In '' -- "$f" 2>/dev/null | awk -v f="$f" '{ n = $0; sub(/:.*/, "", n); sub(/^[0-9]+:/, ""); print f ":" n "\t" $0 }'
  done
}

scan() {
  awk -F'\t' -v deny="$denylist" '
    BEGIN {
      home = "/ho" "me/"; users = "/Us" "ers/"
      n = 0
      if (deny != "") while ((getline t < deny) > 0) {
        sub(/\r$/, "", t); sub(/^[ \t]+/, "", t); sub(/[ \t]+$/, "", t)
        if (t == "" || t ~ /^#/) continue
        terms[++n] = tolower(t)
      }
    }
    function hit(kind, s) { printf "%s: [%s] %s\n", $1, kind, s; bad = 1 }
    {
      line = $0; sub(/^[^\t]*\t/, "", line)
      if (index(line, home) || index(line, users)) hit("home-path", line)
      # IPv4
      rest = line; off = 0
      while (match(rest, /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/)) {
        ip = substr(rest, RSTART, RLENGTH)
        before = (RSTART + off > 1) ? substr(line, RSTART + off - 1, 1) : ""
        after = substr(rest, RSTART + RLENGTH, 1)
        split(ip, o, ".")
        ok = (o[1] <= 255 && o[2] <= 255 && o[3] <= 255 && o[4] <= 255)
        if (before ~ /[0-9.A-Za-z_-]/ || after ~ /[0-9A-Za-z_]/ || after == "." ) ok = 0
        if (ip == "127.0.0.1" || ip == "0.0.0.0") ok = 0
        if (ok) hit("ipv4", ip)
        off += RSTART + RLENGTH - 1; rest = substr(rest, RSTART + RLENGTH)
      }
      # email (skipped in converted third-party sources: published author contacts)
      rest = ($1 ~ /\/02_sources\/md\//) ? "" : line
      while (match(rest, /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z][A-Za-z]+/)) {
        em = substr(rest, RSTART, RLENGTH); rest = substr(rest, RSTART + RLENGTH)
        le = tolower(em)
        if (le ~ /@users\.noreply\.github\.com$/ || le ~ /^noreply@/) continue
        hit("email", em)
      }
      low = tolower(line)
      # the author identity may be named only on its copyright/metadata lines
      if ($1 ~ /(^|:)(LICENSE|\.claude-plugin\/marketplace\.json|plugins\/research-kit\/\.claude-plugin\/plugin\.json):[0-9]+$/ && line ~ /^Copyright \(c\) |"(name|owner|author)": *[{"]/) next
      if ($1 ~ /(^|:)README\.md:[0-9]+$/ && line ~ /^\/plugin marketplace add [A-Za-z0-9-]+\/research-kit$/) next
      for (i = 1; i <= n; i++) if (index(low, terms[i])) hit("denylist", "term #" i)
    }
    END { exit bad ? 1 : 0 }'
}

rc=0
case "$mode" in
  staged) git diff --cached -U0 --no-color --diff-filter=ACM | diff_to_stream | scan || rc=1 ;;
  history) git log -p --all -U0 --no-color --format='commit %H' 2>/dev/null | diff_to_stream | scan || rc=1 ;;
  tree) tree_stream | scan || rc=1 ;;
esac

if command -v gitleaks >/dev/null 2>&1; then
  case "$mode" in
    staged) gitleaks protect --staged --no-banner >&2 2>&1 || gitleaks git --staged --no-banner >&2 2>&1 || rc=1 ;;
    history) gitleaks detect --no-banner >&2 2>&1 || rc=1 ;;
    tree) gitleaks detect --no-git --no-banner >&2 2>&1 || rc=1 ;;
  esac
fi

[ "$rc" -eq 0 ] && echo "leak-check ($mode): clean" >&2
exit "$rc"
