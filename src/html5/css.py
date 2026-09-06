"""CSS3 stylesheet helpers."""

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
    """Base class for CSS document nodes."""

    def render(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class CSSComment(CSSNode):
    """Render a CSS comment."""

    value: str

    def render(self) -> str:
        return f"/* {self.value} */"


@dataclass(frozen=True)
class CSSDeclaration(CSSNode):
    """Render a CSS declaration pair."""

    property_name: str
    value: Any
    important: bool = False

    def render(self) -> str:
        if self.value is None:
            return ""
        suffix = " !important" if self.important else ""
        return f"{_normalize_property_name(self.property_name)}: {self.value}{suffix};"


def css_var(name: str) -> str:
    """Return a CSS var() reference for a custom property.

    Example: ``css_var("--size-1")`` → ``"var(--size-1)"``
    """
    return f"var({name})"


@dataclass(frozen=True, init=False)
class CSSCustomProperties(CSSNode):
    """Render a block of CSS custom properties (variables) on a selector.

    Pass a plain ``dict`` mapping ``--name`` strings to values.  The selector
    defaults to ``:root`` so the variables are available document-wide::

        CSSCustomProperties({"--size-1": "0.25rem", "--color-brand": "#005fcc"})
    """

    selector: str
    properties: tuple[tuple[str, Any], ...]

    def __init__(self, props: Mapping[str, Any], selector: str = ":root") -> None:
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "properties", tuple(props.items()))

    def render(self) -> str:
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
    """Render a sequence of declarations for use in a style attribute."""

    declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...] = ()

    def __init__(self, *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> None:
        object.__setattr__(self, "declarations", declarations)

    def render(self) -> str:
        return _render_declarations(self.declarations)


@dataclass(frozen=True)
class CSSLink(CSSNode):
    """Render a stylesheet link element."""

    href: str
    rel: str = "stylesheet"
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        return element("link", void=True, rel=self.rel, href=self.href, **self.attributes).render()


@dataclass(frozen=True, init=False)
class CSSRule(CSSNode):
    """Render a CSS selector rule."""

    selector: str
    declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...] = ()

    def __init__(self, selector: str, *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> None:
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "declarations", declarations)

    def render(self) -> str:
        body = _render_declarations(self.declarations)
        return f"{self.selector} {{ {body} }}" if body else f"{self.selector} {{}}"


@dataclass(frozen=True)
class CSSAtRule(CSSNode):
    """Render a generic CSS at-rule."""

    name: str
    prelude: str = ""
    body: tuple[CSSNode | str, ...] = ()
    block: bool = True

    def render(self) -> str:
        name = _normalize_at_rule_name(self.name)
        prelude = f" {self.prelude}" if self.prelude else ""
        if not self.block:
            return f"@{name}{prelude};"
        body = _render_nodes(self.body)
        return f"@{name}{prelude} {{ {body} }}" if body else f"@{name}{prelude} {{}}"


@dataclass(frozen=True, init=False)
class CSSImportRule(CSSAtRule):
    """Render a CSS @import rule."""

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
    """Render a CSS @media block."""

    def __init__(self, query: str, *rules: CSSNode | str) -> None:
        object.__setattr__(self, "name", "media")
        object.__setattr__(self, "prelude", query)
        object.__setattr__(self, "body", rules)
        object.__setattr__(self, "block", True)


@dataclass(frozen=True, init=False)
class CSSSupportsRule(CSSAtRule):
    """Render a CSS @supports block."""

    def __init__(self, condition: str, *rules: CSSNode | str) -> None:
        object.__setattr__(self, "name", "supports")
        object.__setattr__(self, "prelude", condition)
        object.__setattr__(self, "body", rules)
        object.__setattr__(self, "block", True)


@dataclass(frozen=True, init=False)
class CSSLayerRule(CSSAtRule):
    """Render a CSS @layer block."""

    def __init__(self, layer: str = "", *rules: CSSNode | str) -> None:
        object.__setattr__(self, "name", "layer")
        object.__setattr__(self, "prelude", layer)
        object.__setattr__(self, "body", rules)
        object.__setattr__(self, "block", True)


@dataclass(frozen=True, init=False)
class CSSKeyframe(CSSNode):
    """Render a single frame inside a CSS keyframes rule."""

    selector: str
    declarations: tuple[CSSDeclaration | tuple[str, Any] | Mapping[str, Any], ...] = ()

    def __init__(self, selector: str, *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any]) -> None:
        object.__setattr__(self, "selector", selector)
        object.__setattr__(self, "declarations", declarations)

    def render(self) -> str:
        body = _render_declarations(self.declarations)
        return f"{self.selector} {{ {body} }}" if body else f"{self.selector} {{}}"


@dataclass(frozen=True)
class CSSKeyframesRule(CSSNode):
    """Render a CSS @keyframes rule."""

    name: str
    frames: tuple[CSSKeyframe, ...] = ()

    def render(self) -> str:
        body = " ".join(frame.render() for frame in self.frames)
        return f"@keyframes {self.name} {{ {body} }}" if body else f"@keyframes {self.name} {{}}"


@dataclass(frozen=True)
class CSSStyleElement(CSSNode):
    """Render a complete <style> element."""

    stylesheet: CSSNode | str

    def render(self) -> str:
        css = self.stylesheet.render() if isinstance(self.stylesheet, CSSNode) else self.stylesheet
        return f"<style>{css}</style>"


BOOTSTRAP5_CSS_URL = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
TAILWIND_PLAY_CDN_URL = "https://cdn.tailwindcss.com"
GOOGLE_FONTS_PRECONNECT_URL = "https://fonts.googleapis.com"
GOOGLE_FONTS_STATIC_URL = "https://fonts.gstatic.com"


def bootstrap5_stylesheet(version: str = "5.3.3") -> CSSLink:
    """Return the Bootstrap 5 stylesheet link tag."""

    href = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/css/bootstrap.min.css"
    return CSSLink(href=href)


def tailwind_script() -> JSScript:
    """Return the Tailwind Play CDN script tag."""

    return JSScript(src=TAILWIND_PLAY_CDN_URL)


def google_fonts_url(
    *families: str,
    weights: Sequence[int] = (400, 500, 700),
    display: str = "swap",
    text: str | None = None,
) -> str:
    """Build a Google Fonts CSS2 URL for the requested families and weights."""

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
    """Return preconnect and stylesheet links for Google Fonts."""

    href = google_fonts_url(*families, weights=weights, display=display, text=text)
    return (
        CSSLink(href=GOOGLE_FONTS_PRECONNECT_URL, rel="preconnect"),
        CSSLink(href=GOOGLE_FONTS_STATIC_URL, rel="preconnect", attributes={"crossorigin": "anonymous"}),
        CSSLink(href=href),
    )


@dataclass
class CSSStyleSheet(CSSNode):
    rules: list[CSSNode | str] = field(default_factory=list)

    def add(self, *items: CSSNode | str) -> "CSSStyleSheet":
        self.rules.extend(items)
        return self

    def add_comment(self, value: str) -> "CSSStyleSheet":
        self.rules.append(CSSComment(value))
        return self

    def add_rule(
        self,
        selector: str,
        *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any],
        **keyword_declarations: Any,
    ) -> "CSSStyleSheet":
        combined_declarations = declarations + tuple(keyword_declarations.items())
        self.rules.append(CSSRule(selector, *combined_declarations))
        return self

    def add_import(self, url: str, media: str = "") -> "CSSStyleSheet":
        self.rules.append(CSSImportRule(url=url, media=media))
        return self

    def add_media(self, query: str, *rules: CSSNode | str) -> "CSSStyleSheet":
        self.rules.append(CSSMediaRule(query, *rules))
        return self

    def add_supports(self, condition: str, *rules: CSSNode | str) -> "CSSStyleSheet":
        self.rules.append(CSSSupportsRule(condition, *rules))
        return self

    def add_layer(self, layer: str = "", *rules: CSSNode | str) -> "CSSStyleSheet":
        self.rules.append(CSSLayerRule(layer, *rules))
        return self

    def add_keyframes(self, name: str, *frames: CSSKeyframe) -> "CSSStyleSheet":
        self.rules.append(CSSKeyframesRule(name=name, frames=frames))
        return self

    def add_custom_properties(
        self,
        props: Mapping[str, Any],
        selector: str = ":root",
    ) -> "CSSStyleSheet":
        self.rules.append(CSSCustomProperties(props, selector=selector))
        return self

    def add_raw(self, css: str) -> "CSSStyleSheet":
        self.rules.append(css)
        return self

    def render(self) -> str:
        parts: list[str] = []
        for rule in self.rules:
            parts.append(rule.render() if isinstance(rule, CSSNode) else rule)
        return "\n".join(parts)


def style_tag(stylesheet: CSSNode | str) -> Raw:
    """Render a stylesheet or CSS node into a raw <style> tag.

    If *stylesheet* is already a :class:`CSSStyleElement` (which renders its
    own ``<style>`` wrapper), return it as-is to avoid double-wrapping.
    """

    if isinstance(stylesheet, CSSStyleElement):
        return raw(stylesheet.render())
    css = stylesheet.render() if isinstance(stylesheet, CSSNode) else stylesheet
    return raw(f"<style>{css}</style>")


def inline_style(
    *declarations: CSSDeclaration | tuple[str, Any] | Mapping[str, Any],
    **keyword_declarations: Any,
) -> str:
    """Render declarations for a style attribute."""

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
