"""CSS3 stylesheet helpers.

This module provides a tree of immutable CSS node classes that mirrors the
structure of a CSS stylesheet: declarations, rules, at-rules, keyframes, and
complete stylesheets.  Every node implements ``render()`` which returns a
plain CSS string.

The mutable :class:`CSSStyleSheet` accumulates nodes and renders them as a
complete stylesheet.  Use it with :func:`style_tag` to embed styles in an
:class:`~html5.document.HtmlDocument`, or with
:class:`~html5.writer.MarkupWriter` to write a ``.css`` file to disk.

CSS custom properties (variables) are supported via :class:`CSSCustomProperties`
and the :func:`css_var` helper::

    from html5 import CSSStyleSheet, css_var

    sheet = (
        CSSStyleSheet()
        .add_custom_properties({"--size-1": "0.25rem", "--color-brand": "#005fcc"})
        .add_rule("button", ("padding", css_var("--size-1")))
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence
from urllib.parse import quote_plus

from .document import Raw, element, raw
from .js import JSScript


def _normalize_property_name(name: str) -> str:
    return name.replace("_", "-")


def _normalize_at_rule_name(name: str) -> str:
    return name.removeprefix("@").replace("_", "-")


class CSSNode:
    """Abstract base class for all CSS document nodes.

    Every subclass implements :meth:`render` which returns a plain CSS string.
    """

    def render(self) -> str:
        """Return the CSS string for this node.

        Raises:
            NotImplementedError: Subclasses must override this method.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class CSSComment(CSSNode):
    """A CSS comment node.

    Example::

        CSSComment("Reset styles").render()
        # "/* Reset styles */"
    """

    value: str

    def render(self) -> str:
        """Return the CSS comment string."""
        return f"/* {self.value} */"


@dataclass(frozen=True)
class CSSDeclaration(CSSNode):
    """A single CSS property–value declaration.

    Property names are normalised: underscores are replaced with hyphens, so
    ``font_size`` becomes ``font-size``.  CSS custom property names (starting
    with ``--``) pass through unchanged.

    Args:
        property_name: The CSS property name (e.g. ``"color"``, ``"--size-1"``).
        value: The CSS value.  ``None`` causes the declaration to render as an
            empty string (the declaration is skipped).
        important: If ``True`` appends ``!important`` to the value.

    Example::

        CSSDeclaration("font_size", "1rem").render()   # "font-size: 1rem;"
        CSSDeclaration("--size-1", "0.25rem").render() # "--size-1: 0.25rem;"
        CSSDeclaration("color", "red", important=True).render()
        # "color: red !important;"
    """

    property_name: str
    value: Any
    important: bool = False

    def render(self) -> str:
        """Return the CSS declaration string, or an empty string if value is None."""
        if self.value is None:
            return ""
        suffix = " !important" if self.important else ""
        return f"{_normalize_property_name(self.property_name)}: {self.value}{suffix};"


def css_var(name: str) -> str:
    """Return a CSS ``var()`` reference for a custom property.

    Args:
        name: The custom property name including the ``--`` prefix
            (e.g. ``"--size-1"``).

    Returns:
        A string of the form ``"var(--size-1)"``.

    Example::

        css_var("--color-brand")  # "var(--color-brand)"
    """
    return f"var({name})"


@dataclass(frozen=True, init=False)
class CSSCustomProperties(CSSNode):
    """A block of CSS custom properties (variables) on a selector.

    Renders a ``selector { --name: value; ... }`` block.  The selector
    defaults to ``:root`` so the variables are available document-wide.

    Pass a plain :class:`dict` mapping ``--name`` strings to their values.
    Use :func:`css_var` to reference them in other declarations.

    Args:
        props: A mapping of custom property names to values.
        selector: The CSS selector for the block.  Defaults to ``":root"``.

    Example::

        CSSCustomProperties(
            {"--size-1": "0.25rem", "--color-brand": "#005fcc"},
        ).render()
        # ":root { --size-1: 0.25rem; --color-brand: #005fcc; }"

        CSSCustomProperties({"--fg": "#fff"}, selector="[data-theme='dark']")
    """

    selector: str
    properties: tuple[tuple[str, Any], ...]

    def __init__(self, props: Mapping[str, Any], selector: str = ":root") -> None:
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "properties", tuple(props.items()))

    def render(self) -> str:
        """Return the CSS custom-properties block string."""
        if not self.properties:
            return f"{self.selector} {{}}"
        declarations = " ".join(f"{name}: {value};" for name, value in self.properties)
        return f"{self.selector} {{ {declarations} }}"


def _coerce_declaration(value: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> CSSDeclaration:
    if isinstance(value, CSSDeclaration):
        return value
    if isinstance(value, Mapping):
        if len(value) != 1:
            raise ValueError("CSS declaration mapping must contain exactly one property")
        property_name, property_value = next(iter(value.items()))
        return CSSDeclaration(property_name=str(property_name), value=property_value)
    property_name, property_value = value
    return CSSDeclaration(property_name=str(property_name), value=property_value)


def _render_declarations(declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...]) -> str:
    parts: list[str] = []
    for declaration in declarations:
        rendered = _coerce_declaration(declaration).render()
        if rendered:
            parts.append(rendered)
    return " ".join(parts)


def _render_nodes(nodes: tuple[CSSNode | str, ...]) -> str:
    parts: list[str] = []
    for node in nodes:
        parts.append(node.render() if isinstance(node, CSSNode) else str(node))
    return "\n".join(parts)


@dataclass(frozen=True, init=False)
class CSSInlineStyle(CSSNode):
    """A sequence of CSS declarations for use in a ``style`` attribute.

    Accepts the same declaration forms as :class:`CSSRule`: a
    :class:`CSSDeclaration`, a ``(name, value)`` tuple, or a single-key
    mapping.

    Use :func:`inline_style` for a convenience wrapper that returns a string
    directly suitable for the ``style`` attribute.

    Example::

        CSSInlineStyle(("color", "red"), ("font_size", "1rem")).render()
        # "color: red; font-size: 1rem;"
    """

    declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...] = ()

    def __init__(self, *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> None:
        object.__setattr__(self, "declarations", declarations)

    def render(self) -> str:
        """Return the inline style string (without the ``style=""`` wrapper)."""
        return _render_declarations(self.declarations)


@dataclass(frozen=True)
class CSSLink(CSSNode):
    """A ``<link rel="stylesheet">`` element node.

    Args:
        href: The URL of the stylesheet.
        rel: The ``rel`` attribute value.  Defaults to ``"stylesheet"``.
        attributes: Additional HTML attributes for the ``<link>`` element.

    Example::

        CSSLink(href="styles.css").render()
        # '<link rel="stylesheet" href="styles.css">'
    """

    href: str
    rel: str = "stylesheet"
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        """Return the rendered ``<link>`` element string."""
        return element("link", void=True, rel=self.rel, href=self.href, **self.attributes).render()


@dataclass(frozen=True, init=False)
class CSSRule(CSSNode):
    """A CSS selector rule with one or more declarations.

    Accepts three declaration forms:

    - A :class:`CSSDeclaration` instance.
    - A ``(property_name, value)`` tuple.
    - A single-key :class:`~collections.abc.Mapping` ``{"property_name": value}``.

    Property names are normalised: underscores become hyphens.

    Args:
        selector: The CSS selector string (e.g. ``".btn"``, ``"h1"``, ``":root"``).
        *declarations: One or more declarations in any accepted form.

    Example::

        CSSRule("body", ("margin", 0), ("font_family", "system-ui")).render()
        # "body { margin: 0; font-family: system-ui; }"
    """

    selector: str
    declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...] = ()

    def __init__(self, selector: str, *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> None:
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "declarations", declarations)

    def render(self) -> str:
        """Return the CSS rule string."""
        body = _render_declarations(self.declarations)
        return f"{self.selector} {{ {body} }}" if body else f"{self.selector} {{}}"


@dataclass(frozen=True)
class CSSAtRule(CSSNode):
    """A generic CSS at-rule (``@name prelude { body }`` or ``@name prelude;``).

    Use the specialised subclasses (:class:`CSSMediaRule`,
    :class:`CSSSupportsRule`, :class:`CSSLayerRule`, :class:`CSSImportRule`,
    :class:`CSSKeyframesRule`) for common at-rules.  Use this class directly
    for less common ones such as ``@charset``.

    Args:
        name: The at-rule name, with or without the leading ``@``.
            Underscores are replaced with hyphens.
        prelude: Optional text between the rule name and the block or semicolon.
        body: Child nodes or strings rendered inside the block.
        block: If ``True`` (default) renders a ``{ body }`` block; if ``False``
            renders a semicolon-terminated statement.

    Example::

        CSSAtRule("charset", '"UTF-8"', block=False).render()
        # '@charset "UTF-8";'
    """

    name: str
    prelude: str = ""
    body: tuple[CSSNode | str, ...] = ()
    block: bool = True

    def render(self) -> str:
        """Return the at-rule CSS string."""
        name = _normalize_at_rule_name(self.name)
        prelude = f" {self.prelude}" if self.prelude else ""
        if not self.block:
            return f"@{name}{prelude};"
        body = _render_nodes(self.body)
        return f"@{name}{prelude} {{ {body} }}" if body else f"@{name}{prelude} {{}}"


@dataclass(frozen=True, init=False)
class CSSImportRule(CSSAtRule):
    """A CSS ``@import`` rule.

    Args:
        url: The URL of the stylesheet to import.
        media: An optional media query string appended after the URL.

    Example::

        CSSImportRule("reset.css").render()
        # '@import url("reset.css");'

        CSSImportRule("print.css", media="print").render()
        # '@import url("print.css") print;'
    """

    def __init__(self, url: str, media: str = "") -> None:
        prelude = f'url("{url}")'
        if media:
            prelude = f"{prelude} {media}"
        object.__setattr__(self, "name", "import")
        object.__setattr__(self, "prelude", prelude)
        object.__setattr__(self, "body", ())
        object.__setattr__(self, "block", False)


@dataclass(frozen=True, init=False)
class CSSMediaRule(CSSAtRule):
    """A CSS ``@media`` block.

    Args:
        query: The media query string (e.g. ``"screen and (min-width: 40rem)"``).
        *rules: Child :class:`CSSNode` instances or CSS strings.

    Example::

        CSSMediaRule(
            "(prefers-color-scheme: dark)",
            CSSRule("body", ("background", "#000")),
        ).render()
        # "@media (prefers-color-scheme: dark) { body { background: #000; } }"
    """

    def __init__(self, query: str, *rules: CSSNode | str) -> None:
        object.__setattr__(self, "name", "media")
        object.__setattr__(self, "prelude", query)
        object.__setattr__(self, "body", rules)
        object.__setattr__(self, "block", True)


@dataclass(frozen=True, init=False)
class CSSSupportsRule(CSSAtRule):
    """A CSS ``@supports`` block.

    Args:
        condition: The supports condition (e.g. ``"(display: grid)"``).
        *rules: Child :class:`CSSNode` instances or CSS strings.

    Example::

        CSSSupportsRule(
            "(display: grid)",
            CSSRule("div", ("display", "grid")),
        ).render()
        # "@supports (display: grid) { div { display: grid; } }"
    """

    def __init__(self, condition: str, *rules: CSSNode | str) -> None:
        object.__setattr__(self, "name", "supports")
        object.__setattr__(self, "prelude", condition)
        object.__setattr__(self, "body", rules)
        object.__setattr__(self, "block", True)


@dataclass(frozen=True, init=False)
class CSSLayerRule(CSSAtRule):
    """A CSS ``@layer`` block.

    Args:
        layer: The layer name.  Omit for an anonymous layer.
        *rules: Child :class:`CSSNode` instances or CSS strings.

    Example::

        CSSLayerRule("utilities", CSSRule(".hidden", ("display", "none"))).render()
        # "@layer utilities { .hidden { display: none; } }"
    """

    def __init__(self, layer: str = "", *rules: CSSNode | str) -> None:
        object.__setattr__(self, "name", "layer")
        object.__setattr__(self, "prelude", layer)
        object.__setattr__(self, "body", rules)
        object.__setattr__(self, "block", True)


@dataclass(frozen=True, init=False)
class CSSKeyframe(CSSNode):
    """A single keyframe stop inside a :class:`CSSKeyframesRule`.

    Args:
        selector: The keyframe selector (e.g. ``"from"``, ``"to"``, ``"50%"``).
        *declarations: Declarations in any accepted form.

    Example::

        CSSKeyframe("from", ("opacity", 0)).render()
        # "from { opacity: 0; }"
    """

    selector: str
    declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...] = ()

    def __init__(self, selector: str, *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> None:
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "declarations", declarations)

    def render(self) -> str:
        """Return the keyframe CSS string."""
        body = _render_declarations(self.declarations)
        return f"{self.selector} {{ {body} }}" if body else f"{self.selector} {{}}"


@dataclass(frozen=True)
class CSSKeyframesRule(CSSNode):
    """A CSS ``@keyframes`` rule.

    Args:
        name: The animation name.
        frames: The keyframe stops as :class:`CSSKeyframe` instances.

    Example::

        CSSKeyframesRule(
            "fade",
            frames=(CSSKeyframe("from", ("opacity", 0)), CSSKeyframe("to", ("opacity", 1))),
        ).render()
        # "@keyframes fade { from { opacity: 0; } to { opacity: 1; } }"
    """

    name: str
    frames: tuple[CSSKeyframe, ...] = ()

    def render(self) -> str:
        """Return the ``@keyframes`` rule CSS string."""
        body = " ".join(frame.render() for frame in self.frames)
        return f"@keyframes {self.name} {{ {body} }}" if body else f"@keyframes {self.name} {{}}"


@dataclass(frozen=True)
class CSSStyleElement(CSSNode):
    """A complete ``<style>`` element wrapping a stylesheet or CSS node.

    Prefer :func:`style_tag` over this class directly, as :func:`style_tag`
    avoids double-wrapping when passed a :class:`CSSStyleElement`.

    Args:
        stylesheet: A :class:`CSSNode` or raw CSS string to wrap.

    Example::

        CSSStyleElement(CSSStyleSheet().add_rule("p", ("color", "red"))).render()
        # "<style>p { color: red; }</style>"
    """

    stylesheet: CSSNode | str

    def render(self) -> str:
        """Return the ``<style>`` element HTML string."""
        css = self.stylesheet.render() if isinstance(self.stylesheet, CSSNode) else self.stylesheet
        return f"<style>{css}</style>"


BOOTSTRAP5_CSS_URL = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
"""The jsDelivr CDN URL for Bootstrap 5.3.3 CSS."""

TAILWIND_PLAY_CDN_URL = "https://cdn.tailwindcss.com"
"""The Tailwind CSS Play CDN script URL."""

GOOGLE_FONTS_PRECONNECT_URL = "https://fonts.googleapis.com"
"""The Google Fonts API preconnect URL."""

GOOGLE_FONTS_STATIC_URL = "https://fonts.gstatic.com"
"""The Google Fonts static assets preconnect URL."""


def bootstrap5_stylesheet(version: str = "5.3.3") -> CSSLink:
    """Return a Bootstrap 5 stylesheet ``<link>`` node from jsDelivr.

    Args:
        version: The Bootstrap version string.  Defaults to ``"5.3.3"``.

    Returns:
        A :class:`CSSLink` pointing to the Bootstrap CSS CDN URL.
    """
    href = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/css/bootstrap.min.css"
    return CSSLink(href=href)


def tailwind_script() -> JSScript:
    """Return the Tailwind CSS Play CDN ``<script>`` node.

    Returns:
        A :class:`~html5.js.JSScript` loading the Tailwind Play CDN.
    """
    return JSScript(src=TAILWIND_PLAY_CDN_URL)


def google_fonts_url(
    *families: str,
    weights: Sequence[int] = (400, 500, 700),
    display: str = "swap",
    text: str | None = None,
) -> str:
    """Build a Google Fonts CSS2 API URL for the requested font families.

    Args:
        *families: One or more font family names (e.g. ``"Inter"``, ``"Open Sans"``).
        weights: The font weights to request.  Defaults to ``(400, 500, 700)``.
        display: The ``font-display`` value.  Defaults to ``"swap"``.
        text: If provided, restricts the character set to the given string for
            smaller downloads.

    Returns:
        A Google Fonts CSS2 URL string.

    Raises:
        ValueError: If no font families are provided.

    Example::

        google_fonts_url("Inter", "Open Sans", weights=(400, 700))
        # "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&..."
    """
    if not families:
        raise ValueError("At least one Google Fonts family is required")

    family_parts: list[str] = []
    weight_part = ";".join(str(weight) for weight in weights)
    for family in families:
        family_parts.append(f"family={quote_plus(family)}:wght@{weight_part}")

    params = [*family_parts, f"display={quote_plus(display)}"]
    if text is not None:
        params.append(f"text={quote_plus(text)}")
    return "https://fonts.googleapis.com/css2?" + "&".join(params)


def google_fonts_assets(
    *families: str,
    weights: Sequence[int] = (400, 500, 700),
    display: str = "swap",
    text: str | None = None,
) -> tuple[CSSLink, CSSLink, CSSLink]:
    """Return the three ``<link>`` nodes required to load Google Fonts.

    Returns a preconnect to ``fonts.googleapis.com``, a crossorigin preconnect
    to ``fonts.gstatic.com``, and the CSS stylesheet link — in the correct
    order for optimal font loading performance.

    Args:
        *families: One or more font family names.
        weights: Font weights to request.  Defaults to ``(400, 500, 700)``.
        display: The ``font-display`` strategy.  Defaults to ``"swap"``.
        text: Optional character subset string for smaller downloads.

    Returns:
        A 3-tuple of :class:`CSSLink` nodes: ``(preconnect, crossorigin_preconnect, stylesheet)``.

    Example::

        doc.add_head(*google_fonts_assets("Inter"))
    """
    href = google_fonts_url(*families, weights=weights, display=display, text=text)
    return (
        CSSLink(href=GOOGLE_FONTS_PRECONNECT_URL, rel="preconnect"),
        CSSLink(href=GOOGLE_FONTS_STATIC_URL, rel="preconnect", attributes={"crossorigin": "anonymous"}),
        CSSLink(href=href),
    )


@dataclass
class CSSStyleSheet(CSSNode):
    """A mutable CSS stylesheet that accumulates rules and renders them in order.

    Build a stylesheet by chaining the ``add_*`` methods, then pass it to
    :func:`style_tag` for embedding in an HTML document or to
    :class:`~html5.writer.MarkupWriter` for writing to disk.

    Example::

        from html5 import CSSStyleSheet, css_var, style_tag, HtmlDocument

        sheet = (
            CSSStyleSheet()
            .add_custom_properties({"--brand": "#005fcc", "--gap": "1rem"})
            .add_comment("Base styles")
            .add_import("reset.css")
            .add_rule("body", margin="0", font_family="system-ui")
            .add_rule("a", ("color", css_var("--brand")))
            .add_media("(prefers-color-scheme: dark)", CSSRule("body", ("background", "#111")))
        )
        doc = HtmlDocument(title="Example").add_head(style_tag(sheet))
    """

    rules: list[CSSNode | str] = field(default_factory=list)
    """The ordered list of CSS nodes in this stylesheet."""

    def add(self, *items: CSSNode | str) -> "CSSStyleSheet":
        """Append one or more raw nodes or strings to the stylesheet.

        Args:
            *items: :class:`CSSNode` instances or raw CSS strings.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.extend(items)
        return self

    def add_comment(self, value: str) -> "CSSStyleSheet":
        """Append a CSS comment.

        Args:
            value: The comment text (without ``/* */`` delimiters).

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(CSSComment(value))
        return self

    def add_rule(
        self,
        selector: str,
        *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any],
        **keyword_declarations: Any,
    ) -> "CSSStyleSheet":
        """Append a CSS selector rule.

        Declarations may be passed positionally (as :class:`CSSDeclaration`,
        tuples, or single-key mappings) or as keyword arguments.  Keyword
        argument names are normalised: underscores become hyphens.

        Args:
            selector: The CSS selector (e.g. ``"body"``, ``".btn"``).
            *declarations: Positional declarations.
            **keyword_declarations: Keyword declarations — each key becomes a
                CSS property name after underscore→hyphen normalisation.

        Returns:
            This stylesheet (for method chaining).

        Example::

            sheet.add_rule("body", margin="0", font_family="system-ui")
            sheet.add_rule("h1", ("font_size", "2rem"), ("color", "#111"))
        """
        combined_declarations = declarations + tuple(keyword_declarations.items())
        self.rules.append(CSSRule(selector, *combined_declarations))
        return self

    def add_custom_properties(
        self,
        props: Mapping[str, Any],
        selector: str = ":root",
    ) -> "CSSStyleSheet":
        """Append a CSS custom-properties block.

        Args:
            props: A mapping of ``--name`` strings to their CSS values.
            selector: The selector for the block.  Defaults to ``":root"``.

        Returns:
            This stylesheet (for method chaining).

        Example::

            sheet.add_custom_properties({"--size-1": "0.25rem", "--color-brand": "#005fcc"})
        """
        self.rules.append(CSSCustomProperties(props, selector=selector))
        return self

    def add_import(self, url: str, media: str = "") -> "CSSStyleSheet":
        """Append a CSS ``@import`` rule.

        Args:
            url: The URL of the stylesheet to import.
            media: An optional media query string.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(CSSImportRule(url=url, media=media))
        return self

    def add_media(self, query: str, *rules: CSSNode | str) -> "CSSStyleSheet":
        """Append a CSS ``@media`` block.

        Args:
            query: The media query string.
            *rules: Child nodes or CSS strings for the block body.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(CSSMediaRule(query, *rules))
        return self

    def add_supports(self, condition: str, *rules: CSSNode | str) -> "CSSStyleSheet":
        """Append a CSS ``@supports`` block.

        Args:
            condition: The supports condition string.
            *rules: Child nodes or CSS strings for the block body.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(CSSSupportsRule(condition, *rules))
        return self

    def add_layer(self, layer: str = "", *rules: CSSNode | str) -> "CSSStyleSheet":
        """Append a CSS ``@layer`` block.

        Args:
            layer: The layer name.  Pass an empty string for an anonymous layer.
            *rules: Child nodes or CSS strings for the block body.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(CSSLayerRule(layer, *rules))
        return self

    def add_keyframes(self, name: str, *frames: CSSKeyframe) -> "CSSStyleSheet":
        """Append a CSS ``@keyframes`` rule.

        Args:
            name: The animation name.
            *frames: :class:`CSSKeyframe` stops.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(CSSKeyframesRule(name=name, frames=frames))
        return self

    def add_raw(self, css: str) -> "CSSStyleSheet":
        """Append a raw CSS string.

        Use this for CSS that has no dedicated node class (e.g. a
        vendor-prefixed block or a one-off snippet).

        Args:
            css: A raw CSS string to insert verbatim.

        Returns:
            This stylesheet (for method chaining).
        """
        self.rules.append(css)
        return self

    def render(self) -> str:
        """Render all rules in order as a newline-joined CSS string."""
        parts: list[str] = []
        for rule in self.rules:
            parts.append(rule.render() if isinstance(rule, CSSNode) else rule)
        return "\n".join(parts)


def style_tag(stylesheet: CSSNode | str) -> Raw:
    """Wrap a stylesheet or CSS node in a ``<style>`` tag.

    If *stylesheet* is already a :class:`CSSStyleElement` (which renders its
    own ``<style>`` wrapper), it is returned as-is to prevent double-wrapping.

    Args:
        stylesheet: A :class:`CSSNode` or raw CSS string to embed.

    Returns:
        A :class:`~html5.document.Raw` node containing the ``<style>`` tag.

    Example::

        sheet = CSSStyleSheet().add_rule("body", margin="0")
        doc.add_head(style_tag(sheet))
    """
    if isinstance(stylesheet, CSSStyleElement):
        return raw(stylesheet.render())
    css = stylesheet.render() if isinstance(stylesheet, CSSNode) else stylesheet
    return raw(f"<style>{css}</style>")


def inline_style(
    *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any],
    **keyword_declarations: Any,
) -> str:
    """Render CSS declarations as a string for a ``style`` attribute.

    Args:
        *declarations: Positional declarations (:class:`CSSDeclaration`, tuples,
            or single-key mappings).
        **keyword_declarations: Keyword declarations with underscore→hyphen name
            normalisation.

    Returns:
        A CSS declaration string suitable for a ``style`` attribute value.

    Example::

        inline_style(("border_radius", "8px"), color="red")
        # "border-radius: 8px; color: red;"
    """
    return CSSInlineStyle(*(declarations + tuple(keyword_declarations.items()))).render()


__all__ = [
    "CSSAtRule",
    "CSSComment",
    "CSSCustomProperties",
    "CSSDeclaration",
    "CSSLink",
    "CSSImportRule",
    "CSSInlineStyle",
    "CSSKeyframe",
    "CSSKeyframesRule",
    "CSSLayerRule",
    "CSSMediaRule",
    "CSSNode",
    "CSSRule",
    "CSSStyleElement",
    "CSSStyleSheet",
    "CSSSupportsRule",
    "BOOTSTRAP5_CSS_URL",
    "GOOGLE_FONTS_PRECONNECT_URL",
    "GOOGLE_FONTS_STATIC_URL",
    "TAILWIND_PLAY_CDN_URL",
    "bootstrap5_stylesheet",
    "css_var",
    "google_fonts_assets",
    "google_fonts_url",
    "inline_style",
    "tailwind_script",
    "style_tag",
]
