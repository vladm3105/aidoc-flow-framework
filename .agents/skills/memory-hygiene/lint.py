#!/usr/bin/env python3
"""memory-hygiene — assert the memory store's invariants.

Adapted from GlassOnTin/claude-memory-skills @ skills/memory-lint/lint.py (MIT).
Three changes from upstream, each for a defect found by running it on the real
stores (2026-08-12, 14 stores, 341 memories):

  1. MEMORY.md absence no longer crashes. Upstream opens it unguarded, so a
     store with no index raised IOError instead of reporting the defect.
  2. NEW check `content` — prose, tables or code in MEMORY.md instead of
     one-line pointers. Upstream has no such check, so it reported the one
     store known to be broken as "clean ✓ (0 memories)".
  3. NEW check `noindex` — memories on disk with no MEMORY.md at all.

Both new checks are MANUAL-TRIAGE ONLY. --fix must never act on them: splitting
a content-bearing index is a judgement call about what is still true, and the
file is often the only copy of the data.

Usage:  lint.py [<memory_dir>] [--fix] [--brief]
  (no dir) → uses cwd as the memory dir.
  --fix    → back up, then apply the DETERMINISTIC repairs only:
             name: → filename-stem, and rewrite [[links]] to stems.
             Coverage, over-length, slug-titles, content-in-index and
             missing-index are NOT auto-fixed.

Exit 0 if every invariant passes, 1 if any fails (hook/CI friendly).
"""
import os, re, sys, time, tarfile

FIX = "--fix" in sys.argv
BRIEF = "--brief" in sys.argv
pos = [a for a in sys.argv[1:] if not a.startswith("--")]
D = pos[0] if pos else os.getcwd()
if not os.path.isdir(D):
    if not BRIEF: print(f"memory-hygiene: no memory store at {D} — skipping")
    sys.exit(0)
os.chdir(D)

SKIP = {"MEMORY.md", "CANDIDATES.md"}
OVER = 300          # hook-text length ceiling (== compact's giant allowance)
CONTENT_ALLOWANCE = 3   # calibrated: healthy stores carry 0-2 non-pointer lines

def files():   return [f for f in os.listdir(".") if f.endswith(".md") and f not in SKIP]
def stemset(): return set(f[:-3] for f in files())

def fm_name(text):
    if not text.startswith("---"): return None
    end = text.find("\n---", 3); fm = text[:end] if end > 0 else text
    m = re.search(r'^name:\s*(.+)$', fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None

def strip_pfx(s): return re.sub(r'^(project|feedback|reference|plan)_', '', s)
LINK = re.compile(r'\[\[([A-Za-z0-9_.\-]+)\]\]')
HOOK = re.compile(r'^- \[(?P<t>.*?)\]\((?P<f>[A-Za-z0-9_.\-]+\.md)\)(?: — (?P<h>.*))?$')
HEADING = re.compile(r'^#{1,6}\s')
HRULE = re.compile(r'^(-{3,}|\*{3,}|_{3,})\s*$')

def name2stem():
    m = {}
    for f in files():
        nm = fm_name(open(f, encoding="utf-8").read())
        if nm and nm != f[:-3]: m.setdefault(nm, f[:-3])
    return m

def resolve(X, stems, n2s):
    if X in stems: return X
    if X.endswith(".md") and X[:-3] in stems: return X[:-3]
    if X in n2s: return n2s[X]
    xn = X.replace("-", "_"); xn = xn[:-3] if xn.endswith(".md") else xn
    c = {S for S in stems if S == xn or S.endswith("_" + xn) or strip_pfx(S) == strip_pfx(xn)}
    return next(iter(c)) if len(c) == 1 else None

def check():
    stems = stemset(); n2s = name2stem()
    badname = [f for f in files() if fm_name(open(f, encoding="utf-8").read()) != f[:-3]]
    danglers = {}
    for f in files() + ["MEMORY.md", "CANDIDATES.md"]:
        if not os.path.exists(f): continue
        for X in LINK.findall(open(f, encoding="utf-8").read()):
            if X not in stems and X not in danglers:
                danglers[X] = resolve(X, stems, n2s)   # fuzzy target, or None

    disk = set(files())
    slug = []; over = []; idx = []; content = 0
    has_index = os.path.exists("MEMORY.md")
    if has_index:
        for l in open("MEMORY.md", encoding="utf-8"):
            line = l.rstrip("\n")
            m = HOOK.match(line)
            if m:
                t, f, h = m.group("t"), m.group("f"), m.group("h") or ""
                idx.append(f)
                if t == f or (" " not in t and re.match(r'^[a-z0-9][a-z0-9_\-]*$', t)):
                    slug.append(f)
                if len(h) > OVER: over.append(f)
                continue
            # anything that is not a pointer, a heading, a rule or blank is CONTENT
            if line.strip() and not HEADING.match(line) and not HRULE.match(line):
                content += 1

    # an index that is mostly content, or holds content with no pointers at all
    content_defect = content > CONTENT_ALLOWANCE or (content > 0 and not idx)
    noindex = bool(disk) and not has_index

    return dict(badname=badname, danglers=danglers, slug=slug, over=over,
                orphan=sorted(disk - set(idx)), stale=sorted(set(idx) - disk),
                dupes=sorted({f for f in idx if idx.count(f) > 1}),
                content=content, content_defect=content_defect,
                has_index=has_index, noindex=noindex,
                nfiles=len(disk), nidx=len(idx))

def report(r):
    bad = sorted(k for k, v in r['danglers'].items() if v is None)
    fixable = sorted(k for k, v in r['danglers'].items() if v is not None)
    def L(ok, label, detail, remedy):
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {detail}" + ("" if ok else f"   → {remedy}"))
    print(f"memory-hygiene — {D}  ({r['nfiles']} memories)")
    L(not r['badname'], "name == filename-stem", f"{len(r['badname'])} off", "lint --fix")
    L(not r['danglers'], "[[links]] resolve",
      f"{len(fixable)} auto-fixable, {len(bad)} unresolvable",
      "; ".join(([f"lint --fix ({len(fixable)})"] if fixable else []) + ([f"manual: {bad}"] if bad else [])))
    L(not r['slug'], "no slug titles in index", f"{len(r['slug'])} slug-titled", "memory-reindex / retitle from body")
    L(not (r['orphan'] or r['stale'] or r['dupes']), "index 1:1 with files",
      f"{len(r['orphan'])} orphan, {len(r['stale'])} stale, {len(r['dupes'])} dup  ({r['nidx']} idx / {r['nfiles']} files)", "memory-reindex")
    L(not r['over'], f"no hook text > {OVER} chars", f"{len(r['over'])} bloated", "memory-compact")
    L(not r['content_defect'], "MEMORY.md is an index, not content",
      f"{r['content']} content line(s), {r['nidx']} pointer(s)",
      "MANUAL — split each fact into its own memory, leave one-line pointers. NEVER --fix: the index may be the only copy")
    L(not r['noindex'], "index exists", f"{r['nfiles']} memories, no MEMORY.md", "memory-reindex")
    ok = not (r['badname'] or r['danglers'] or r['slug'] or r['orphan'] or r['stale']
              or r['dupes'] or r['over'] or r['content_defect'] or r['noindex'])
    print("RESULT:", "clean ✓" if ok else "violations — see remedies above")
    return ok

def do_fix():
    """Deterministic repairs ONLY: name: fields and [[link]] targets.

    Never touches MEMORY.md content, never splits an index, never deletes.
    Backs up every file it is about to write first.
    """
    stems = stemset(); n2s = name2stem()
    pending = {}; nlink = nname = 0
    for f in files() + ["MEMORY.md", "CANDIDATES.md"]:
        if not os.path.exists(f): continue
        orig = open(f, encoding="utf-8").read()
        def repl(m):
            nonlocal nlink
            X = m.group(1); r = resolve(X, stems, n2s)
            if r and r != X: nlink += 1; return f"[[{r}]]"
            return m.group(0)
        text = LINK.sub(repl, orig)
        if f not in SKIP and text.startswith("---"):
            end = text.find("\n---", 3); head, rest = text[:end], text[end:]
            nh, n = re.subn(r'(?m)^name:.*$', f"name: {f[:-3]}", head, count=1)
            if n and nh != head: nname += 1; text = nh + rest
        if text != orig: pending[f] = text
    if not pending:
        print("--fix: no name/link drift — store already normalized\n"); return
    os.makedirs(".backups", exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    with tarfile.open(f".backups/lint-fix-{ts}.tar.gz", "w:gz") as tar:
        for f in pending: tar.add(f)
    for f, text in pending.items(): open(f, "w", encoding="utf-8").write(text)
    print(f"--fix: normalized {nname} name: fields, rewrote {nlink} links in {len(pending)} files  (backup: .backups/lint-fix-{ts}.tar.gz)\n")

def brief():
    """One-line health summary — surfaces only actionable issues; known
    unresolvable danglers are a quiet note."""
    r = check()
    act = []
    if r['content_defect']:
        act.append(f"MEMORY.md holds {r['content']} content lines, not pointers (MANUAL)")
    if r['noindex']: act.append(f"{r['nfiles']} memories with no index (reindex)")
    if r['orphan'] or r['stale'] or r['dupes']:
        act.append(f"{len(r['orphan']) + len(r['stale']) + len(r['dupes'])} coverage (reindex)")
    if r['slug']: act.append(f"{len(r['slug'])} slug-titles (reindex)")
    if r['over']: act.append(f"{len(r['over'])} bloated (compact)")
    fixable = [k for k, v in r['danglers'].items() if v is not None]
    bad = [k for k, v in r['danglers'].items() if v is None]
    if fixable: act.append(f"{len(fixable)} fixable links (lint --fix)")
    note = f"; {len(bad)} unresolvable links pending manual triage" if bad else ""
    if act: print(f"memory-hygiene: needs attention — {'; '.join(act)}{note}  ({r['nfiles']} memories)")
    else:   print(f"memory-hygiene: clean ✓  ({r['nfiles']} memories{note})")

if BRIEF:
    brief(); sys.exit(0)
if FIX: do_fix()
sys.exit(0 if report(check()) else 1)
