# Adversarial review brief — check another agent's collation decisions against the print

Work dir: `{WD}` · scripts: `{SCRIPTS}` · scan: archive.org `{SCAN}`. Read `{WD}/packets/BRIEF.md` first for the
witnesses, tools and house rules — they apply to you too. Edit nothing outside `{WD}/review/` and `{WD}/img/`.

Someone has already decided each item in `{WD}/packets/p{K}.json`; their decisions are in `{WD}/review/q{K}.json`
(`body` / `notes` maps — their reasoning is deliberately withheld). Assume they made mistakes and find them. You are
judged on errors found that are real, not on agreement.

## What to check
1. Every **custom** decision (body and notes) — character by character against the page image: words, spelling,
   punctuation, quote marks, Greek letters/accents/breathings, italics.
2. A sample of the rest: `{WD}/review/sample{K}.json` lists the ids/keys to check (a random ~25% of "ccel"/"thml"/
   "ours" decisions). Check each against the image.
3. Structure, for the leaf range of your packet: open each page image and compare it with the corresponding stretch
   of `{WD}/review/after.html` (the work with all decisions applied, and with footnotes rebuilt). Look for: a
   paragraph break or numbered section missing/extra; a heading missing or wrong; a footnote marker missing, extra
   or on the wrong word; a footnote whose text belongs to a different marker; words missing or duplicated. Note the
   check in `_structure` even when nothing is wrong ("n104: ok").

Only report a problem you have verified on the page image. Quote the print exactly.

## Output `{WD}/review/r{K}.json`
```
{"overrides": {"body": {"i1:i2": "<value>"}, "notes": {"tNNN": "<value>"}},
 "structural": [{"where": "<context to find it>", "print": "<what the print has>", "fix": "<what to change>"}],
 "_structure": "<per-leaf one-liners>",
 "_report": "<what you checked, how many items, what you found>"}
```
Override values use the same vocabulary as the original decisions ("ccel"/"ours"/"thml"/custom). Final message: ≤5
lines with counts (checked / overridden / structural).
