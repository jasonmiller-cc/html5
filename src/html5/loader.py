"""File loaders that read HTML and CSS into html5 document objects."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from .css import CSSStyleSheet
from .document import HtmlDocument, Raw

_VOID_ELEMENTS = frozenset(
    {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }
)


class _HTMLStructureParser(HTMLParser):
    """Extract lang, title, head content, and body content from an HTML file."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.lang: str = "en"
        self.title: str = ""
        self._section: str = ""
        self._in_title: bool = False
        self._head_buf: list[str] = []
        self._body_buf: list[str] = []

    def _buf(self) -> list[str]:
        if self._section == "head":
            return self._head_buf
        if self._section == "body":
            return self._body_buf
        return []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "html":
            self.lang = attr_map.get("lang", "en") or "en"
            return
        if tag == "head":
            self._section = "head"
            return
        if tag == "body":
            self._section = "body"
            return
        if tag == "title" and self._section == "head":
            self._in_title = True
            return
        if tag == "meta" and self._section == "head" and "charset" in attr_map:
            return

        if self._in_title:
            return

        attrs_str = "".join(
            f" {k}" if v is None else f' {k}="{v}"'
            for k, v in attrs
        )
        self._buf().append(f"<{tag}{attrs_str}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("html", "head", "body"):
            if tag == "head":
                self._section = ""
            elif tag == "body":
                self._section = ""
            return
        if tag == "title" and self._in_title:
            self._in_title = False
            return
        if tag in _VOID_ELEMENTS or self._in_title:
            return
        self._buf().append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        else:
            self._buf().append(data)

    def handle_comment(self, data: str) -> None:
        self._buf().append(f"<!--{data}-->")

    def handle_entityref(self, name: str) -> None:
        self._buf().append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._buf().append(f"&#{name};")


def html_loader(path: str | Path) -> HtmlDocument:
    """Read an HTML file and return an :class:`HtmlDocument`.

    The document title, ``lang`` attribute, head nodes, and body content are
    extracted from the file.  The charset ``<meta>`` tag is stripped (since
    :meth:`HtmlDocument.render` always emits one).  All other head and body
    content is preserved as a single :class:`Raw` node each.

    Args:
        path: Path to the HTML file to read.

    Returns:
        An :class:`HtmlDocument` populated from the file.
    """
    content = Path(path).read_text(encoding="utf-8")
    parser = _HTMLStructureParser()
    parser.feed(content)

    doc = HtmlDocument(title=parser.title, lang=parser.lang)

    head_html = "".join(parser._head_buf).strip()
    if head_html:
        doc.add_head(Raw(head_html))

    body_html = "".join(parser._body_buf).strip()
    if body_html:
        doc.add_body(Raw(body_html))

    return doc


def css_loader(path: str | Path) -> CSSStyleSheet:
    """Read a CSS file and return a :class:`CSSStyleSheet`.

    The file content is stored as a single raw CSS block; no parsing of
    individual rules is performed.

    Args:
        path: Path to the CSS file to read.

    Returns:
        A :class:`CSSStyleSheet` whose rendered output is the file content.
    """
    content = Path(path).read_text(encoding="utf-8")
    return CSSStyleSheet().add_raw(content)


__all__ = ["html_loader", "css_loader"]
