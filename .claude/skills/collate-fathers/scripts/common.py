"""Shared helpers for the collate-fathers pipeline (CCEL fathers2-mirror texts vs CCEL + print scans)."""
import bisect, html, json, os, re, subprocess, difflib

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repo_root():
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()


def collate_root():
    return os.path.join(repo_root(), 'standardization', 'collate')


def load_cfg(wd):
    return json.load(open(os.path.join(wd, 'config.json')))


def save_json(obj, path):
    with open(path, 'w') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- our file

NOTES_OPEN = '<section class="notes">'


def split_notes(s):
    k = s.find(NOTES_OPEN)
    return (s, '') if k < 0 else (s[:k], s[k:])


REF_RE = re.compile(r'<sup><a href="#fn(\d+)" id="r(\d+)">(\d+)</a></sup>')
DEF_RE = re.compile(r'<span id="fn(\d+)"><a href="#r\d+">\d+</a>&nbsp;(.*?)</span>', re.S)


def our_tokens(s):
    """Visible body tokens as (text, start, end) raw offsets. Footnote <sup>s and non-inline tags act as spaces;
    <i>/<b>/<em> are transparent; entities are decoded."""
    stop = s.find(NOTES_OPEN)
    if stop < 0:
        stop = len(s)
    vis, src, i = [], [], 0
    while i < stop:
        if s.startswith('<sup>', i):
            i = s.index('</sup>', i) + 6
            vis.append(' '); src.append(-1); continue
        if s[i] == '<':
            j = s.index('>', i) + 1
            if not re.match(r'</?(i|b|em)>', s[i:j]):
                vis.append(' '); src.append(-1)
            i = j; continue
        if s[i] == '&':
            m = re.match(r'&[#\w]+;', s[i:i + 12])
            if m:
                vis.append(html.unescape(m.group())); src.append(i); i += len(m.group()); continue
        vis.append(s[i]); src.append(i); i += 1
    V = ''.join(vis)
    return [(m.group(), src[m.start()], src[m.end() - 1] + 1) for m in re.finditer(r'\S+', V)]


def norm_with_map(raw):
    """Lower-case ASCII letters only, with a map from normalized index -> raw offset. Tags and <sup>…</sup> skipped,
    entities decoded."""
    out, mp, i, n = [], [], 0, len(raw)
    while i < n:
        c = raw[i]
        if raw.startswith('<sup>', i):
            i = raw.index('</sup>', i) + 6; continue
        if c == '<':
            i = raw.index('>', i) + 1; continue
        if c == '&':
            m = re.match(r'&[#\w]+;', raw[i:i + 12])
            if m:
                d = html.unescape(m.group()).lower()
                if 'a' <= d <= 'z':
                    out.append(d); mp.append(i)
                i += len(m.group()); continue
        lc = c.lower()
        if 'a' <= lc <= 'z':
            out.append(lc); mp.append(i)
        i += 1
    return ''.join(out), mp


def norm(t):
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).lower()
    return re.sub(r'[^a-z]', '', t)


def plain_note(t):
    t = re.sub(r'<[^>]+>', '', t)
    t = html.unescape(t).replace('—', '-').replace('--', '-')
    t = t.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    return re.sub(r'\s+', '', t)


def br_style(s):
    return '<br/>' if s.count('<br/>') >= s.count('<br>') else '<br>'


# ---------------------------------------------------------------- CCEL plain text

def ccel_paragraphs(txt_path):
    """CCEL volume .txt with footnote blocks removed -> (tokens, set of paragraph-start token indexes)."""
    t = open(txt_path, encoding='utf-8', errors='replace').read()
    blocks = re.split(r'\n\s*_{10,}\s*\n', t)
    cb = ' \n'.join(b for b in blocks if not re.match(r'\s*\[\d+\]', b))
    cb = re.sub(r'\[\d+\]', '', cb)
    B, starts = [], set()
    for para in re.split(r'\n\s*\n', cb):
        ws = [w for w in re.findall(r'\S+', para) if not re.fullmatch(r'-{3,}|_{3,}|\*+', w)]
        if ws:
            starts.add(len(B)); B.extend(ws)
    return B, starts


def locate(a, B, n=8):
    """Find where our token list `a` starts/ends inside CCEL tokens B via unique n-gram anchors."""
    Bs = ' '.join(B)
    offs, c = [], 0
    for w in B:
        offs.append(c); c += len(w) + 1

    def find(it):
        for i in it:
            g = ' '.join(a[i:i + n])
            k = Bs.find(' ' + g + ' ')
            if k >= 0 and Bs.find(' ' + g + ' ', k + 1) < 0:
                return i, bisect.bisect_left(offs, k + 1)
        return None
    st = find(range(min(40, max(0, len(a) - n - 1)), min(len(a) - n, 3000)))
    en = find(range(len(a) - n, max(0, len(a) - 3000), -1))
    return st, en


def words(t):
    return re.findall(r'[A-Za-zÀ-ÿæœÆŒ]+', t)


def classify(ours, cc):
    o = ours.replace('—', '--')
    if o == cc:
        return 'same'
    if o.lower() == cc.lower():
        return 'case'
    if '..' in ours or '..' in cc or '. .' in ours:
        return 'review'          # CCEL compresses the print's spaced ". . ." -- never auto
    alt = re.sub(r'\s+-\s*|\s*-\s+', '-', ours).replace('-', '--')
    if alt == cc:
        return 'dash'
    if ' ' not in ours and ours == cc.replace(' ', '') and '--' not in cc:
        return 'split'
    if ours.replace(' ', '') == cc.replace(' ', '').replace('--', '-'):
        # spacing-only; auto only if CCEL does not glue two of our words together
        return 'spacing' if len(words(cc)) >= len(words(ours)) else 'review'
    return 'review'


AUTO = {'dash', 'split', 'spacing'}


def diff_body(s, B):
    toks = our_tokens(s)
    a = [t[0] for t in toks]
    st, en = locate(a, B)
    if not st or not en or not (0 <= st[1] - st[0] < en[1]):
        return None
    bi0 = max(0, st[1] - st[0] - 50)
    bi1 = min(len(B), en[1] + (len(a) - en[0]) + 50)
    b = B[bi0:bi1]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    hunks, amap = [], {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            amap[bi0 + blk.b + k] = blk.a + k
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        ours, cc = ' '.join(a[i1:i2]), ' '.join(b[j1:j2])
        cls = classify(ours, cc)
        if cls == 'same':
            continue
        hunks.append(dict(id=f'{i1}:{i2}', op=op, i1=i1, i2=i2, ours=ours, ccel=cc, cls=cls,
                          ctx_ours=' '.join(a[max(0, i1 - 12):i1]) + ' [[' + ours + ']] ' + ' '.join(a[i2:i2 + 12]),
                          ctx_ccel=' '.join(b[max(0, j1 - 12):j1]) + ' [[' + cc + ']] ' + ' '.join(b[j2:j2 + 12])))
    return dict(ntok=len(a), bspan=[bi0, bi1], hunks=hunks, amap=amap)


# ---------------------------------------------------------------- ThML

def esc_keep(t, keep=r'</?i>|</?sup>|<br>'):
    parts = re.split('(' + keep + ')', t)
    return ''.join(p if re.fullmatch(keep, p) else html.escape(p, quote=False) for p in parts)


def thml_clean(t):
    t = re.sub(r'</?(scripRef|span|p|a|abbr|name|unclear|foreign|term|added|div\d?)\b[^>]*>', '', t)
    t = re.sub(r'<br\s*/?>', ' ', t)
    t = re.sub(r'<i>(\s+)', r'\1<i>', t); t = re.sub(r'(\s+)</i>', r'</i>\1', t)
    t = re.sub(r'<(?!/?(i|sup)>)[^>]+>', '', t)   # drop any other markup
    t = html.unescape(t)
    t = t.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('–', '-')
    t = re.sub(r'\s+', ' ', t).strip()
    return esc_keep(t)


def thml_notes(xml):
    """[(n, html_text, start_offset_in_xml, end_offset)] ; multi-<p> notes joined with <br>."""
    out = []
    for m in re.finditer(r'<note\b[^>]*\bn="(\d+)"[^>]*>([\s\S]*?)</note>', xml):
        paras = [p for p in re.split(r'<p\b[^>]*>', m.group(2)) if re.sub(r'<[^>]+>|\s', '', p)]
        txt = '<br>'.join(thml_clean(p) for p in paras)
        out.append((int(m.group(1)), txt, m.start(), m.end()))
    return out


def thml_plain_with_notes(xml):
    """Normalized ThML text (notes removed) + list of (note_n, offset_in_plain)."""
    parts, offs, pos, L = [], [], 0, 0
    for m in re.finditer(r'<note\b[^>]*\bn="(\d+)"[^>]*>[\s\S]*?</note>', xml):
        p = norm(xml[pos:m.start()]); parts.append(p); L += len(p)
        offs.append((int(m.group(1)), L)); pos = m.end()
    parts.append(norm(xml[pos:]))
    return ''.join(parts), offs
