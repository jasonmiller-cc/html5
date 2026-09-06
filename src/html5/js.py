"""JavaScript helpers for HTML documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .document import raw, element


class JSNode:
    """Base class for JavaScript document nodes."""

    def render(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class JSScript(JSNode):
    """Render an inline or external JavaScript script tag.

    Set *src* for an external script, or *code* for an inline script.
    Setting both raises :exc:`ValueError`.
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
        if self.src is not None:
            return element("script", src=self.src, **self.attributes).render()
        return element("script", raw(self.code), **self.attributes).render()


def javascript_script(code: str, **attributes: Any) -> JSScript:
    """Create an inline script node."""
    return JSScript(code=code, attributes=attributes)


def javascript_link(src: str, **attributes: Any) -> JSScript:
    """Create an external script node."""
    return JSScript(src=src, attributes=attributes)


def bootstrap5_bundle_script(version: str = "5.3.3") -> JSScript:
    """Return the Bootstrap 5 bundle script tag."""
    href = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist/js/bootstrap.bundle.min.js"
    return javascript_link(href)


def google_charts_loader(version: str = "51") -> JSScript:
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
    "JSNode",
    "JSScript",
    "bootstrap5_bundle_script",
    "google_charts_loader",
    "google_charts_package_loader",
    "javascript_link",
    "javascript_script",
]
