# Type-01 files needing a CCEL content re-source pass

_Generated 2026-09-18. Updated 2026-09-18: the **15** files whose missing notes were
un-mirrored `footnote/fnNN.htm` refs have been **RECOVERED** — their note text was
re-sourced and injected, and each now passes `standardization/tools/ccel_mirror_transform.py`
(footnote-balanced + visible-text-validated) with no gate weakened._

_**Updated 2026-09-18 (second pass): the final 17 are now ALSO RECOVERED.** Both remaining
sub-forms — 16 dangling-in-page-anchor files and 1 sibling-page file — were re-sourced with the
same method (extended tooling: `resource_footnotes_v2.py`). For the dangling-anchor files the
complete tertullian.org / Wayback source page still carries the same anchors as `footnote/fnNN.htm`
refs, which maps each anchor to its footnote page; the sibling-page file's notes came from the named
NPNF endnotes page. All 32 type-01 content-missing files are now recovered; **0 remain open.**_

**This is a content-recovery job, not a transform bug.** The note text is re-sourced from the
same 2004 HTTrack tree CCEL later dropped: Roger Pearse's mirror at
`www.tertullian.org/fathers2/<VOL>/footnote/fnNN.htm`, with the archive.org Wayback snapshot of
`www.ccel.org/fathers2/...` as a per-page fallback where tertullian's copy is truncated (e.g.
ANF-07 `fn68`). Do **not** relax the footnote-balance assertion to force any file through. See
`standardization/pilot/reports/_failure-triage.md` for the full triage.

Reference forms:
- **un-mirrored `footnote/` refs** — `href="footnote/fnNN.htm#…"`; the `footnote/` directory was
  never mirrored locally. **→ RECOVERED** (re-sourced from tertullian.org / Wayback).
- **sibling-page refs** — `href="npnfX-YY-ZZ.htm#…"`; notes live in a different volume page not
  present in this work's folder. **→ still open.**
- **dangling in-page anchors** — `href="#Pxxxx_yyyy"` whose target anchor was never captured.
  **→ still open** (though note: Augustine/Letters' apparent dangling anchors turned out to live
  in its `footnote/` pages and were recovered — worth re-checking each before deferring).

## Recovered (15) — 2026-09-18

Each rewritten so `footnote/fnNN.htm#anchor` refs point in-page (`#anchor`), with one ref-ordered
notes block injected; verified balanced + visible-text-identical against the transformer.

| # | File | Refs |
|---:|---|---:|
| 1 | `Acts of Peter and Paul/Acts of Peter and Paul.html` | 46 |
| 2 | `Aphrahat the Persian Sage/The Demonstrations.html` | 567 |
| 3 | `Apostolic Constitutions/Constitutions of the Holy Apostles Book 7.html` | 207 |
| 6 | `Augustine of Hippo/A Treatise on the Predestination of the Saints/Book 2.html` | 157 |
| 7 | `Augustine of Hippo/Confessions/Book 11.html` | 71 |
| 8 | `Augustine of Hippo/Confessions/Book 12.html` | 98 |
| 10 | `Augustine of Hippo/Letters.html` | 861 |
| 11 | `Augustine of Hippo/On Care to Be Had for the Dead.html` | 70 |
| 20 | `Hermias Sozomen/THE ECCLESIASTICAL HISTORY/Book 9.html` | 20 |
| 21 | `Hippolytus of Rome/Dubious and Spurious Pieces.html` | 206 |
| 22 | `John Cassian/The Seven Books on the Incarnation of the Lord,/Book 7.html` | 89 |
| 25 | `John Chrysostom/Homilies/On Romans/Homily 32.html` | 13 |
| 29 | `Origen of Alexandria/Against Celsus/Book 8.html` | 139 |
| 31 | `Origen of Alexandria/Commentary on Matthew/Book 11.html` | 216 |
| 32 | `Origen of Alexandria/Commentary on Matthew/Book 14.html` | 210 |

**Recovered total: ~2,970 references across 15 files.**

## Recovered (17) — 2026-09-18 (second pass: dangling in-page anchors / sibling-page refs)

The harder sub-forms, recovered with the extended engine
`standardization/tools/footnote_resource/resource_footnotes_v2.py`. For the dangling-anchor files,
the complete tertullian.org/Wayback source page carries the same anchors as `footnote/fnNN.htm` refs,
mapping each anchor to its footnote page; those pages supplied the defs. Reply to Faustus Bk5's notes
came from the named NPNF endnotes page (`npnf1-04-64.htm`), with its sibling hrefs rewritten in-page.
Each verified balanced + visible-text-identical; highlight.js preserved.

| # | File | Refs | Sub-form |
|---:|---|---:|---|
| 4 | `Arnobius of Sicca/Against the Heathen Book 1.html` | 159 | dangling in-page anchors |
| 5 | `Arnobius of Sicca/Against the Heathen Book 2.html` | 522 | dangling in-page anchors |
| 9 | `Augustine of Hippo/Confessions/Book 9.html` | 125 | dangling in-page anchors |
| 12 | `Augustine of Hippo/Reply to Faustus the Manichaean/Book 5.html` | 26 | sibling-page refs |
| 13 | `Augustine of Hippo/The City of God/Book 13.html` | 23 | dangling in-page anchors |
| 14 | `Augustine of Hippo/The City of God/Book 14.html` | 91 | dangling in-page anchors |
| 15 | `Augustine of Hippo/The City of God/Book 15.html` | 28 | dangling in-page anchors |
| 16 | `Gregory the Dialogist/Register of Epistles/Book 5.html` | 19 | dangling in-page anchors |
| 17 | `Gregory the Dialogist/Register of Epistles/Book 6.html` | 54 | dangling in-page anchors |
| 18 | `Gregory the Dialogist/Register of Epistles/Book 7.html` | 38 | dangling in-page anchors |
| 19 | `Gregory the Dialogist/Register of Epistles/Book 8.html` | 4 | dangling in-page anchors |
| 23 | `John Chrysostom/Homilies/On Matthew/Homily 11.html` | 51 | dangling in-page anchors |
| 24 | `John Chrysostom/Homilies/On Matthew/Homily 12.html` | 22 | dangling in-page anchors |
| 26 | `Lucius Caecilius Firmianus Lactantius/The Divine Institutes Book 6.html` | 108 | dangling in-page anchors |
| 27 | `Lucius Caecilius Firmianus Lactantius/The Divine Institutes Book 7.html` | 155 | dangling in-page anchors |
| 28 | `Lucius Caecilius Firmianus Lactantius/The Epitome of the Divine Institutes.html` | 29 | dangling in-page anchors |
| 30 | `Origen of Alexandria/Commentary on John/Book 6.html` | 141 | dangling in-page anchors |

**Second-pass recovered total: ~1,595 references across 17 files.**

## Still open (0)

**Original total: 32 files → 32 recovered, 0 remaining.** The whole type-01 content-missing cluster
(A/B) is closed; no file was forced through and no gate was weakened.

## D-cluster one-offs (3) — RESOLVED 2026-09-19 (structural/format, not content re-source)

The 3 remaining predicted failures were **not** content-recovery jobs — all note text was already
in each file; the problems were structural/format, so they were fixed manually in place (no gate
weakened, transformer untouched, all note text preserved verbatim):

| File | Fix | Result |
|---|---|---|
| Aristides/The Apology/Introduction | 5 def paragraphs converted from empty-`<a name>` + separate `<sup>N</sup>` to `<sup id="ANCHOR">N</sup>`; highlight.js added | PASS refs=5 notes=5 valid=True (standard) |
| Aristides/The Apology/…parallel columns | hand-authored idempotent `<article class="writing">` fragment: kept the two-column Greek\|Syriac table, dropped only nav chrome, refs/notes rebuilt as standard two-way-linked 1..25; highlight.js added | PASS mode=idempotent, valid=True; independent visible-text check: 12487/12487 tokens, word multisets identical (0 lost, 0 added) |
| Leo the Great/Letter 123 To Eudocia Augusta | two title footnote refs moved out of the `<font size=4>` title block to a `<p>` just after `</h2>` (in document order) so the transform no longer reverses them on relocation | PASS refs=8 notes=8 valid=True; fn1="See Letter CXVII…", fn2="See Letter CIX. above." (correct source order) |

**Type-01 predicted-failure set is now fully closed: 32 content-recovered (A/B/C) + 3 D-cluster
one-offs = 0 remaining.**
