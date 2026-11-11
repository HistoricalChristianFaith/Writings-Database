#!/usr/bin/env python3
"""analyze.py <workdir>

Diffs orig.html against the CCEL volume text, aligns footnotes against ThML (markers by context, definitions by
text), checks paragraph breaks / numbered sections / headings / leftover beta-code, and writes analysis.json.
Prints a human summary."""
import bisect, collections, difflib, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

wd = os.path.abspath(sys.argv[1])
cfg = load_cfg(wd)
s = open(os.path.join(wd, 'orig.html')).read()
body, notes = split_notes(s)
B, cstarts = ccel_paragraphs(cfg['txt'])

# ------------------------------------------------------------------ body diff
r = diff_body(s, B)
if r is None:
    sys.exit('could not anchor the work inside the CCEL volume text')
toks = our_tokens(s)
a = [t[0] for t in toks]
tstarts = [t[1] for t in toks]
hunks = r['hunks']
cnt = collections.Counter(h['cls'] for h in hunks)

# ------------------------------------------------------------------ paragraph breaks
b0, b1 = r['bspan']
amap = {int(k): v for k, v in r['amap'].items()}
ourstarts = set()
for i, (w, st, en) in enumerate(toks):
    pre = re.sub(r'<sup>.*?</sup>', '', s[max(0, st - 400):st])
    if re.search(r'(<br/?>\s*<br/?>|</h\d>|<article[^>]*>|<h\d>)\s*(<i>|<b>)?\s*$', pre):
        ourstarts.add(i)
mapped_cstarts = {amap[j] for j in cstarts if b0 <= j < b1 and j in amap}
para_missing = [dict(tok=i, ctx=' '.join(a[max(0, i - 8):i]) + ' ¦ ' + ' '.join(a[i:i + 8]))
                for i in sorted(mapped_cstarts - ourstarts)]
_mapped = set(amap.values())
para_extra = [dict(tok=i, ctx=' '.join(a[max(0, i - 8):i]) + ' ¦ ' + ' '.join(a[i:i + 8]))
              for i in sorted(ourstarts - mapped_cstarts) if i in _mapped and i > 0
              and not re.search(r'</h\d>\s*(<i>|<b>)?\s*$', s[max(0, toks[i][1] - 60):toks[i][1]])
              and not re.search(r'<h\d>\s*$', s[max(0, toks[i][1] - 10):toks[i][1]])]

# numbered sections that are not at a paragraph start (run-ins like 'us.3. Lately', '<i> 44.</i>')
runins = []
for m in re.finditer(r'(?<![\w#;&/,-])(?<!\d)(\d{1,3})\.(?=\s|<sup>|$|[A-Z])', body):
    st = m.start()
    pre = re.sub(r'<sup>.*?</sup>', '', body[max(0, st - 200):st])
    nxt = body[m.end():m.end() + 30]
    at_start = re.search(r'(<br/?>\s*<br/?>|</h\d>)\s*(<i>|<b>)?\s*$', pre)
    looks_section = re.match(r'(\s|<sup>.*?</sup>\s*)*(<i>|<b>)?["\'(]?[A-Z]', nxt) or re.search(r'<i>\s*$', pre) or nxt.startswith('</i>')
    prev_char = re.sub(r'<[^>]+>', '', pre).rstrip()[-1:] if re.sub(r'<[^>]+>', '', pre).strip() else ''
    if not at_start and looks_section and prev_char in '.?!"\'’”:;)' :
        runins.append(dict(n=int(m.group(1)), ctx=re.sub(r'\s+', ' ', body[max(0, st - 80):m.end() + 40])))
secnums = [int(x) for x in re.findall(r'(?:<br/?>\s*<br/?>|</h\d>)\s*(?:<i>)?\s*\n?(\d{1,3})\.(?:\s|<sup>)', body)]
sec_gaps = [(x, y) for x, y in zip(secnums, secnums[1:]) if y != x + 1]

# headings in the CCEL span that ours lacks as <h*>
ccel_txt_span = ' '.join(B[b0:b1])
our_heads = [norm(h) for h in re.findall(r'<h\d>(.*?)</h\d>', body, re.S)]
missing_heads = []
for m in re.finditer(r'\b(Chapter|CHAPTER|Book|BOOK|Homily|HOMILY|Section|Letter|LETTER|Epistle|Part|PART)\s+([IVXLC]+|\d+)\.?', ccel_txt_span):
    h = norm(m.group(0))
    if h not in our_heads:
        ctx = ccel_txt_span[max(0, m.start() - 60):m.end() + 60]
        # only report if it looks like a standalone heading in CCEL (preceded by sentence end)
        if re.search(r'[.?!"]\s*$', ccel_txt_span[max(0, m.start() - 3):m.start()]) or m.start() < 5:
            missing_heads.append(dict(heading=m.group(0), ccel_ctx=ctx))

# leftover beta-code / OCR junk
plain = html.unescape(re.sub(r'<[^>]+>', ' ', s))
beta = [plain[max(0, m.start() - 40):m.end() + 20] for m in
        re.finditer(r'\b[a-zA-Z]+[/\\=][a-zA-Z]+|\b[a-z]+0[a-z]+\b|\b[a-z]\'[a-z]+[/\\=]|`|&amp;#', plain)]

# ------------------------------------------------------------------ footnotes
x = open(cfg['xml'], encoding='utf-8', errors='replace').read()
TH = thml_notes(x)                       # [(n, text, xs, xe)]
TP, toffs = thml_plain_with_notes(x)     # plain, [(n, off)] same order as TH
assert len(toffs) == len(TH)
OP, omap = norm_with_map(body)

def anchor(fromstart):
    rng = range(0, max(1, len(OP) - 80), 50) if fromstart else range(max(0, len(OP) - 80), 0, -50)
    for k in rng:
        g = OP[k:k + 60]
        p = TP.find(g)
        if p >= 0 and TP.find(g, p + 1) < 0:
            return k, p
    return None
A1, A2 = anchor(True), anchor(False)
notes_info = dict(available=bool(A1 and A2))
refs = [(int(m.group(2)), m.start()) for m in REF_RE.finditer(body)]
defs = [(int(m.group(1)), m.group(2).strip()) for m in DEF_RE.finditer(notes)]
if A1 and A2:
    tp_lo = A1[1] - A1[0] - 50
    tp_hi = A2[1] + (len(OP) - A2[0]) + 50
    rng = [i for i, (n, off) in enumerate(toffs) if tp_lo <= off <= tp_hi]
    th_lo, th_hi = (rng[0], rng[-1]) if rng else (0, -1)
    TIDX = list(range(th_lo, th_hi + 1))
    toff = [toffs[i][1] for i in TIDX]
    # --- markers -> ThML by context
    refmap, last, lasto = [], A1[1] - A1[0], 0
    for rn, raw in refs:
        o = bisect.bisect_left(omap, raw)
        exp = last + (o - lasto); found = None
        for L in (30, 20, 12):
            ctx = OP[max(0, o - L):o]
            if len(ctx) < 6: break
            k = TP.find(ctx, max(0, exp - 4000), exp + 4000)
            if k >= 0:
                found = k + len(ctx); break
        if found is None or not toff:
            refmap.append([rn, None, None]); continue
        last, lasto = found, o
        q = min(range(len(toff)), key=lambda q: abs(toff[q] - found))
        refmap.append([rn, TIDX[q], toff[q] - found])
    # repair: keep the longest increasing run of confident matches as anchors, then fill the gaps
    flags = []
    conf = [(i, m[1]) for i, m in enumerate(refmap) if m[1] is not None and abs(m[2]) <= 3]
    import bisect as _b
    tails, tidx, prevp = [], [], [-1] * len(conf)
    for k, (i, t) in enumerate(conf):
        p = _b.bisect_left(tails, t)
        if p == len(tails): tails.append(t); tidx.append(k)
        else: tails[p] = t; tidx[p] = k
        prevp[k] = tidx[p - 1] if p else -1
    lis, k = [], tidx[-1] if tidx else -1
    while k >= 0:
        lis.append(conf[k]); k = prevp[k]
    lis.reverse()
    tl = [None] * len(refmap)
    for i, t in lis: tl[i] = t
    bounds = [(-1, th_lo - 1)] + lis + [(len(refmap), th_hi + 1)]
    for (ia, ta), (ib, tb) in zip(bounds, bounds[1:]):
        between = list(range(ia + 1, ib))
        if not between: continue
        slots = tb - ta - 1
        if len(between) == slots:
            for j, i in enumerate(between): tl[i] = ta + 1 + j
            continue
        cur = ta
        for j, i in enumerate(between):
            own = refmap[i][1]
            remaining = len(between) - j - 1
            if own is not None and cur < own < tb - remaining:
                tl[i] = own
            elif cur + 1 < tb - remaining:
                tl[i] = cur + 1
            else:
                flags.append(refmap[i][0]); continue
            cur = tl[i]
        if len(between) != slots:
            flags.extend([refmap[i][0] for i in between if refmap[i][1] is None or abs(refmap[i][2] or 99) > 3])
    flags = sorted(set(flags))
    refmap = [[m[0], t] for m, t in zip(refmap, tl)]
    have = {t for t in tl if t is not None}
    missing_markers = [i for i in TIDX if i not in have]
    # --- definitions -> ThML by text
    op = [plain_note(t) for n, t in defs]
    tp = [plain_note(TH[i][1]) for i in TIDX]
    sm = difflib.SequenceMatcher(None, op, tp, autojunk=False)
    defmap, auto = {}, set()
    for tag, i1, i2, k1, k2 in sm.get_opcodes():
        if tag == 'equal':
            for d in range(i2 - i1):
                defmap[defs[i1 + d][0]] = TIDX[k1 + d]; auto.add(defs[i1 + d][0])
        elif tag == 'replace' and i2 - i1 == k2 - k1:
            for d in range(i2 - i1):
                defmap[defs[i1 + d][0]] = TIDX[k1 + d]
        elif tag == 'replace':
            # unequal block: monotonic best pairing by similarity
            O, T = list(range(i1, i2)), list(range(k1, k2))
            dp = [[0.0] * (len(T) + 1) for _ in range(len(O) + 1)]
            for p in range(1, len(O) + 1):
                for q in range(1, len(T) + 1):
                    rt = difflib.SequenceMatcher(None, op[O[p - 1]], tp[T[q - 1]]).ratio()
                    dp[p][q] = max(dp[p - 1][q], dp[p][q - 1], dp[p - 1][q - 1] + (rt if rt > 0.4 else -1))
            p, q = len(O), len(T)
            while p and q:
                rt = difflib.SequenceMatcher(None, op[O[p - 1]], tp[T[q - 1]]).ratio()
                if rt > 0.4 and abs(dp[p][q] - (dp[p - 1][q - 1] + rt)) < 1e-9:
                    defmap[defs[O[p - 1]][0]] = TIDX[T[q - 1]]; p -= 1; q -= 1
                elif dp[p][q] == dp[p - 1][q]:
                    p -= 1
                else:
                    q -= 1
    inv = {t: d for d, t in defmap.items()}
    ours_only = [d for d, t in defs if d not in defmap]
    thml_only = [i for i in TIDX if i not in inv]
    refpos = {rn: raw for rn, raw in refs}
    ref_by_ti = {t: rn for rn, t in refmap if t is not None}
    misnumbered = sum(1 for rn, t in refmap if t is not None and defmap.get(rn) != t)
    # note items for review (everything not auto)
    items = []
    for ti in TIDX:
        d = inv.get(ti)
        if d in auto:
            continue
        rn = ref_by_ti.get(ti)
        tok = bisect.bisect_left(tstarts, refpos[rn]) if rn else None
        if tok is None:
            # missing marker: estimate position from neighbours
            prev = [bisect.bisect_left(tstarts, refpos[ref_by_ti[t]]) for t in range(ti - 1, th_lo - 1, -1) if t in ref_by_ti][:1]
            tok = prev[0] if prev else 0
        items.append(dict(key=f't{ti}', thml_n=TH[ti][0], our_def=d, marker=rn, tok=tok,
                          kind='pair' if d is not None else 'thml-only',
                          ours=dict(defs).get(d, '') if d is not None else '', thml=TH[ti][1],
                          marker_missing=rn is None,
                          thml_ctx=re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', re.sub(r'<note[\s\S]*?</note>', '[N]', x[max(0, TH[ti][2] - 300):TH[ti][2]])))[-140:]))
    notes_info.update(th_lo=th_lo, th_hi=th_hi, thml_count=len(TIDX), our_refs=len(refs), our_defs=len(defs),
                      refmap=refmap, unresolved_refs=flags, missing_markers=missing_markers,
                      defmap=defmap, auto=sorted(auto), ours_only=ours_only, thml_only=thml_only,
                      misnumbered=misnumbered, items=items)

out = dict(ntok=r['ntok'], bspan=r['bspan'], hunks=hunks, para_missing=para_missing, para_extra=para_extra,
           runins=runins, sec_gaps=sec_gaps, missing_heads=missing_heads, beta=beta, notes=notes_info)
save_json(out, os.path.join(wd, 'analysis.json'))

# ------------------------------------------------------------------ summary
print(f"BODY  {r['ntok']} tokens, {len(hunks)} hunks vs CCEL: {dict(cnt)}")
print(f"      auto-applicable: {sum(1 for h in hunks if h['cls'] in AUTO)}   to review: {sum(1 for h in hunks if h['cls'] not in AUTO)}")
print(f"PARAS CCEL breaks missing in ours: {len(para_missing)}   ours-only breaks: {len(para_extra)}")
for p in para_missing[:15]: print('      missing ¦', p['ctx'])
print(f"      numbered sections run in: {len(runins)}  gaps in section numbering: {sec_gaps}")
for p in runins[:15]: print('      run-in', p['n'], '::', p['ctx'])
print(f"HEADS CCEL headings not found as <h*> in ours: {len(missing_heads)}")
for h in missing_heads[:15]: print('      ', h['heading'], '::', h['ccel_ctx'])
print(f"BETA  leftover beta-code/OCR-junk spots: {len(beta)}")
for b_ in beta[:10]: print('      ', repr(b_))
n = notes_info
if not n['available']:
    print('NOTES could not anchor the work in ThML -- notes not analyzed')
else:
    print(f"NOTES ThML notes in range: {n['thml_count']} (ThML n={TH[n['th_lo']][0]}..{TH[n['th_hi']][0]})   ours: {n['our_refs']} markers / {n['our_defs']} defs")
    print(f"      defs identical to ThML (plain text): {len(n['auto'])}   differing: {sum(1 for i in n['items'] if i['kind']=='pair')}")
    print(f"      ThML notes with no def in ours: {len(n['thml_only'])}   our defs matching no ThML note: {n['ours_only']}")
    print(f"      ThML notes with no marker in ours: {len(n['missing_markers'])}   unresolved markers: {n['unresolved_refs']}")
    print(f"      MARKERS POINTING AT THE WRONG DEF (drift): {n['misnumbered']}")
    for ti in n['missing_markers'][:10]:
        c = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', re.sub(r'<note[\s\S]*?</note>', '[N]', x[max(0, TH[ti][2] - 400):TH[ti][2]])))
        print('      no marker for ThML', TH[ti][0], '::', c[-90:], '||', TH[ti][1][:60])
