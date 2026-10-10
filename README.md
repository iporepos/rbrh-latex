# rbrh-latex

LaTeX template for the journal *Revista Brasileira de Recursos Hídricos* (RBRH).
Designed to be imported straight into Overleaf — no local install needed.

## Quick start

1. Import this repository into Overleaf (**New Project → Import from GitHub**,
   or upload the `.zip`).
2. Compiler: **pdfLaTeX** (the Overleaf default — no change needed).
3. Fill in **`article.toml`** (title, abstracts, keywords, highlights) and
   **`authors.toml`** (names, affiliations, ORCID, emails), then regenerate
   the cover:
   ```
   python build_cover.py
   ```
4. Edit **`contents.tex`** — sections, figures, tables and equations. It
   starts at the first section; the cover is generated, so there is no front
   matter to maintain. Copy the worked examples already there and replace the
   placeholder text. Put your own image files in **`figures/`** (the
   `assets/` folder is reserved for the journal logo and other editor-owned
   icons).
5. Add your references to **`references.bib`** and cite them with
   `\textcite{key}` or `\parencite{key}`.

You should not need to open `main.tex` or `config.tex` — they hold the
journal's layout, fonts, colors and styling, and are maintained by the
editors.

## Metadata

Everything except the body text and the bibliography lives in three TOML
files, split by who owns the information:

| File | Holds | Who edits it |
|---|---|---|
| `journal.toml` | Journal name, logos, editor-in-chief, licence text | Editors |
| `article.toml` | Title, abstracts, keywords, highlights, DOI, volume, issue, dates, acknowledgements | Authors |
| `authors.toml` | One block per author: given and family name, affiliation, ORCID, email | Authors |

`python build_cover.py` reads all three and regenerates **`cover.tex`**,
which supplies the first page: masthead, title, author list, both abstracts,
and the whole sidebar (DOI, highlights, citation, correspondence,
acknowledgements, editors, data availability, publication dates, history and
the CC-BY notice). It also builds the short citation printed in the footer,
abbreviating the author list the way a citation does — one name in full, two
joined with `&`, three listed, and four or more as "First et al.".

In `authors.toml` each author gets a self-contained block, filled in like a
form. Give your name as `name_first` and `name_last` — split in two so the
family name is never guessed at. Put the whole family name in `name_last`,
particles and suffixes included ("dos Santos", "Magalhães Filho"), and it
will be cited correctly. Write your affiliation out in full rather than
referring to a number.
The script collects the affiliations, drops the duplicates and numbers them
by the order they first appear, so authors at the same institution share a
superscript automatically. Authors print in the order their blocks appear.

`cover.tex` is generated: don't edit it by hand, edit the TOML and re-run.
It is committed, so the template still compiles if you can't run Python.

The body language is set by `language` in `article.toml` (`english` or
`portuguese`); `draft = true` there stamps every page.

## Figures

Put your image files in **`figures/`** and insert them with one of three
macros — no LaTeX layout code needed:

```latex
\FigureM{name}{caption}{label}        % text width
\FigureS{name}{caption}{label}        % small, caption beside the image
\FigureL{name}{caption}{label}        % full width, margin to margin
```

`name` is just the file name — no folder, no extension. `figures/name` is
resolved against `.pdf`, `.png`, `.jpeg`, `.jpg`, in that order of
preference.

Each takes an optional float position first, defaulting to `t` (top):

```latex
\FigureM[b]{name}{caption}{label}     % bottom of the page
\FigureS[t][0.5]{name}{caption}{label} % and, for S only, a width
```

`\FigureS` accepts a second optional argument: its width as a fraction of
the text width (default `0.67`). Because position comes first, pass both
when you want to change the width.

If no matching file exists the build still succeeds and a placeholder box
appears in the figure's place, labelled with the name it looked for — so a
missing or misspelled image is obvious in the PDF instead of stopping the
compile.

## Tables

Two sizes, written as environments so the tabular material goes in the
body. The caption is an argument and is placed above the table:

```latex
\begin{TableM}{Caption text.}{tbl:label}
  \begin{tabularx}{\linewidth}{LLL}
  \toprule
  \textbf{A} & \textbf{B} & \textbf{C} \\
  \midrule
  1 & 2 & 3\tnote{a} \\
  \bottomrule
  \end{tabularx}
  \begin{tablenotes}
    \item[\textit{a}] A note about that value.
  \end{tablenotes}
\end{TableM}
```

`TableM` is text width; `TableL` spans the full width, margin to margin,
for tables with many columns. Both take the same optional position
argument as the figures (`\begin{TableM}[ht]{...}{...}`).

Notes are optional — the `tablenotes` block is passed through
`threeparttable`, keyed with `\tnote{a}` in the cell being annotated.

`L` is a left-aligned flexible column: `tabularx` divides `\linewidth`
between them, so the table fills the text width and the caption and notes
stay flush with it. Use `booktabs` rules — `\toprule`, `\midrule`,
`\bottomrule` — and avoid vertical lines. `contents.tex` ships worked
examples of both sizes.

## Language

The body language is set by `language` in `article.toml` (`portuguese` or
`english`). It drives hyphenation, dates, and every journal-facing label —
"Figure"/"Figura", "References"/"Referências" and so on. The abstract and
resumo are both printed whichever you choose, per RBRH convention.

## Bibliography style

`biblatex` with the `biber` backend, APA style with author–year citations.
Cite with `\textcite{key}` when the authors are part of the sentence
("Hoffman et al. (2023) showed…") and `\parencite{key}` when they belong in
parentheses ("…as reported (Hoffman et al. 2023)").

Put DOIs in `references.bib` as the bare identifier — `10.3390/e25010129`,
not the full `https://doi.org/…` URL — since biblatex adds the prefix
itself.

Run a **Full** / biber recompile in Overleaf if citations don't appear
after your first edit.

## Local compilation (optional)

Overleaf compiles this project on its own — nothing below is required to
use the template. If you also want to build it locally (needs a TeX
distribution with `latexmk` on your `PATH`):

```
./compile.sh      # Linux/macOS
./compile.ps1     # Windows (PowerShell)
```

Both run latexmk in silent mode and, only if the build succeeds, remove
the regeneratable auxiliary files (`.aux`, `.log`, `.bbl`, ...) and keep
`main.pdf`.

## Mathematics

`contents.tex` demonstrates the full set in *Mathematical features*: inline
math, numbered and unnumbered displays, lettered sub-equations (2a, 2b),
aligned systems, symbol variants, and theorem-like environments
(`definition`, `theorem`, `proof`, `lemma`, `corollary`, `example`,
`remark`) that number independently of the equations.

## Optional apparatus

`config.tex` also carries ready-to-use machinery you may not need: code
listings, color-coded admonition boxes (`amdnote`, `amdtip`,
`amdimportant`, `amdwarning`, `amdcaution`), numbered `boxstory` boxes,
and a draft watermark (`\IsDraft` in `main.tex`).
