"""Sphinx configuration for the html5 package documentation."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

project = "html5"
author = "Jason Miller"
copyright = f"{datetime.now().year}, {author}"

from html5.version import __version__  # noqa: E402

release = __version__
version = release.rsplit(".", 1)[0]

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autosectionlabel_prefix_document = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "substitution",
]
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}
master_doc = "index"
html_theme = "furo"
html_title = "html5"
html_baseurl = "https://jasonmiller-cc.github.io/html5/"
html_static_path = ["_static"]
html_show_sourcelink = True
html_copy_source = True
html_use_index = True
html_split_index = False
htmlhelp_basename = "html5doc"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

def setup(app):
    """Register Sphinx-specific configuration hooks."""

    app.add_css_file("custom.css")

