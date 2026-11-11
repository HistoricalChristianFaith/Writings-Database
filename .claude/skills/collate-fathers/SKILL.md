---
name: collate-fathers
description: Check and fix the quality of one ANF/NPNF work imported from the 2004 CCEL fathers2 mirror — diff it against CCEL's modern text and ThML, rebuild drifted/truncated footnotes, adjudicate every difference against archive.org scans of the printed volume with subagents, run an adversarial review pass, then build, validate and report. Use when asked whether such a work's text is good, or to collate/proof/fix one against CCEL or the print.
argument-hint: <path to the work's .html>
---

# collate-fathers

Proof one work (`$ARGUMENTS`) from the CCEL **fathers2** mirror (ANF/NPNF imports, 2004 HTTrack) against independent
witnesses, with the 1880s–90s **print as the arbiter**. Typical defects: OCR errors, lost quote marks, beta-code Greek,
stripped italics, notes truncated at the first Greek word or at the first paragraph, and footnote **drift**, where
OCR ate a marker so every later marker opens the wrong note.

Scripts live in `.claude/skills/collate-fathers/scripts/` (call them `S/`). State lives in the gitignored work dir
`standardization/collate/<slug>/` (`WD`); downloads are cached in `standardization/collate/_cache/<vol>/`. Run
everything from the repo root. Read `VOLUMES.md` for known per-volume quirks first.

## 1. Prep and analyze (you)
```
python3 S/prep.py "<work.html>"        # -> volume, scan, leaf range; last line = WD
python3 S/analyze.py WD                # summary; details in WD/analysis.json
```
- prep refuses non-fathers2 works (check the first-version header); other lineages are out of scope.
- If the scan can't be found automatically, find it (archive.org, by volume/date), pass `--scan <id>`, and add it to
  `known_scans.json`.
- Read the analyze summary and tell the user the verdict in a few lines: body hunk counts, the drift count
  ("markers pointing at the wrong def"), notes with no text or no marker, run-in sections, missing headings. If the
  work is clean (only a handful of trivial hunks, no drift), say so and stop unless the user wants the fixes.

## 2. Adjudicate (subagents, parallel)
`python3 S/packets.py WD [N]` splits the review items into N packets (default ≈ 1 per 110 items, max 6) and writes
`WD/packets/BRIEF.md`. Launch N `general-purpose` agents **in one message**, each with:
> Read and follow `WD/packets/BRIEF.md` exactly. Your K = k (packet `WD/packets/pk.json`, leaves …). Write
> `WD/packets/dk.json`. Do not edit any file outside `WD/packets/` and `WD/img/`.

Relay their key findings to the user as they arrive. Keep each `_report`: it lists fixes needed outside the hunks.

## 3. Adversarial review (subagents, parallel)
`python3 S/merge.py WD --review-prep` checks coverage (it reports any undecided or stray items; fix those by
resuming the agent), then writes `WD/review/` with decisions stripped of reasoning (`qK.json`), a sample to check
(`sampleK.json`: all customs + ~25% of the rest), a preview build `after.html`, and `review/BRIEF.md`. Launch one
**fresh** `general-purpose` agent per packet (not the adjudicators, and no anchoring on their reasoning) with:
> Read and follow `WD/review/BRIEF.md` exactly. Your K = k. Write `WD/review/rk.json`.

Then `python3 S/merge.py WD` applies the overrides and collects `WD/review/structural.json`. For each override that
changes a reading, look at the crop yourself if the two agents' readings both look plausible
(`python3 S/leaf.py WD --find "words"`, `python3 S/leaf.py WD LEAF x0 y0 x1 y1`, then Read the image). The print
decides; edit `WD/merged.json` to settle it.

## 4. Build, hand-fix, validate (you)
`python3 S/build.py WD "<work.html>"` rebuilds the file from `WD/orig.html` + `WD/merged.json`. It applies the body
decisions and rebuilds all notes in print order: missing markers are re-inserted, and everything is renumbered.

Hand fixes go into `merged.json` → `"hand"`, never directly into the file, so the build stays reproducible:
`{"old": "<exact text in the built file>", "new": "…", "count": 1}` (add `"regex": true` for a regex). Sources:
- `MANUAL` lines from build (hunks whose span crosses `<i>` etc.): `WD/manual.json`;
- analysis structure: `para_missing`, `runins`, `missing_heads` → `<br/><br/>` breaks / `<h2>` headings (match the
  file's own `<br>` style and heading conventions);
- `PROBLEM` lines from build: a marker it could not place → `merged.json "markers": {"tNNN": "<regex; marker goes
  after the match>"}`; our defs with no ThML counterpart → decide by hand from the print;
- adjudicators' `_report` "outside my hunks" items and `review/structural.json`, after confirming each in the print;
- print-style passes the agents establish for the whole work (e.g. spaced `. . .` ellipses, a word the print spells
  differently throughout). Use a regex hand fix with an explicit count.
Re-run build after each batch of hand fixes, then `python3 S/validate.py WD -v`. The hard checks must pass. Every
remaining difference from CCEL must be a deliberate print reading: go through the `-v` list.

## 5. Report and stop
Tell the user what was wrong (with concrete examples), what changed, what is still open, and anything you couldn't
verify. Offer a commit; don't commit unasked. When asked: commit on `master` with a message like
`<Author>, <Work> (<VOL>): collate against print, fix OCR, rebuild notes` and a short body, **no Co-Authored-By or
other Claude attribution**. Add any new per-volume quirk you learned to `VOLUMES.md`.

## Conventions (CLAUDE.md format)
Bare fragment in `<article class="writing">`, paragraphs as `<br><br>` (keep the file's existing `<br/>` vs `<br>`
style), two-way-linked notes `rN`/`fnN` numbered 1..k in document order, multi-paragraph notes joined with `<br>`.
Preserve the print exactly. Straight quotes, em dashes `—`, Unicode Greek.

## Cost
About 200–250k subagent tokens per 100 review items for adjudication, plus roughly half that for the review. Fan out
across several works only if the user asks.
