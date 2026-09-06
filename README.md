# html5

A Python toolkit for building HTML5 documents, CSS3 stylesheets, and JavaScript assets programmatically.

[![PyPI](https://img.shields.io/pypi/v/html5cc)](https://pypi.org/project/html5cc/)
[![Python](https://img.shields.io/pypi/pyversions/html5cc)](https://pypi.org/project/html5cc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jasonmiller-cc.github.io/html5/)

Documentation: [jasonmiller-cc.github.io/html5](https://jasonmiller-cc.github.io/html5/)

## Features

- **HTML5 element classes** for every standard tag (`Div`, `H1`, `Img`, …), with automatic attribute normalisation (`class_` → `class`, `data_value` → `data-value`).
- **CSS3 helpers** — rules, at-rules (`@media`, `@supports`, `@layer`, `@keyframes`, `@import`), inline styles, and CSS custom properties.
- **CSS custom properties (variables)** — define `--name: value` blocks on any selector and reference them with `var()`.
- **CDN helpers** — Bootstrap 5, Tailwind CSS Play CDN, Google Fonts, Google Charts.
- **JavaScript helpers** — external and inline script tags, Bootstrap 5 bundle, Google Charts loaders.
- **File loaders** — read HTML and CSS files back into `HtmlDocument` and `CSSStyleSheet` objects.
- **Disk writer** — safe, root-anchored writer for rendering HTML and CSS to disk.
- **Typed** — fully annotated with inline types; ships a `py.typed` marker for mypy/pyright.

## Installation

`html5cc` is published to [PyPI](https://pypi.org/project/html5cc/). The import name is `html5`.

```bash
pip install html5cc
```

**requirements.txt**

```text
html5cc==0.4.0
```

**pyproject.toml (uv / pip)**

```toml
[project]
dependencies = ["html5cc>=0.4.0"]
```

**Poetry**

```toml
[tool.poetry.dependencies]
python = "^3.10"
html5cc = "^0.4.0"
```

See the [Installation docs](https://jasonmiller-cc.github.io/html5/installation.html) for full details.

## Quick start

```python
from html5 import (
    CSSKeyframe,
    CSSStyleSheet,
    Div,
    H1,
    HtmlDocument,
    Img,
    MarkupWriter,
    bootstrap5_bundle_script,
    bootstrap5_stylesheet,
    css_var,
    google_fonts_assets,
    inline_style,
    style_tag,
)

sheet = (
    CSSStyleSheet()
    .add_custom_properties({
        "--color-brand": "#005fcc",
        "--gap-md": "1.5rem",
    })
    .add_comment("Base styles")
    .add_rule("body", margin="0", font_family="system-ui")
    .add_rule("a", ("color", css_var("--color-brand")))
    .add_keyframes(
        "fade",
        CSSKeyframe("from", ("opacity", 0)),
        CSSKeyframe("to", ("opacity", 1)),
    )
)

doc = (
    HtmlDocument(title="Hello html5cc")
    .add_head(style_tag(sheet))
    .add_head(*google_fonts_assets("Inter"))
    .add_head(bootstrap5_stylesheet())
    .add_head(bootstrap5_bundle_script())
    .add_body(
        Div(
            H1("Hello, world!"),
            Img(src="hero.png", style=inline_style(("border_radius", "8px"))),
            class_="container py-4",
        )
    )
)

writer = MarkupWriter(root="dist")
writer.write_html("index.html", doc)
writer.write_css("site.css", sheet)
```

## CSS custom properties

Define CSS variables on `:root` (or any selector) and reference them with `var()`:

```python
from html5 import CSSCustomProperties, CSSStyleSheet, css_var, style_tag

sheet = (
    CSSStyleSheet()
    .add_custom_properties({
        "--size-1": "0.25rem",
        "--size-2": "0.5rem",
        "--color-brand": "#005fcc",
        "--radius": "4px",
    })
    .add_rule(
        "button",
        ("padding", f"{css_var('--size-1')} {css_var('--size-2')}"),
        ("background", css_var("--color-brand")),
        ("border_radius", css_var("--radius")),
    )
    # Override for dark theme
    .add_custom_properties(
        {"--color-brand": "#3b82f6"},
        selector="[data-theme='dark']",
    )
)
```

Renders as:

```css
:root { --size-1: 0.25rem; --size-2: 0.5rem; --color-brand: #005fcc; --radius: 4px; }
button { padding: var(--size-1) var(--size-2); background: var(--color-brand); border-radius: var(--radius); }
[data-theme='dark'] { --color-brand: #3b82f6; }
```

## File loaders

Read existing HTML and CSS files back into document objects:

```python
from html5 import css_loader, html_loader

# Load a CSS file → CSSStyleSheet
sheet = css_loader("styles/site.css")

# Load an HTML file → HtmlDocument (title, lang, head, body preserved)
doc = html_loader("dist/index.html")
print(doc.title)  # "My page"
print(doc.lang)   # "en"

# Extend the loaded document and re-render
from html5 import Div, P
doc.add_body(Div(P("Appended content")))
```

## Bootstrap 5

```python
from html5 import HtmlDocument, bootstrap5_stylesheet, bootstrap5_bundle_script

page = (
    HtmlDocument(title="Bootstrap demo")
    .add_head(bootstrap5_stylesheet())
    .add_body("<main class='container py-4'>Hello Bootstrap</main>")
    .add_body(bootstrap5_bundle_script())
)
```

## Tailwind CSS

```python
from html5 import HtmlDocument, tailwind_script

page = (
    HtmlDocument(title="Tailwind demo")
    .add_head(tailwind_script())
    .add_body("<main class='mx-auto max-w-3xl p-6'>Hello Tailwind</main>")
)
```

## Google Fonts

```python
from html5 import HtmlDocument, google_fonts_assets

page = HtmlDocument(title="Fonts demo")
page.add_head(*google_fonts_assets("Inter", "Open Sans"))
# google_fonts_assets returns (preconnect, crossorigin preconnect, stylesheet)
```

## JavaScript helpers

```python
from html5 import javascript_link, javascript_script

# External script
javascript_link("https://example.com/app.js", defer=True)

# Inline script
javascript_script("console.log('hello')")
```

## Disk writer

```python
from html5 import MarkupWriter, HtmlDocument, CSSStyleSheet

writer = MarkupWriter(root="build")
writer.write_html("index.html", HtmlDocument(title="Page"))
writer.write_css("styles/site.css", CSSStyleSheet().add_rule("body", margin="0"))
```

Paths that traverse outside the root directory are rejected with `ValueError`.

## Attribute normalisation

Keyword attribute names are normalised automatically:

- Trailing underscore stripped: `class_="btn"` → `class="btn"`
- Underscores replaced with hyphens: `data_value="x"` → `data-value="x"`
- `None` or `False` — attribute omitted entirely
- `True` — rendered as a boolean attribute (no value)

```python
from html5 import element

element("input", type="checkbox", checked=True, disabled=False).render()
# '<input type="checkbox" checked>'
```

## Module layout

| Module | Contents |
|---|---|
| `html5.document` | `Node`, `Element`, `HtmlDocument`, `Text`, `Raw`, `Comment` |
| `html5.css` | `CSSStyleSheet`, `CSSRule`, `CSSCustomProperties`, `css_var`, at-rules, keyframes |
| `html5.js` | `JSScript`, Bootstrap 5, Google Charts helpers |
| `html5.loader` | `html_loader`, `css_loader` |
| `html5.writer` | `MarkupWriter` |
| `html5.elements` | All standard HTML5 tag classes (`Div`, `H1`, `Img`, …) |
| `html5.version` | `__version__` |

## Versioning

This project uses semantic versioning. The current version is `0.4.0`. See [CHANGELOG.md](CHANGELOG.md) for the full release history.
