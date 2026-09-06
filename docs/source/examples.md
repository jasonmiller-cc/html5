# Examples

## CSS custom properties (variables)

CSS custom properties let you define reusable values once and reference them
anywhere with ``var()``.  Use :class:`~html5.css.CSSCustomProperties` or the
:meth:`~html5.css.CSSStyleSheet.add_custom_properties` convenience method, and
:func:`~html5.css.css_var` to reference them:

```python
from html5 import CSSStyleSheet, HtmlDocument, css_var, style_tag

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
    .add_custom_properties(
        {"--color-brand": "#3b82f6"},
        selector="[data-theme='dark']",
    )
)

doc = HtmlDocument(title="Custom properties").add_head(style_tag(sheet))
```

Custom property names with hyphens (``--size-1``) are passed as plain dict
keys and rendered verbatim — no underscore conversion applies to them.

## HTML and CSS file loaders

Load existing HTML or CSS files back into html5 objects with
:func:`~html5.loader.html_loader` and :func:`~html5.loader.css_loader`:

```python
from html5 import css_loader, html_loader

# Read a CSS file → CSSStyleSheet (renders it back as-is)
sheet = css_loader("styles/site.css")
print(sheet.render())

# Read an HTML file → HtmlDocument (title, lang, head, body preserved)
doc = html_loader("dist/index.html")
print(doc.title)   # e.g. "My page"
print(doc.lang)    # e.g. "en"

# Extend the document and re-render
from html5 import Div, P
doc.add_body(Div(P("Appended after loading")))
print(doc.render())
```

The ``html_loader`` strips the ``<meta charset>`` tag (since
:meth:`~html5.document.HtmlDocument.render` always emits one) and preserves
the rest of the head and body as raw HTML nodes.

## Bootstrap 5

```python
from html5 import HtmlDocument, bootstrap5_stylesheet, bootstrap5_bundle_script

page = HtmlDocument(title="Bootstrap demo")
page.add_head(bootstrap5_stylesheet())
page.add_body("<main class='container py-4'>Hello Bootstrap</main>")
page.add_body(bootstrap5_bundle_script())
```

Bootstrap helpers are aimed at the standard CDN entry points:

- CSS: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css`
- JS bundle: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js`

## Tailwind CSS

```python
from html5 import HtmlDocument, tailwind_script

page = HtmlDocument(title="Tailwind demo")
page.add_head(tailwind_script())
page.add_body("<main class='mx-auto max-w-3xl p-6'>Hello Tailwind</main>")
```

The library uses the official Tailwind Play CDN script for browser-side use.

## Google Fonts

```python
from html5 import HtmlDocument, google_fonts_assets

page = HtmlDocument(title="Fonts demo")
page.add_head(*google_fonts_assets("Inter", "Open Sans"))
```

The helper emits a preconnect pair plus the fonts stylesheet URL so browsers
can establish connections early.

## JavaScript libraries

```python
from html5 import HtmlDocument, google_charts_loader, google_charts_package_loader

page = HtmlDocument(title="Charts demo")
page.add_head(google_charts_loader())
page.add_body(google_charts_package_loader(["corechart", "table"], callback="drawChart"))
```

Use :func:`~html5.js.javascript_link` and :func:`~html5.js.javascript_script`
for arbitrary external and inline scripts.

## Write files to disk

```python
from html5 import CSSStyleSheet, HtmlDocument, MarkupWriter

writer = MarkupWriter(root="build")
page = HtmlDocument(title="Saved page")
sheet = CSSStyleSheet().add_rule("body", margin="0")
writer.write_html("index.html", page)
writer.write_css("styles/site.css", sheet)
```

Use :meth:`~html5.writer.MarkupWriter.write_html` and
:meth:`~html5.writer.MarkupWriter.write_css` to persist rendered output under
a fixed root directory.  Path traversal outside the root is rejected.

## Complete document example

```python
from html5 import (
    CSSKeyframe,
    CSSRule,
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
    tailwind_script,
)

sheet = (
    CSSStyleSheet()
    .add_custom_properties({
        "--color-brand": "#005fcc",
        "--gap-md": "1.5rem",
    })
    .add_comment("Base styles")
    .add_import("reset.css")
    .add_rule("body", margin="0", font_family="system-ui")
    .add_rule("a", ("color", css_var("--color-brand")))
    .add_media(
        "(prefers-color-scheme: dark)",
        CSSRule(":root", ("--color-brand", "#60a5fa")),
    )
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
    .add_head(tailwind_script())
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
