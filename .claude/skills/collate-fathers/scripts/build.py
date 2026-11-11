#!/usr/bin/env python3
"""build.py <wd> <out.html>

Deterministically rebuilds the work from <wd>/orig.html + <wd>/merged.json:
  1. body: auto hunks (dash/split/spacing) -> CCEL; reviewed hunks -> decision; `¶` -> paragraph break.
     Hunks whose span crosses markup are NOT applied; they are listed in <wd>/manual.json for hand-fixing.
  2. footnotes (if the work's notes were aligned to ThML): every ThML note in range becomes a note, in print order;
     markers are kept where they map, missing markers are re-inserted by ThML context (or merged.json "markers"
     {"tNNN": "<regex>"} -> insert after the unique match); text = ThML for identical notes, else the decision.
     Notes are renumbered 1..k in document order.
  3. hand fixes: merged.json "hand": [{"old": str, "new": str, "count": 1, "regex": false}] applied last (exact
     string replace on the built file, asserting the match count) -- record every manual/structural fix here
     instead of editing the file, so the build stays reproducible.
Run it again after changing merged.json — it always starts from orig.html."""
import bisect, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

wd = os.path.abspath(sys.argv[1]); out_path = sys.argv[2]
cfg = load_cfg(wd); an = json.load(open(os.path.join(wd, 'analysis.json')))
M = json.load(open(os.path.join(wd, 'merged.json')))
bdec, ndec, mk = M.get('body', {}), M.get('notes', {}), M.get('markers', {})
s = open(os.path.join(wd, 'orig.html')).read()
BR = br_style(s)

# ------------------------------------------------------------------ body
toks = our_tokens(s)
assert len(toks) == an['ntok'], 'orig.html changed since analyze'
edits, manual = [], []
for h in an['hunks']:
    d = bdec.get(h['id'])
    if d is None:
        d = 'ccel' if h['cls'] in AUTO else 'ours'
    if d == 'ours':
        continue
    new = h['ccel'] if d == 'ccel' else d
    new = html.escape(new.replace('--', '—'), quote=False)
    new = new.replace('¶', BR + BR + '\n')
    if h['i1'] == h['i2']:
        if h['i1'] == 0 or h['i1'] >= len(toks):
            continue
        p = toks[h['i1'] - 1][2]; edits.append((p, p, ' ' + new)); continue
    st, en = toks[h['i1']][1], toks[h['i2'] - 1][2]
    old = s[st:en]
    if '<' in old:
        manual.append(dict(id=h['id'], old=old, new=new, ctx=h['ctx_ours'])); continue
    edits.append((st, en, new))
for st, en, new in sorted(edits, reverse=True):
    s = s[:st] + new + s[en:]
s = re.sub(r'(</sup>) —', r'\1—', s)
s = re.sub(r'(?<=\S)  +(?=\S)', ' ', s)
save_json(manual, os.path.join(wd, 'manual.json'))
print(f'body: {len(edits)} edits applied, {len(manual)} need hand-fixing (manual.json)')
for m_ in manual:
    print('   MANUAL', m_['id'], repr(m_['old']), '->', repr(m_['new']))

# ------------------------------------------------------------------ notes
N = an['notes']
if N.get('available') and N.get('thml_count'):
    x = open(cfg['xml'], encoding='utf-8', errors='replace').read()
    TH = thml_notes(x)
    TP, toffs = thml_plain_with_notes(x)
    lo, hi = N['th_lo'], N['th_hi']
    body, notes = split_notes(s)
    ourdefs = {int(m.group(1)): m.group(2).strip() for m in DEF_RE.finditer(notes)}
    defmap = {int(k): v for k, v in N['defmap'].items()}
    inv = {t: d for d, t in defmap.items()}
    auto = set(N['auto'])
    TEXT, problems = {}, []
    for ti in range(lo, hi + 1):
        d = inv.get(ti); key = f't{ti}'
        if d in auto:
            TEXT[ti] = TH[ti][1]; continue
        v = ndec.get(key)
        if v is None:
            problems.append(f'no decision for note {key}'); v = 'thml' if d is None else 'ours'
        if v == 'thml':
            TEXT[ti] = TH[ti][1]
        elif v == 'ours':
            TEXT[ti] = ourdefs.get(d, '') if d is not None else TH[ti][1]
        else:
            t = esc_keep(v)
            if '<br>' in TH[ti][1] and '<br>' not in t:      # restore paragraph breaks in long notes
                for para in TH[ti][1].split('<br>')[1:]:
                    key2 = re.sub(r'<[^>]+>', '', para)
                    for L in (18, 12, 8):
                        hits = [m_.start() for m_ in re.finditer(re.escape(key2[:L]), t)] if len(key2) >= L else []
                        if len(hits) == 1:
                            t = t[:hits[0]].rstrip() + '<br>' + t[hits[0]:]; break
            TEXT[ti] = t
    dropped = [d for d in N['ours_only'] if ourdefs.get(d, '').strip()]
    if dropped:
        problems.append(f'our defs with no ThML counterpart would be dropped: {dropped} -- handle by hand')
    # markers: original ref number -> ThML index
    rm = {r: t for r, t in N['refmap'] if t is not None}
    def subref(m):
        rn = int(m.group(2))
        return '\x00%d\x00' % rm[rn] if rn in rm else '\x01%d\x01' % rn
    body = REF_RE.sub(subref, body)
    if '\x01' in body:
        problems.append('unmapped markers left in place: ' + str(re.findall(r'\x01(\d+)\x01', body)))
    # insert missing markers
    for ti in N['missing_markers']:
        key = f't{ti}'
        if key in mk:
            ms = list(re.finditer(mk[key], body))
            if len(ms) != 1:
                problems.append(f'marker regex for {key} matched {len(ms)} times'); continue
            pos = ms[0].end()
        else:
            OPb, omap = norm_with_map(body)
            # neighbours' positions in body
            def pos_of(t):
                m_ = re.search('\x00%d\x00' % t, body); return m_.start() if m_ else None
            prevs = [pos_of(t) for t in range(ti - 1, lo - 1, -1)]
            prevp = next((p for p in prevs if p is not None), 0)
            nexts = [pos_of(t) for t in range(ti + 1, hi + 1)]
            nextp = next((p for p in nexts if p is not None), len(body))
            o0, o1 = bisect.bisect_left(omap, prevp), bisect.bisect_left(omap, nextp)
            noff = toffs[ti][1]; pos = None
            for L in (40, 28, 18, 12):
                ctx = TP[max(0, noff - L):noff]
                w0 = max(0, o0 - L)
                hits = [w0 + m_.end() for m_ in re.finditer(re.escape(ctx), OPb[w0:o1]) if w0 + m_.end() > o0]
                if len(hits) == 1:
                    pos = omap[hits[0] - 1] + 1; break
            if pos is None:
                problems.append(f'could not place missing marker {key} (ThML n={TH[ti][0]}); add merged.json markers["{key}"] = regex'); continue
            # move past closing punctuation / quotes / italics end
            m_ = re.match(r'(?:</i>|[.,;:?!"\'’”)\]])*', body[pos:])
            pos += m_.end()
        body = body[:pos] + '\x00%d\x00' % ti + body[pos:]
    order = [int(v) for v in re.findall(r'\x00(\d+)\x00', body)]
    if order != sorted(order) or len(set(order)) != len(order):
        bad = [(a_, b_) for a_, b_ in zip(order, order[1:]) if b_ <= a_][:5]
        problems.append(f'marker order not monotonic near ThML idx {bad}')
    present = [t for t in range(lo, hi + 1) if t in set(order)]
    num = {t: k + 1 for k, t in enumerate(present)}
    body = re.sub(r'\x00(\d+)\x00', lambda m_: '<sup><a href="#fn{0}" id="r{0}">{0}</a></sup>'.format(num[int(m_.group(1))]), body)
    body = re.sub(r'\x01(\d+)\x01', lambda m_: f'<sup><a href="#fn{m_.group(1)}" id="r{m_.group(1)}">{m_.group(1)}</a></sup>', body)
    # rebuild notes section in the file's own style
    first = notes.find('<span id="fn')
    prefix = notes[:first] if first >= 0 else NOTES_OPEN + '\n<hr>\n'
    lastspan = notes.rfind('</span>')
    tail = notes[lastspan + len('</span>'):] if lastspan >= 0 else '\n</section>\n</article>\n'
    sep_m = re.search(r'</span>(\s*<br/?>\s*)<span id="fn', notes)
    sep = sep_m.group(1) if sep_m else BR + '\n'
    trail_m = re.match(r'\s*<br/?>\s*', tail)
    trail = trail_m.group(0) if trail_m else ''
    tail = tail[len(trail):]
    inner_end = '\n' if re.search(r'\n</span>', notes) else ''
    spans = [f'<span id="fn{num[t]}"><a href="#r{num[t]}">{num[t]}</a>&nbsp;{TEXT[t]}{inner_end}</span>' for t in present]
    notes = prefix + sep.join(spans) + trail + tail
    s = body + notes
    missing_text = [t for t in range(lo, hi + 1) if t not in set(order)]
    print(f'notes: {len(present)} notes rebuilt in print order' + (f'; ThML notes with no marker (omitted): {[TH[t][0] for t in missing_text]}' if missing_text else ''))
    for p in problems:
        print('   PROBLEM', p)
    save_json(problems, os.path.join(wd, 'build_problems.json'))
# ------------------------------------------------------------------ hand fixes (replayed every build)
hand_fail = []
for h in M.get('hand', []):
    n = h.get('count', 1)
    if h.get('regex'):
        s2, k = re.subn(h['old'], h['new'], s)
    else:
        k = s.count(h['old']); s2 = s.replace(h['old'], h['new'])
    if k != n:
        hand_fail.append(f"hand fix matched {k}x (expected {n}): {h['old'][:80]!r}"); continue
    s = s2
print(f"hand fixes: {len(M.get('hand', [])) - len(hand_fail)} applied" + (f", {len(hand_fail)} FAILED" if hand_fail else ''))
for x in hand_fail:
    print('   PROBLEM', x)
open(out_path, 'w').write(s)
print('wrote', out_path)
