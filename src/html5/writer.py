"""Utilities for writing rendered HTML and CSS to disk.

:class:`MarkupWriter` provides a safe, root-anchored disk writer that prevents
path traversal outside a configured base directory.  Pass rendered HTML or CSS
strings, or any object with a ``render()`` method, and the writer handles
directory creation and encoding.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class Renderable(Protocol):
    """Protocol for objects that can render themselves to a string."""

    def render(self) -> str:
        """Return the rendered string representation of this object."""
        raise NotImplementedError


@dataclass(slots=True)
class MarkupWriter:
    """Write rendered HTML and CSS content beneath a fixed root directory.

    All paths passed to write methods must be relative to *root*.  Absolute
    paths and ``..`` traversal that would escape *root* are rejected with
    :exc:`ValueError`.  Parent directories are created automatically.

    Args:
        root: The base directory under which all files are written.
            Defaults to the current working directory (``"."``).
        encoding: The text encoding for written files.  Defaults to
            ``"utf-8"``.

    Example::

        from html5 import CSSStyleSheet, HtmlDocument, MarkupWriter

        writer = MarkupWriter(root="build")
        doc = HtmlDocument(title="Hello").add_body("<p>Hello</p>")
        sheet = CSSStyleSheet().add_rule("body", margin="0")

        writer.write_html("index.html", doc)
        writer.write_css("styles/site.css", sheet)
    """

    root: Path = Path(".")
    encoding: str = "utf-8"

    def write_text(self, path: str | Path, content: str) -> Path:
        """Write a text string to a file beneath the root directory.

        Args:
            path: A relative path (from *root*) for the output file.
            content: The text content to write.

        Returns:
            The absolute :class:`~pathlib.Path` of the written file.

        Raises:
            ValueError: If *path* is absolute or would escape the root
                directory via ``..`` traversal.
        """
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
        """Write rendered HTML to a file beneath the root directory.

        Args:
            path: A relative path for the output ``.html`` file.
            document: An object with a ``render()`` method (e.g.
                :class:`~html5.document.HtmlDocument`) or a plain HTML string.

        Returns:
            The absolute :class:`~pathlib.Path` of the written file.
        """
        content = document if isinstance(document, str) else document.render()
        return self.write_text(path, content)

    def write_css(self, path: str | Path, stylesheet: Renderable | str) -> Path:
        """Write rendered CSS to a file beneath the root directory.

        Args:
            path: A relative path for the output ``.css`` file.
            stylesheet: An object with a ``render()`` method (e.g.
                :class:`~html5.css.CSSStyleSheet`) or a plain CSS string.

        Returns:
            The absolute :class:`~pathlib.Path` of the written file.
        """
        content = stylesheet if isinstance(stylesheet, str) else stylesheet.render()
        return self.write_text(path, content)
