# Per-volume notes (add to this as you learn)

General (all fathers2 imports)
- CCEL .txt flattens œ→oe (keeps æ); drops the opening single quote of nested quotations; compresses ". . ." to "...".
- CCEL silently corrects the print's own typos. Keep the print's reading.
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
