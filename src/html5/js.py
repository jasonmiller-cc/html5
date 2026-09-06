"""JavaScript helpers for HTML documents.

Provides :class:`JSScript` and convenience factory functions for common
JavaScript patterns: external script tags, inline scripts, Bootstrap 5 bundle,
and Google Charts loaders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .document import raw, element


class JSNode:
    """Abstract base class for JavaScript document nodes.

    Every subclass implements :meth:`render` which returns an HTML string.
    """

    def render(self) -> str:
        """Return the HTML string for this node.

        Raises:
            NotImplementedError: Subclasses must override this method.
        """
        raise NotImplementedError


@dataclass(frozen=True)
class JSScript(JSNode):
    """Render an inline or external JavaScript ``<script>`` tag.

    Set *src* for an external script, or *code* for an inline script.
    Setting both raises :exc:`ValueError`.  Additional HTML attributes
    (e.g. ``defer``, ``type``) may be passed via *attributes*.

    Args:
        src: URL for an external script.  Mutually exclusive with *code*.
        code: Inline JavaScript source.  Mutually exclusive with *src*.
        attributes: Extra HTML attributes for the ``<script>`` element.

    Raises:
        ValueError: If both *src* and *code* are provided.

    Example::

        JSScript(src="https://example.com/app.js").render()
        # '<script src="https://example.com/app.js"></script>'

        JSScript(code="console.log('hi')").render()
        # "<script>console.log('hi')</script>"
    """

    src: str | None = None
    code: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.src is not None and self.code:
            raise ValueError(
                "JSScript cannot set both 'src' and 'code'; use one or the other"
            )

    def render(self) -> str:
        """Return the rendered ``<script>`` element HTML string."""
        if self.src is not None:
            return element("script", src=self.src, **self.attributes).render()
        return element("script", raw(self.code), **self.attributes).render()


def javascript_script(code: str, **attributes: Any) -> JSScript:
    """Create an inline ``<script>`` node.

    Args:
        code: The JavaScript source code to embed inline.
        **attributes: Extra HTML attributes for the ``<script>`` element.

    Returns:
        A :class:`JSScript` node with inline code.

    Example::

        javascript_script("console.log('hello')").render()
        # "<script>console.log('hello')</script>"
    """
    return JSScript(code=code, attributes=attributes)


def javascript_link(src: str, **attributes: Any) -> JSScript:
    """Create an external ``<script>`` node.

    Args:
        src: The URL of the external JavaScript file.
        **attributes: Extra HTML attributes for the ``<script>`` element
            (e.g. ``defer=True``, ``crossorigin="anonymous"``).

    Returns:
        A :class:`JSScript` node referencing an external URL.

    Example::

        javascript_link("https://example.com/app.js", defer=True).render()
        # '<script src="https://example.com/app.js" defer></script>'
    """
    return JSScript(src=src, attributes=attributes)


def bootstrap5_bundle_script(version: str = "5.3.3") -> JSScript:
    """Return the Bootstrap 5 bundle ``<script>`` node from jsDelivr.

    The bundle includes Popper.js, so no separate Popper script is required.

    Args:
        version: The Bootstrap version string.  Defaults to ``"5.3.3"``.

    Returns:
        A :class:`JSScript` loading the Bootstrap bundle from jsDelivr CDN.
    """
    href = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/js/bootstrap.bundle.min.js"
    return javascript_link(href)


def google_charts_loader(version: str = "51") -> JSScript:
    """Return the Google Charts loader ``<script>`` node.

    This loads the Google Charts core loader.  Call
    :func:`google_charts_package_loader` separately to request specific chart
    packages once the loader is present.

    Args:
        version: The Google Charts loader version.  Defaults to ``"51"``.

    Returns:
        A :class:`JSScript` loading the Google Charts loader from gstatic.com.
    """
    src = f"https://www.gstatic.com/charts/loader.js?ver={version}"
    return javascript_link(src)


def google_charts_package_loader(packages: Sequence[str], callback: str | None = None) -> JSScript:
    """Return an inline Google Charts package-load snippet.

    Renders an inline ``<script>`` that calls ``google.charts.load()`` for the
    specified packages.  Optionally registers a callback via
    ``google.charts.setOnLoadCallback()``.

    Args:
        packages: A sequence of Google Charts package names to load
            (e.g. ``["corechart", "table"]``).
        callback: Optional name of a JavaScript function to register as the
            on-load callback.

    Returns:
        A :class:`JSScript` with the inline Google Charts loader snippet.

    Example::

        google_charts_package_loader(["corechart"], callback="drawChart")
        # Renders an inline script calling google.charts.load(...)
    """
    package_list = ", ".join(f'"{package}"' for package in packages)
    callback_line = f"google.charts.setOnLoadCallback({callback});" if callback else ""
    code = (
        "google.charts.load('current', {packages: ["
        f"{package_list}"
        "]});\n"
        f"{callback_line}"
    )
    return javascript_script(code.strip())


__all__ = [
    "JSNode",
    "JSScript",
    "bootstrap5_bundle_script",
    "google_charts_loader",
    "google_charts_package_loader",
    "javascript_link",
    "javascript_script",
]
