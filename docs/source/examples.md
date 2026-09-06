# Examples

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

The helper emits a preconnect pair plus the fonts stylesheet URL so browsers can connect early.

## JavaScript libraries

```python
from html5 import HtmlDocument, google_charts_loader, google_charts_package_loader

page = HtmlDocument(title="Charts demo")
page.add_head(google_charts_loader())
page.add_body(google_charts_package_loader(["corechart", "table"], callback="drawChart"))
```

The JavaScript helpers are generic enough for external script tags and common libraries such as Google Charts.

## Write files to disk

```python
from html5 import CSSStyleSheet, HtmlDocument, MarkupWriter

writer = MarkupWriter(root="build")
page = HtmlDocument(title="Saved page")
writer.write_html("index.html", page)
```

Use `write_html()` and `write_css()` to persist rendered output under a fixed root directory.
