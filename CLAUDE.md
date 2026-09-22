# Writings-Database — working notes

## Git workflow
- Commit directly on `master`. Do **not** create feature branches for changes in this repo.

## HTML works — standard format
Each writing is a **bare semantic fragment**, not a full document. The site renderer injects the
`<head>`, `<title>`, site chrome, CSS, and the `highlight.js` reader script at serve time — so a
fragment contains **no** `<html>`/`<head>`/`<body>`/`<title>` and **no** `highlight.js` script.

- Wrap the whole work in `<article class="writing">`.
- **Paragraphs are `<br><br>`, never `<p>`.** Block elements appear only for headings, the notes
  `<hr>`, `<section class="notes">`, and the `<article>` wrapper.
- `<h1>` = work title (author is derived from the top-level folder — don't repeat it in the title).
  Use `<h2>`/`<h3>` for book / part / section headings.
- Optional leading source note: `<i>{translator/source, edition, license, bracket conventions}</i><br><br>`.
- Scripture quotes in `<i>…</i>`; dialogue speaker labels as `<b>Speaker:</b>` (dialogues only).
- Footnotes are two-way-linked, numbered 1..k in document order:
  - reference: `…text<sup><a href="#fnN" id="rN">N</a></sup>`
  - definitions in a trailing section:
    `<section class="notes"><hr><span id="fnN"><a href="#rN">N</a>&nbsp;Footnote text</span><br>…</section>`
- Preserve the source text **exactly** — structure only; no spelling/grammar/translation "fixes".

Example skeleton:
```html
<article class="writing">
<h1>{Work Title}</h1>
<i>{source note}</i><br><br>
<h2>{Book / Part}</h2>          <!-- only for multi-part works -->
Body paragraph…<sup><a href="#fn1" id="r1">1</a></sup><br><br>
<section class="notes">
<hr>
<span id="fn1"><a href="#r1">1</a>&nbsp;Footnote text</span><br>
</section>
</article>
```

Non-HTML writings (PDF/doc/docx/rtf, often a `Translation-*.pdf` plus a `note.txt`) live in their own
work subfolders and are outside this format.
