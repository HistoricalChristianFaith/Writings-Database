#!/usr/bin/env python3
"""validate.py <wd> [file.html]   (default: the work's file in the repo)

Hard checks (exit 1 on failure): footnote markers and definitions numbered 1..k in order and two-way linked; no
leftover pipeline placeholders; only allowed markup; balanced <i>. Soft report: leftover beta-code / backticks /
broken entities, numbered sections not at a paragraph start, heading list, and the remaining differences vs CCEL
(which should all be deliberate print readings)."""
import collections, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

wd = os.path.abspath([x for x in sys.argv[1:] if not x.startswith('-')][0]); cfg = load_cfg(wd)
_pos = [x for x in sys.argv[1:] if not x.startswith('-')]
f = _pos[1] if len(_pos) > 1 else os.path.join(repo_root(), cfg['html'])
s = open(f).read(); body, notes = split_notes(s)
fail = []
refs = REF_RE.findall(body)
if any(not (a == b == c) for a, b, c in refs): fail.append('marker href/id/label mismatch')
rn = [int(r[1]) for r in refs]
if rn != list(range(1, len(rn) + 1)): fail.append(f'markers not 1..k in order (first bad near {next((i+1 for i,x in enumerate(rn) if x!=i+1), None)})')
defs = re.findall(r'<span id="fn(\d+)"><a href="#r(\d+)">(\d+)</a>&nbsp;', notes)
if any(not (a == b == c) for a, b, c in defs): fail.append('def id/href/label mismatch')
dn = [int(d[0]) for d in defs]
if dn != list(range(1, len(dn) + 1)): fail.append('defs not 1..k in order')
if len(rn) != len(dn): fail.append(f'{len(rn)} markers vs {len(dn)} defs')
if re.search('[\x00\x01¶]', s): fail.append('leftover placeholder (\\x00/\\x01/¶)')
bad_tags = set(re.findall(r'</?(\w+)', body)) - {'article', 'h1', 'h2', 'h3', 'h4', 'i', 'b', 'br', 'sup', 'a', 'em', 'section', 'hr', 'span', 'blockquote'}
if bad_tags: fail.append(f'unexpected tags in body: {bad_tags}')
bad_tags = set(re.findall(r'</?(\w+)', notes)) - {'section', 'hr', 'span', 'a', 'br', 'i', 'sup', 'b', 'article'}
if bad_tags: fail.append(f'unexpected tags in notes: {bad_tags}')
if s.count('<i>') != s.count('</i>'): fail.append(f"unbalanced <i>: {s.count('<i>')} vs {s.count('</i>')}")
if s.count('<span') != s.count('</span>'): fail.append('unbalanced <span>')

print('HARD CHECKS:', 'OK' if not fail else 'FAILED'); [print('  ✗', x) for x in fail]
print(f'markers {len(rn)}, notes {len(dn)}')
plain = html.unescape(re.sub(r'<[^>]+>', ' ', s))
soft = [plain[max(0, m.start() - 40):m.end() + 20].replace('\n', ' ') for m in
        re.finditer(r'\b[a-zA-Z]+[/\\=][a-zA-Z]+|\b[a-z]+0[a-z]+\b|`|&#|\b[a-z]\'[a-z]+[/\\=]', plain)]
print(f'possible beta-code / junk: {len(soft)}'); [print('  ?', repr(x)) for x in soft[:25]]
run = [m.group(0) for m in re.finditer(r'[a-z.?!"\']\d{1,3}\. [A-Z]|<i>\s*\d{1,3}\.</i>', body)]
print(f'possible run-in section numbers: {run}')
secnums = [int(x) for x in re.findall(r'(?:<br/?>\s*<br/?>|</h\d>)\s*(?:<i>)?\s*\n?(\d{1,3})\.(?:\s|<sup>)', body)]
print('section-number gaps:', [(a, b) for a, b in zip(secnums, secnums[1:]) if b != a + 1])
print('headings:', ' | '.join(re.sub(r'<[^>]+>', '', h).strip() for h in re.findall(r'<h\d>.*?</h\d>', body)))
B, _ = ccel_paragraphs(cfg['txt'])
r = diff_body(s, B)
if r:
    r['hunks'] = [h for h in r['hunks'] if not ((h['i1'] < 3 or h['i1'] >= r['ntok'] - 1) and len(h['ccel'].split()) > 25)]
    c = collections.Counter(h['cls'] for h in r['hunks'])
    print(f'remaining differences vs CCEL: {len(r["hunks"])} {dict(c)}  (should all be deliberate print readings)')
    if '-v' in sys.argv:
        for h in r['hunks']:
            print(f"  {h['cls'][:4]} {h['ours']!r} -> {h['ccel']!r}")
sys.exit(1 if fail else 0)
