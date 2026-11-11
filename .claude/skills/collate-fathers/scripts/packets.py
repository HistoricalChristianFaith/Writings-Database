#!/usr/bin/env python3
"""packets.py <wd> [N]  -- split review items (non-auto body hunks + differing/missing notes) into N packets
<wd>/packets/p{K}.json by position in the work, and write the adjudication brief <wd>/packets/BRIEF.md."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

wd = os.path.abspath(sys.argv[1]); N = int(sys.argv[2]) if len(sys.argv) > 2 else 0
cfg = load_cfg(wd); an = json.load(open(os.path.join(wd, 'analysis.json')))
ntok = an['ntok']


def skip(h):
    if h['cls'] in AUTO:
        return True
    if re.fullmatch(r'[IVXLC]+', h['ours']) and h['ccel'] == h['ours'] + '.':
        return True                                   # heading-style period only
    edge = h['i1'] < 3 or h['i1'] >= ntok - 1
    if edge and len(h['ccel'].split()) > 25:
        return True                                   # CCEL text outside our work (intro / next work)
    return False


body = [dict(id=h['id'], tok=h['i1'], ours=h['ours'], ccel=h['ccel'], ctx_ours=h['ctx_ours'], ctx_ccel=h['ctx_ccel'])
        for h in an['hunks'] if not skip(h)]
notes = []
for it in an['notes'].get('items', []):
    d = dict(key=it['key'], tok=it['tok'], thml_n=it['thml_n'], kind=it['kind'], ours=it['ours'], thml=it['thml'])
    if it['marker_missing']:
        d['marker_missing'] = True; d['thml_ctx'] = it['thml_ctx']
    notes.append(d)
total = len(body) + len(notes)
if not N:
    N = max(1, min(6, round(total / 110)))
items = sorted([('b', x['tok'], x) for x in body] + [('n', x['tok'], x) for x in notes], key=lambda t: t[1])
per = -(-len(items) // N) if items else 0
pk = os.path.join(wd, 'packets'); os.makedirs(pk, exist_ok=True)
lo, hi = cfg['leaf_lo'], cfg['leaf_hi']
summary = []
for k in range(N):
    chunk = items[k * per:(k + 1) * per]
    if not chunk:
        continue
    t0, t1 = chunk[0][1], chunk[-1][1]
    l0 = max(lo, int(lo + (hi - lo) * t0 / max(1, ntok)) - 2); l1 = min(hi, int(lo + (hi - lo) * t1 / max(1, ntok)) + 2)
    p = dict(leaves=f'n{l0}-n{l1} (estimate)', body=[x for t, _, x in chunk if t == 'b'], notes=[x for t, _, x in chunk if t == 'n'])
    save_json(p, os.path.join(pk, f'p{k + 1}.json'))
    summary.append(f'p{k + 1}: {len(p["body"])} body, {len(p["notes"])} notes, leaves {p["leaves"]}')
brief = open(os.path.join(SKILL, 'BRIEF.md')).read()
extra = ', '.join(cfg.get('extra_ocr', [])) or '(none)'
brief = (brief.replace('{WD}', wd).replace('{SCRIPTS}', os.path.join(SKILL, 'scripts')).replace('{SCAN}', cfg['scan'])
         .replace('{EXTRA_OCR}', extra).replace('{HTML}', os.path.join(repo_root(), cfg['html'])).replace('{VOL}', cfg['vol']))
open(os.path.join(pk, 'BRIEF.md'), 'w').write(brief)
print(f'{len(body)} body items, {len(notes)} note items -> {len(summary)} packets'); print('\n'.join(summary))
