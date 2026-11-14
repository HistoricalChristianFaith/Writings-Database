# Adjudication brief — collate a fathers2 e-text against the print

Work dir: `{WD}`   ·   scripts: `{SCRIPTS}`   ·   volume: `{VOL}`   ·   scan: archive.org `{SCAN}`

Our text (`{HTML}`) is READ-ONLY for you — never edit it or anything outside `{WD}/packets/` and `{WD}/img/`.
It is a 2004 OCR'd e-text: OCR errors (tile/the, oar/our, girls/gifts, arid/and, riot/not), dropped or doubled quote
marks, stripped footnote italics, Greek left as ASCII beta-code (`dia/`, `e0n`, `a'narxi/a`), footnote markers eaten
by OCR (often turned into "?" or ","), notes truncated at their first Greek word. CCEL's modern text (body) and ThML
(notes; Unicode Greek + italics) are mostly right but not always. **The printed volume is the arbiter.**

## Witnesses
- Per-leaf OCR of the print: `python3 {SCRIPTS}/leaf.py {WD} --find "a few words"` → leaf ids (with printed page);
  `python3 {SCRIPTS}/leaf.py {WD} --text LEAF` prints that leaf's OCR. OCR uses curly quotes and hyphenates at
  line ends — search 3–6 distinctive words.
- Other independent OCRs of the same volume (whole-volume text, grep them): {EXTRA_OCR} (in the cache dir next to the
  volume files; path in `{WD}/config.json` → `extra_ocr`).
- Page image — the real arbiter for anything OCR can't settle (punctuation, quote marks, Greek, italics, footnote
  marker positions): `python3 {SCRIPTS}/leaf.py {WD} LEAF x0 y0 x1 y1` (fractions 0–1; pages are usually two
  columns with footnotes at the bottom) → prints a crop path; Read it. Crop tightly so the text is legible.
- Look at the image whenever the OCRs disagree, and always for quotes/punctuation/Greek/italics.

## Your packet `{WD}/packets/p{K}.json`
- `body`: token-diff hunks ours→CCEL. `id` "i1:i2" = our token span; `ours` / `ccel` = the tokens; `ctx_*` = 12
  tokens either side with the hunk in [[ ]]. Empty `ours` = CCEL has extra words; empty `ccel` = we have extra.
- `notes`: footnotes keyed `key` (e.g. "t712"). `kind` "pair" = our note text (`ours`, HTML-escaped) differs from
  ThML's (`thml`); "thml-only" = we have no text for this note at all (verify ThML's text against the print).
  `marker_missing: true` = our body has no footnote marker for it (`thml_ctx` = ThML text just before the marker);
  just confirm in `_report` that the print has a marker there — the pipeline re-inserts it.

## Decide every item
Body: `"ccel"` (take CCEL's tokens), `"ours"` (keep), or a custom replacement for our token span — plain text, straight
quotes `"` `'`, em dash written `--`, Unicode Greek. A custom string may contain `¶` to mean "paragraph break here"
(e.g. `"us.¶3."` when a numbered section has been run into the previous paragraph).
Notes: `"thml"`, `"ours"`, or a full custom note text (allowed markup: `<i>…</i>`, `<sup>…</sup>`, `<br>` for a
paragraph/line break inside a long note; plain `&` not `&amp;`; straight quotes; Unicode Greek with accents).

Rules:
- Match the print exactly, including its archaisms and period spellings ("shew", "connexion", "to-day") — do not
  modernize. CCEL often silently corrects the print; that alone is NOT a reason to take CCEL.
- Exception — obvious print typos: when the print has an unmistakable typographical error (dropped/transposed/broken
  letter "pruence", doubled word "yourself yourself", wrong verse number you can verify) AND the correct reading is
  certain, take the corrected reading (often CCEL's). Check how others read it first (WebSearch: CCEL, New Advent,
  other editions/reprints, the original language). If there is any doubt, keep the print. List every such
  correction in `_report` under "print typos corrected", with the print's form.
- Small caps in the print (section-opening words like "HE is not", "MSS.") → normal case (CCEL's form).
- Beta-code Greek → the print's Greek in Unicode with accents (`(dia/)` → `(διά)`); CCEL's transliteration (`dia`) is
  not acceptable — read it off the image.
- CCEL drops the opening single quote of nested quotations; the print has it. A backtick in ours (`` `of ``) is an
  opening single quote → `'of`.
- Ellipses: follow the print's spacing (usually `. . .`); CCEL compresses them to `...`.
- ThML is usually right for notes but has its own errors (broken entities like `&#…`, garbled Greek, wrong names,
  `…` for ". . ."); verify any wording or Greek difference against the print.
- Never return a decision for an id/key that is not in your packet.

## Output
Write `{WD}/packets/d{K}.json`:
`{"body": {"i1:i2": "ccel"|"ours"|"<custom>"}, "notes": {"tNNN": "thml"|"ours"|"<custom>"}, "_report": "…"}`
Cover every item. `_report`: CCEL/ThML errors vs print, anything you could not verify, and anything structural you
noticed outside your items (merged/missing paragraphs, headings, footnote markers in the wrong place, missing words,
errors shared by ours and CCEL) — give enough context to find each. Final message: ≤5 lines + counts per decision.
