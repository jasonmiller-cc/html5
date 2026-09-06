"""HTML5 document primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from typing import Any, Mapping


def doctype() -> str:
    """Return the HTML5 doctype string."""

    return "<!doctype html>"


def _normalize_attr_name(name: str) -> str:
    if name.endswith("_"):
        name = name[:-1]
    return name.replace("_", "-")


def _render_attributes(attributes: Mapping[str, Any]) -> str:
    rendered: list[str] = []
    for key, value in attributes.items():
        if value is None or value is False:
            continue
        attribute_name = _normalize_attr_name(key)
        if value is True:
            rendered.append(attribute_name)
        else:
            rendered.append(f'{attribute_name}="{escape(str(value), quote=True)}"')
    return (" " + " ".join(rendered)) if rendered else ""


class Node:
    """Base class for HTML document nodes."""

    def render(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class Text(Node):
    """Render escaped text content."""

    value: str

    def render(self) -> str:
        return escape(self.value)


@dataclass(frozen=True)
class Raw(Node):
    """Render raw HTML content without escaping."""

    value: str

    def render(self) -> str:
        return self.value


@dataclass(frozen=True)
class Comment(Node):
    """Render an HTML comment."""

    value: str

    def render(self) -> str:
        return f"<!--{self.value}-->"


@dataclass(frozen=True)
class Doctype(Node):
    """Render a doctype node."""

    value: str = "html"

    def render(self) -> str:
        return f"<!doctype {self.value}>"


@dataclass(frozen=True)
class Element(Node):
    """Render an HTML element with children and attributes."""

    tag: str
    children: tuple[Node | str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    void: bool = False

    def render(self) -> str:
        attributes = _render_attributes(self.attributes)
        if self.void:
            return f"<{self.tag}{attributes}>"

        inner_html = "".join(_coerce_node(child).render() for child in self.children)
        return f"<{self.tag}{attributes}>{inner_html}</{self.tag}>"


def _coerce_node(value: Node | str) -> Node:
    return value if isinstance(value, Node) else Text(str(value))


def text(value: str) -> Text:
    """Create an escaped text node."""

    return Text(value)


def raw(value: str) -> Raw:
    """Create a raw HTML node."""

    return Raw(value)


def comment(value: str) -> Comment:
    """Create an HTML comment node."""

    return Comment(value)


def doctype_node(value: str = "html") -> Doctype:
    """Create a doctype node."""

    return Doctype(value)


def element(tag: str, *children: Node | str, void: bool = False, **attributes: Any) -> Element:
    """Create an HTML element node."""

    return Element(tag=tag, children=children, attributes=attributes, void=void)


@dataclass
class HtmlDocument:
    """Represent a complete HTML document."""

    title: str = ""
    lang: str = "en"
    head_nodes: list[Node | str] = field(default_factory=list)
    body_nodes: list[Node | str] = field(default_factory=list)

    def add_head(self, *nodes: Node | str) -> "HtmlDocument":
        """Append nodes to the document head."""

        self.head_nodes.extend(nodes)
        return self

    def add_body(self, *nodes: Node | str) -> "HtmlDocument":
        """Append nodes to the document body."""

        self.body_nodes.extend(nodes)
        return self

    def render(self) -> str:
        """Render the full HTML document."""

        head_children: list[Node | str] = [element("meta", charset="utf-8", void=True)]
        if self.title:
            head_children.append(element("title", self.title))
        head_children.extend(self.head_nodes)

        body = element("body", *self.body_nodes)
        head = element("head", *head_children)
        html = element("html", head, body, lang=self.lang)
        return "\n".join([doctype(), html.render()])
