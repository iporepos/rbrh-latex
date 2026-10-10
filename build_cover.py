#!/usr/bin/env python3
"""Render journal.toml + article.toml + authors.toml into cover.tex.

cover.tex holds nothing but data: one macro per field, which
config.tex's \\PrintCover and friends lay out. That split keeps
styling in the editor-owned config and content in the TOML files,
and means this generated file never needs hand-editing.

Usage:
    python build_cover.py

The template compiles without running this script -- cover.tex is
committed as generated output. Re-run it after editing any of the
three TOML files.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "cover.tex"

_ESCAPE_MAP = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape(text: str) -> str:
    """Escape LaTeX specials in plain data such as names and emails.

    Backslashes and braces are deliberately left alone: the TOML
    carries hand-written LaTeX in the prose fields (abstracts,
    highlights), and escaping those would break it.
    """
    return "".join(_ESCAPE_MAP.get(ch, ch) for ch in text)


def load(name: str) -> dict:
    with (ROOT / name).open("rb") as fh:
        return tomllib.load(fh)


def full_name(author: dict) -> str:
    """The printed name: given names, then family name.

    Names are stored split rather than as one string so the family
    name is never guessed at. Splitting on whitespace would get
    compound surnames such as "Magalhães Filho" or "dos Santos"
    wrong, and those are exactly the names a citation has to get
    right.
    """
    return f"{author['name_first']} {author['name_last']}".strip()


def resolve_affiliations(authors: list[dict]) -> list[str]:
    """Collect the distinct affiliations, in order of first appearance.

    Authors write their institution out in full in their own
    block, so the same string recurs for everyone who shares it.
    Numbering them by first appearance is what lets an author fill
    in a self-contained form without having to look up an id.
    """
    seen: list[str] = []
    for author in authors:
        affiliation = author.get("affiliation", "").strip()
        if affiliation and affiliation not in seen:
            seen.append(affiliation)
    return seen


def render_authors(authors: list[dict], affiliations: list[str]) -> str:
    out = []
    for author in authors:
        name = escape(full_name(author))

        # The ORCID mark sits between the name and the affiliation
        # superscript and carries the link itself, so the name stays
        # plain text. \orcidlink scales to the font's X-height and
        # therefore cannot disturb line spacing.
        orcid = author.get("orcid", "")
        icon = f"\\,\\orcidlink{{{orcid}}}" if orcid else ""

        marks = []
        affiliation = author.get("affiliation", "").strip()
        if affiliation:
            marks.append(str(affiliations.index(affiliation) + 1))
        if author.get("corresponding"):
            marks.append("*")
        sup = f"\\textsuperscript{{{','.join(marks)}}}" if marks else ""

        out.append(f"{name}{icon}{sup}")
    return ", ".join(out)


def render_affiliations(affiliations: list[str]) -> str:
    # One flowing paragraph, semicolon-separated, matching the way
    # the author list runs on -- not one line per affiliation.
    return "; ".join(
        f"\\textsuperscript{{{i}}}{escape(name)}"
        for i, name in enumerate(affiliations, start=1)
    )


def render_corresponding(authors: list[dict]) -> str:
    flagged = [a for a in authors if a.get("corresponding")] or authors[:1]
    parts = []
    for author in flagged:
        name = escape(full_name(author))
        email = author.get("email", "")
        if email:
            parts.append(f"{name}\\\\ \\href{{mailto:{email}}}{{{escape(email)}}}")
        else:
            parts.append(name)
    return " \\\\ ".join(parts)


def render_citation_authors(authors: list[dict]) -> str:
    """Author part of the short citation.

    One author prints in full; two are joined with an ampersand;
    three are listed; more than three collapse to "First et al.".
    """
    names = [escape(a["name_last"]) for a in authors]
    if len(authors) == 1:
        return escape(full_name(authors[0]))
    if len(names) == 2:
        return f"{names[0]} \\& {names[1]}"
    if len(names) == 3:
        return f"{names[0]}, {names[1]} \\& {names[2]}"
    return f"{names[0]} et al."


def main() -> None:
    journal = load("journal.toml")
    article = load("article.toml")
    people = load("authors.toml")

    authors = people["authors"]
    affiliations = resolve_affiliations(authors)
    dates = article.get("dates", {})
    doi = article.get("doi", "").strip()
    year = dates.get("published", "").split()[-1] if dates.get("published") else ""

    cite_authors = render_citation_authors(authors)
    short_citation = f"{cite_authors} ({year}). {journal['abbreviation']} {article.get('volume', '')}."
    if doi:
        short_citation += f" \\url{{https://doi.org/{doi}}}"

    full_citation = (
        f"{cite_authors} ({year}). {escape(article['title'])}. "
        f"{journal['name']}, {article.get('volume', '')}, {article.get('issue', '')}."
    )

    highlights = "\\\\\n".join(
        f"---\\quad {h}" for h in article.get("highlights", [])
    )

    def field(name: str, value: str) -> str:
        return f"\\newcommand{{\\{name}}}{{{value}}}"

    lines = [
        "% Auto-generated by build_cover.py from journal.toml,",
        "% article.toml and authors.toml. Do not edit by hand --",
        "% edit those files and re-run:  python build_cover.py",
        "",
        "% --- Journal ---",
        field("JournalName", journal["name"]),
        field("JournalNameEn", journal["name_en"]),
        field("JournalAbbrev", journal["abbreviation"]),
        field("JournalLogoLeft", journal["logo_left"]),
        field("JournalLogoRight", journal["logo_right"]),
        field("EditorInChief", escape(journal["editor_in_chief"])),
        field("LicenseBadge", journal["license"]["badge"]),
        field("LicenseCopyright", journal["license"]["copyright"]),
        field("LicenseStatement", journal["license"]["statement"].strip()),
        "",
        "% --- Article ---",
        field("DocLanguage", article.get("language", "english")),
        field("IsDraft", "true" if article.get("draft") else "false"),
        field("ArticleType", article["type"]),
        field("ArticleTitle", article["title"]),
        field("ArticleShortTitle", article["short_title"]),
        field("ArticleCity", article["city"]),
        field("ArticleDOI", doi),
        field("ArticleVolume", article.get("volume", "")),
        field("ArticleIssue", article.get("issue", "")),
        field("AssociatedEditor", escape(article["associated_editor"])),
        field("CompetingInterests", article.get("competing_interests", "")),
        field("DataAvailability", article.get("data_availability", "")),
        field("Acknowledgements", article.get("acknowledgements", "").strip()),
        field("DatePublished", dates.get("published", "")),
        field("DateReceived", dates.get("received", "")),
        field("DateReviewed", dates.get("reviewed", "")),
        field("DateAccepted", dates.get("accepted", "")),
        "",
        "% --- Abstracts ---",
        field("AbstractEn", article["abstract"]["en"].strip()),
        field("KeywordsEn", article["keywords"]["en"]),
        field("AbstractPt", article["abstract"]["pt"].strip()),
        field("KeywordsPt", article["keywords"]["pt"]),
        "",
        "% --- Authors ---",
        field("AuthorBlock", render_authors(authors, affiliations)),
        field("AffiliationBlock", render_affiliations(affiliations)),
        field("CorrespondingBlock", render_corresponding(authors)),
        "",
        "% --- Citations ---",
        field("ArticleCitation", full_citation),
        field("ArticleShortCitation", short_citation),
        "",
        "% --- Highlights ---",
        f"\\newcommand{{\\ArticleHighlights}}{{%\n{highlights}%\n}}",
        "",
    ]

    TARGET.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Wrote {TARGET.relative_to(ROOT)} "
        f"({len(authors)} authors, {len(affiliations)} affiliations)"
    )


if __name__ == "__main__":
    main()
