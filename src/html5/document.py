"""HTML5 document primitives.

This module provides the core building blocks for constructing HTML5 documents
programmatically.  The primary entry point is :class:`HtmlDocument`, which
manages a title, a language attribute, head nodes, and body nodes and renders
the complete ``<!doctype html>`` output.

Leaf node types—:class:`Text`, :class:`Raw`, :class:`Comment`,
:class:`Doctype`, and :class:`Element`—all derive from :class:`Node` and
implement a ``render()`` method that returns a string of HTML.

Helper factory functions (:func:`text`, :func:`raw`, :func:`comment`,
:func:`doctype_node`, :func:`element`) are thin wrappers around the node
classes and are the preferred way to build nodes inline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from typing import Any, Mapping


def doctype() -> str:
    """Return the HTML5 doctype declaration string.

    Returns:
        The literal string ``"<!doctype html>"``.
    """
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
    """Abstract base class for all HTML document nodes.

    Every node implements :meth:`render` which returns a plain string of HTML.
    Leaf nodes are immutable frozen dataclasses; :class:`HtmlDocument` is the
    only mutable container.
    """

    def render(self) -> str:
        """Return the HTML string for this node.

        Raises:
            NotImplementedError: Subclasses must override this method.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class Text(Node):
    """An HTML-escaped text node.

    The *value* is escaped with :func:`html.escape` so that characters such as
    ``<``, ``>``, and ``&`` are converted to their HTML entities and cannot be
    interpreted as markup.

    Example::

        Text("Hello <world>").render()  # "Hello &lt;world&gt;"
    """

    value: str

    def render(self) -> str:
        """Return the HTML-escaped text string."""
        return escape(self.value)


@dataclass(frozen=True)
class Raw(Node):
    """A raw HTML node whose content is inserted without escaping.

    Use this only for content you trust completely — for example HTML rendered
    by another part of this library.  User-supplied strings should use
    :class:`Text` instead.

    Example::

        Raw("<strong>bold</strong>").render()  # "<strong>bold</strong>"
    """

    value: str

    def render(self) -> str:
        """Return the raw HTML string unchanged."""
        return self.value


@dataclass(frozen=True)
class Comment(Node):
    """An HTML comment node.

    Example::

        Comment(" TODO: remove this ").render()  # "<!-- TODO: remove this -->"
    """

    value: str

    def render(self) -> str:
        """Return the HTML comment string."""
        return f"<!--{self.value}-->"


@dataclass(frozen=True)
class Doctype(Node):
    """A doctype declaration node.

    Defaults to the standard HTML5 doctype.  Pass a custom *value* for
    legacy or XHTML doctypes.

    Example::

        Doctype().render()         # "<!doctype html>"
        Doctype("html").render()   # "<!doctype html>"
    """

    value: str = "html"

    def render(self) -> str:
        """Return the doctype declaration string."""
        return f"<!doctype {self.value}>"


@dataclass(frozen=True)
class Element(Node):
    """An HTML element with optional children and attributes.

    Attribute names follow Python identifier rules with two normalisation
    steps applied automatically:

    - A trailing underscore is stripped (``class_`` → ``class``).
    - Remaining underscores are replaced with hyphens (``data_foo`` → ``data-foo``).

    Attribute values follow these rules:

    - ``None`` or ``False`` — the attribute is omitted entirely.
    - ``True`` — the attribute is rendered as a boolean attribute (no value).
    - Any other value — rendered as a quoted string, HTML-escaped.

    Void elements (``<br>``, ``<img>``, ``<input>``, …) are rendered without a
    closing tag when *void* is ``True``.

    Example::

        Element("p", (Text("Hello"),), {"class": "lead"}).render()
        # '<p class="lead">Hello</p>'

        Element("br", void=True).render()
        # '<br>'
    """

    tag: str
    children: tuple[Node | str, ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    void: bool = False

    def render(self) -> str:
        """Return the rendered HTML element string."""
        attributes = _render_attributes(self.attributes)
        if self.void:
            return f"<{self.tag}{attributes}>"

        inner_html = "".join(_coerce_node(child).render() for child in self.children)
        return f"<{self.tag}{attributes}>{inner_html}</{self.tag}>"


def _coerce_node(value: Node | str) -> Node:
    return value if isinstance(value, Node) else Text(str(value))


def text(value: str) -> Text:
    """Create an HTML-escaped text node.

    Args:
        value: The plain text string to escape and render.

    Returns:
        A :class:`Text` node.
    """
    return Text(value)


def raw(value: str) -> Raw:
    """Create a raw (unescaped) HTML node.

    Args:
        value: A trusted HTML string to insert verbatim.

    Returns:
        A :class:`Raw` node.
    """
    return Raw(value)


def comment(value: str) -> Comment:
    """Create an HTML comment node.

    Args:
        value: The comment text (without the ``<!--`` / ``-->`` delimiters).

    Returns:
        A :class:`Comment` node.
    """
    return Comment(value)


def doctype_node(value: str = "html") -> Doctype:
    """Create a doctype declaration node.

    Args:
        value: The doctype identifier.  Defaults to ``"html"`` for HTML5.

    Returns:
        A :class:`Doctype` node.
    """
    return Doctype(value)


def element(tag: str, *children: Node | str, void: bool = False, **attributes: Any) -> Element:
    """Create an HTML element node.

    Attribute names are normalised: trailing underscores are stripped and
    remaining underscores are replaced with hyphens, so ``data_value="x"``
    becomes ``data-value="x"`` and ``class_="btn"`` becomes ``class="btn"``.

    Args:
        tag: The HTML tag name (e.g. ``"div"``, ``"span"``).
        *children: Child nodes or plain strings.  Strings are text-escaped
            automatically.
        void: If ``True`` the element is rendered without a closing tag.
        **attributes: HTML attributes as keyword arguments.

    Returns:
        An :class:`Element` node.

    Example::

        element("a", "Click me", href="/home", class_="nav-link").render()
        # '<a href="/home" class="nav-link">Click me</a>'
    """
    return Element(tag=tag, children=children, attributes=attributes, void=void)


@dataclass
class HtmlDocument:
    """A complete, renderable HTML5 document.

    The document always emits a ``<!doctype html>`` declaration and a
    ``<meta charset="utf-8">`` tag.  The *title* is placed inside ``<title>``
    in the document head.  Additional head and body content is appended with
    :meth:`add_head` and :meth:`add_body`.

    Example::

        from html5 import HtmlDocument, Div, H1, style_tag, CSSStyleSheet

        sheet = CSSStyleSheet().add_rule("body", margin="0")
        doc = (
            HtmlDocument(title="My page")
            .add_head(style_tag(sheet))
            .add_body(Div(H1("Hello, world!")))
        )
        print(doc.render())
    """

    title: str = ""
    """The page title placed inside ``<title>`` in the document head."""

    lang: str = "en"
    """The ``lang`` attribute on the root ``<html>`` element.  Defaults to ``"en"``."""

    head_nodes: list[Node | str] = field(default_factory=list)
    """Nodes appended to the document ``<head>`` after the charset meta and title."""

    body_nodes: list[Node | str] = field(default_factory=list)
    """Nodes placed inside the document ``<body>``."""

    def add_head(self, *nodes: Node | str) -> "HtmlDocument":
        """Append one or more nodes to the document head.

        Args:
            *nodes: :class:`Node` instances or raw HTML strings to add.

        Returns:
            This document (for method chaining).
        """
        self.head_nodes.extend(nodes)
        return self

    def add_body(self, *nodes: Node | str) -> "HtmlDocument":
        """Append one or more nodes to the document body.

        Args:
            *nodes: :class:`Node` instances or raw HTML strings to add.

        Returns:
            This document (for method chaining).
        """
        self.body_nodes.extend(nodes)
        return self

    def render(self) -> str:
        """Render the complete HTML5 document as a string.

        Always prepends ``<!doctype html>`` and includes ``<meta charset="utf-8">``.

        Returns:
            The full HTML document string.
        """
        head_children: list[Node | str] = [element("meta", charset="utf-8", void=True)]
        if self.title:
            head_children.append(element("title", self.title))
        head_children.extend(self.head_nodes)

        body = element("body", *self.body_nodes)
        head = element("head", *head_children)
        html = element("html", head, body, lang=self.lang)
        return "\n".join([doctype(), html.render()])
