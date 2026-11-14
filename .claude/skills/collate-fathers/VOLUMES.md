# Per-volume notes (add to this as you learn)

General (all fathers2 imports)
- CCEL .txt flattens œ→oe (keeps æ); drops the opening single quote of nested quotations; compresses ". . ." to "...".
- CCEL silently corrects the print's own typos. Take the correction only for an obvious typo whose fix is certain
  (policy since 2026-11-14); otherwise keep the print's reading.
- New Advent is NOT an independent witness: it has the same OCR errors as fathers2.
- Original fathers2 footnote pages (with `<I>` and SPIonic Greek) are on Wayback:
  `web/2006id_/http://www.ccel.org:80/fathers2/<VOL>/footnote/fnNNN.htm`. They are a fallback witness for notes when
  ThML is garbled.
- Print small caps (MSS., chapter-opening words) → normal case.

anf05 (Novatian etc.) — scans `antenicenefather05robeuoft` (+ `antenicenefather05robe`); leaf = printed page + 11.

npnf105 (Augustine, Anti-Pelagian) — scan id is MISLABELED `psychologybriefe05jameuoft` (really NPNF1 v5, 1887);
printed page = leaf − 77. Imports ended with the NEXT work's Retractations extract (fixed in 9e28284a). Check for
this in other NPNF1 volumes.

npnf106 (Augustine, Harmony etc.) — scan `aselectlibrary06unknuoft`, leaf = printed page + 17. Footnote-def drift
happened where the print sets one note number at several marks.

npnf208 (Basil) — scan `niceneandpostnic08unknuoft` (1895), leaf = printed page + 86; extra OCRs
`selectlibraryofn08scha`, `selectlibraryofn0008phil_q3e0`. ThML notes have many broken Greek entities/typos, so
check them against the print. The print uses "subnumeration" (unhyphenated) in running text, ". . ." ellipses, and
"It's" for "Its". De Spiritu Sancto collated 2026-11-11 (4622138d).

anf06 (Gregory Thaumaturgus, Dionysius, Julius Africanus, …) — scan `antenicenefathte0006jame` (Buffalo 1886),
leaf = printed page + 12; extra OCRs `antenicenefather06buff`, `antenicenefather0006unse_h9i4`. Fathers2 OCR read
"Heli" as "Hell" throughout Africanus. ThML Hebrew can be in reversed logical order (check it against the image).

npnf201 (Eusebius, Church History) — scan `cu31924031002102` (Cornell, 1890), leaf = printed page + 13. The other
archive.org candidates are different volumes. The work is split into 10 Book files: run prep per Book, and fix the
leaf range by hand when a stray phrase hit widens it (Books 2 and 9). analyze's ThML range can be off by one at
book edges (the previous book's last note, or front matter such as t10 in Book 1), so check th_lo/th_hi.
- The print sets bare margin section numbers ("12", no period), and the file convention is one section per
  paragraph, "N Text". Keep ours on every "N" vs CCEL "N." hunk. A section that begins at a quotation after a
  colon or comma does start a new paragraph, at the quotation. Other mid-sentence starts are not split. The bare "1"
  is kept in single-section chapters, although the print has no numeral there. Section starts are often misplaced
  in both ours and CCEL: check them against the margin numerals.
- Chapter headings: the files use the importer's Title Case, kept for consistency (the print uses sentence-ish case).
- ThML Greek is systematically broken: `€`=ά, `ž`=ἔ, `Ž`=ᾷ, and `&amp; NNN·` (U+0387 terminator) with 139=ᾳ,
  251=ῳ, 242=ῶ, 240=ώ, 231=ό, 252=ῴ, 191=ῥ, 187=ΐ (βρεουΐον). Some notes are set in a Greek font by mistake
  ("Σεε αβόε, νοτε 5." = "See above, note 5."). Check every ThML note that carries Greek.
- Structural damage found 2026-11-11: Book 4 Chs. I–V §4 and XI–XV come from a worse retyped lineage (typos like
  "hte"; run-in sections "2At"; headings XII–XV run into the text; no notes). The notes in Books 9/10 were shifted:
  Book 9 held the Martyrs-of-Palestine notes (a duplicate of Book 8's), Book 10 held Book IX's, and Book X's were
  missing. Book 4 was then fully collated: the retyped span had also dropped words (XV §3 "dwelleth at Smyrna
  to the church of God which"; "and our Lord Jesus Christ"), and ThML note t1099 dropped a sentence (eye-skip).
- Learned across Books 2–10 (collated 2026-11-11/12 by per-Book lead agents; brief in
  standardization/collate/EUSEBIUS_LEAD_BRIEF.md):
  - fathers2 section starts are often misplaced in ours AND CCEL, frequently by one line off the margin numeral
    (26 in Book 6 alone). Check every one, and also look for run-in numerals ("And 6 when").
  - Unnumbered paragraph breaks inside a section are kept where the print has them.
  - Lost notes show up in analyze as "drift" plus unmatched defs. In Book 5 a lost note left its garbage spliced into
    the next two defs; in Book 8 a note cut off at its first Greek word did the same. The print sometimes sets two
    notes under one marker (Book 7 XXIX §1), or a note with no marker (Book 8 XI).
  - Whole notes or sentences can be missing: Book 3 lost the last six notes of XXXIX and ~120 words of the
    Papias-on-Mark note.
  - A note imported from ThML is trivially "identical to ThML", so the pipeline skips it. Proof such notes against
    the print explicitly.
  - Custom note text must use a plain "&amp;" (build re-escapes it). In notes, keep "§N" (no space) and the space
    after an opening italic abbreviation ("<i>Ibid.</i> chap.").
  - Parallel adjudicators sharing a scratchpad can overwrite each other's temp files: make them prefix their temp files.

npnf207 (Cyril of Jerusalem, Gregory Nazianzen) — scan `cu31924079626705` (Cornell 1890), leaf = printed page + 75.
No extra OCRs (the other archive.org copies 403/401). Orations 4 and 5 and the Introduction in
`Gregory of Nazianzus/Orations/` are from King's *Julian the Emperor* (1888), not fathers2 — out of scope.
24 orations collated 2026-11-13 by per-group lead agents (brief: standardization/collate/NAZIANZEN_LEAD_BRIEF.md).
- prep's leaf range is often blown wide by stray phrase hits (shared Scripture phrases; Or. 45 repeats long passages
  of Or. 38): set leaf_lo/hi by hand from the contiguous hit cluster.
- analyze's run-in detector fires on years ("a.d. 361") and on the "</blockquote>1." intro boundary — false alarms.
- Small caps → CCEL's form: "a.d." (CCEL has 135×, 0× "A.D."), "mss."/"MSS." as CCEL has it at each spot.
- The print restores æ (Cæsarius, Nicæa, Hær.) where fathers2 has "ae"; but some spots really print "ae"
  (Or. 21 "Haer. 68.7", Or. 1 "Caesarius", Or. 45 "Arimathaea"). Check the image, don't regex it.
- Defective ellipses: the print often shows 1–2 dots where type dropped out; we normalize to ". . .".
- The print sets "Introduction to …" headings and puts the oration title AFTER the editor's intro; the files keep
  title-first with the intro in <blockquote> (house layout, 117 corpus files use <blockquote>; validate allows it).
- Drift came from 1–3 lost markers or lost defs per oration (Or. 2: 205 markers off; Or. 43 note 146 held two notes
  run together); Or. 42's last note (Col. iv. 18) sat in Or. 43's ThML range.
- Errors shared by ours AND CCEL were common (same OCR lineage): "cats stones", "us His only sacrifice", "became That
  which", "bent gain", "to the fortune" (=opportune, lost at a column break), dropped repeated words ("loveth most
  most", "laughter laughter"). Read suspicious words in the print even when both agree.
- 2026-11-14, under the new typo policy: 62 print typos corrected across 21 orations (hand fixes tagged
  `"why": "print typo …"` in each merged.json). Many are wrong verse numbers in notes that were verified from the
  body text (Cant. "xi." → ii. 15, "Cor. xvii. 7" → 2 Cor. xii. 7). New Advent modernizes spelling ("today",
  "yourself"), so it is useless for hyphenation questions; CCEL is the better comparison.
