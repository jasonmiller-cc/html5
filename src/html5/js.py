"""JavaScript helpers for HTML documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .document import Raw, element, raw


class JSNode:
    """Base class for JavaScript document nodes."""

    def render(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class JSScript(JSNode):
    """Render an inline or external JavaScript script tag."""

    src: str | None = None
    code: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        if self.src is not None:
            return element("script", src=self.src, **self.attributes).render()
        return element("script", raw(self.code), **self.attributes).render()


@dataclass(frozen=True)
class JSLink(JSNode):
    """Render an external script tag."""

    src: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        return element("script", src=self.src, **self.attributes).render()


def javascript_script(code: str, **attributes: Any) -> JSScript:
    """Create an inline script node."""

    return JSScript(code=code, attributes=attributes)


def javascript_link(src: str, **attributes: Any) -> JSLink:
    """Create an external script node."""

    return JSLink(src=src, attributes=attributes)


def bootstrap5_bundle_script(version: str = "5.3.3") -> JSLink:
    """Return the Bootstrap 5 bundle script tag."""

    href = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/js/bootstrap.bundle.min.js"
    return javascript_link(href)


def google_charts_loader(version: str = "51") -> JSLink:
    """Return the Google Charts loader script tag."""

    src = f"https://www.gstatic.com/charts/loader.js?ver={version}"
    return javascript_link(src)


def google_charts_package_loader(packages: Sequence[str], callback: str | None = None) -> JSScript:
    """Return an inline Google Charts package loader snippet."""

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
    "JSLink",
    "JSNode",
    "JSScript",
    "bootstrap5_bundle_script",
    "google_charts_loader",
    "google_charts_package_loader",
    "javascript_link",
    "javascript_script",
]
