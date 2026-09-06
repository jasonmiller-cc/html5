"""Utilities for writing rendered HTML and CSS to disk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class Renderable(Protocol):
    def render(self) -> str:
        raise NotImplementedError


@dataclass(slots=True)
class MarkupWriter:
    """Write rendered HTML and CSS content beneath a fixed root directory."""

    root: Path = Path(".")
    encoding: str = "utf-8"

    def write_text(self, path: str | Path, content: str) -> Path:
        """Write text content to a file below the configured root directory."""

        root = self.root.resolve()
        relative_path = Path(path)
        if relative_path.is_absolute():
            raise ValueError("path must be relative to the writer root")

        destination = (root / relative_path).resolve()
        if destination == root or root not in destination.parents:
            raise ValueError("path must be a file inside the writer root, not the root itself")

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding=self.encoding)
        return destination

    def write_html(self, path: str | Path, document: Renderable | str) -> Path:
        """Write rendered HTML to disk."""

        content = document if isinstance(document, str) else document.render()
        return self.write_text(path, content)

    def write_css(self, path: str | Path, stylesheet: Renderable | str) -> Path:
        """Write rendered CSS to disk."""

        content = stylesheet if isinstance(stylesheet, str) else stylesheet.render()
        return self.write_text(path, content)
