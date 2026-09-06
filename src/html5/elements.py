"""Generated HTML5 element classes."""

from __future__ import annotations

from typing import Any

from .document import Element, Node


VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

HTML5_ELEMENTS = (
    "a",
    "abbr",
    "address",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "bdi",
    "bdo",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "datalist",
    "dd",
    "del",
    "details",
    "dfn",
    "dialog",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hgroup",
    "hr",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "menu",
    "meta",
    "meter",
    "nav",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "param",
    "picture",
    "pre",
    "progress",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "script",
    "section",
    "select",
    "slot",
    "small",
    "source",
    "span",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "u",
    "ul",
    "var",
    "video",
    "wbr",
)


def _class_name(tag: str) -> str:
    return tag.replace("-", " ").title().replace(" ", "")


def _build_init(tag: str, *, void: bool) -> Any:
    def __init__(self, *children: Node | str, **attributes: Any) -> None:
        if void and children:
            raise ValueError(f"{tag} is a void HTML element and cannot have children")
        Element.__init__(self, tag=tag, children=children, attributes=attributes, void=void)

    return __init__


def _create_tag_class(tag: str) -> type[Element]:
    cls = type(
        _class_name(tag),
        (Element,),
        {
            "__module__": __name__,
            "__init__": _build_init(tag, void=tag in VOID_ELEMENTS),
        },
    )
    cls.__doc__ = f"Render a <{tag}> HTML element."
    return cls


A = _create_tag_class("a")
Abbr = _create_tag_class("abbr")
Address = _create_tag_class("address")
Area = _create_tag_class("area")
Article = _create_tag_class("article")
Aside = _create_tag_class("aside")
Audio = _create_tag_class("audio")
B = _create_tag_class("b")
Base = _create_tag_class("base")
Bdi = _create_tag_class("bdi")
Bdo = _create_tag_class("bdo")
Blockquote = _create_tag_class("blockquote")
Body = _create_tag_class("body")
Br = _create_tag_class("br")
Button = _create_tag_class("button")
Canvas = _create_tag_class("canvas")
Caption = _create_tag_class("caption")
Cite = _create_tag_class("cite")
Code = _create_tag_class("code")
Col = _create_tag_class("col")
Colgroup = _create_tag_class("colgroup")
Data = _create_tag_class("data")
Datalist = _create_tag_class("datalist")
Dd = _create_tag_class("dd")
Del = _create_tag_class("del")
Details = _create_tag_class("details")
Dfn = _create_tag_class("dfn")
Dialog = _create_tag_class("dialog")
Div = _create_tag_class("div")
Dl = _create_tag_class("dl")
Dt = _create_tag_class("dt")
Em = _create_tag_class("em")
Embed = _create_tag_class("embed")
Fieldset = _create_tag_class("fieldset")
Figcaption = _create_tag_class("figcaption")
Figure = _create_tag_class("figure")
Footer = _create_tag_class("footer")
Form = _create_tag_class("form")
H1 = _create_tag_class("h1")
H2 = _create_tag_class("h2")
H3 = _create_tag_class("h3")
H4 = _create_tag_class("h4")
H5 = _create_tag_class("h5")
H6 = _create_tag_class("h6")
Head = _create_tag_class("head")
Header = _create_tag_class("header")
Hgroup = _create_tag_class("hgroup")
Hr = _create_tag_class("hr")
Html = _create_tag_class("html")
I = _create_tag_class("i")
Iframe = _create_tag_class("iframe")
Img = _create_tag_class("img")
Input = _create_tag_class("input")
Ins = _create_tag_class("ins")
Kbd = _create_tag_class("kbd")
Label = _create_tag_class("label")
Legend = _create_tag_class("legend")
Li = _create_tag_class("li")
Link = _create_tag_class("link")
Main = _create_tag_class("main")
Map = _create_tag_class("map")
Mark = _create_tag_class("mark")
Menu = _create_tag_class("menu")
Meta = _create_tag_class("meta")
Meter = _create_tag_class("meter")
Nav = _create_tag_class("nav")
Noscript = _create_tag_class("noscript")
Object = _create_tag_class("object")
Ol = _create_tag_class("ol")
Optgroup = _create_tag_class("optgroup")
Option = _create_tag_class("option")
Output = _create_tag_class("output")
P = _create_tag_class("p")
Param = _create_tag_class("param")
Picture = _create_tag_class("picture")
Pre = _create_tag_class("pre")
Progress = _create_tag_class("progress")
Q = _create_tag_class("q")
Rp = _create_tag_class("rp")
Rt = _create_tag_class("rt")
Ruby = _create_tag_class("ruby")
S = _create_tag_class("s")
Samp = _create_tag_class("samp")
Script = _create_tag_class("script")
Section = _create_tag_class("section")
Select = _create_tag_class("select")
Slot = _create_tag_class("slot")
Small = _create_tag_class("small")
Source = _create_tag_class("source")
Span = _create_tag_class("span")
Strong = _create_tag_class("strong")
Style = _create_tag_class("style")
Sub = _create_tag_class("sub")
Summary = _create_tag_class("summary")
Sup = _create_tag_class("sup")
Table = _create_tag_class("table")
Tbody = _create_tag_class("tbody")
Td = _create_tag_class("td")
Template = _create_tag_class("template")
Textarea = _create_tag_class("textarea")
Tfoot = _create_tag_class("tfoot")
Th = _create_tag_class("th")
Thead = _create_tag_class("thead")
Time = _create_tag_class("time")
Title = _create_tag_class("title")
Tr = _create_tag_class("tr")
Track = _create_tag_class("track")
U = _create_tag_class("u")
Ul = _create_tag_class("ul")
Var = _create_tag_class("var")
Video = _create_tag_class("video")
Wbr = _create_tag_class("wbr")

__all__ = [
    "VOID_ELEMENTS",
    "HTML5_ELEMENTS",
    "A",
    "Abbr",
    "Address",
    "Area",
    "Article",
    "Aside",
    "Audio",
    "B",
    "Base",
    "Bdi",
    "Bdo",
    "Blockquote",
    "Body",
    "Br",
    "Button",
    "Canvas",
    "Caption",
    "Cite",
    "Code",
    "Col",
    "Colgroup",
    "Data",
    "Datalist",
    "Dd",
    "Del",
    "Details",
    "Dfn",
    "Dialog",
    "Div",
    "Dl",
    "Dt",
    "Em",
    "Embed",
    "Fieldset",
    "Figcaption",
    "Figure",
    "Footer",
    "Form",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "Head",
    "Header",
    "Hgroup",
    "Hr",
    "Html",
    "I",
    "Iframe",
    "Img",
    "Input",
    "Ins",
    "Kbd",
    "Label",
    "Legend",
    "Li",
    "Link",
    "Main",
    "Map",
    "Mark",
    "Menu",
    "Meta",
    "Meter",
    "Nav",
    "Noscript",
    "Object",
    "Ol",
    "Optgroup",
    "Option",
    "Output",
    "P",
    "Param",
    "Picture",
    "Pre",
    "Progress",
    "Q",
    "Rp",
    "Rt",
    "Ruby",
    "S",
    "Samp",
    "Script",
    "Section",
    "Select",
    "Slot",
    "Small",
    "Source",
    "Span",
    "Strong",
    "Style",
    "Sub",
    "Summary",
    "Sup",
    "Table",
    "Tbody",
    "Td",
    "Template",
    "Textarea",
    "Tfoot",
    "Th",
    "Thead",
    "Time",
    "Title",
    "Tr",
    "Track",
    "U",
    "Ul",
    "Var",
    "Video",
    "Wbr",
]