# html5

Small Python helpers for building HTML5 documents, CSS, and JavaScript assets from Python.

Documentation is published on GitHub Pages at [jasonmiller-cc.github.io/html5](https://jasonmiller-cc.github.io/html5/).

The package ships with HTML5 element classes, CSS node classes, JavaScript helpers, CDN helpers for Bootstrap 5 and Tailwind, optimized Google Fonts helpers, a disk writer, and semantic version metadata.

## Example

```python
from html5 import (
    CSSDeclaration,
    CSSKeyframe,
    CSSStyleSheet,
    Div,
    H1,
    HtmlDocument,
    Img,
    MarkupWriter,
    bootstrap5_bundle_script,
    bootstrap5_stylesheet,
    google_charts_loader,
    google_charts_package_loader,
    google_fonts_assets,
    inline_style,
    tailwind_script,
)

styles = CSSStyleSheet()
styles.add_comment("base styles")
styles.add_import("reset.css")
styles.add_rule("body", margin="0", font_family="system-ui")
styles.add_rule("h1", color="#1f2937")
styles.add_media("screen and (min-width: 40rem)", CSSDeclaration("color", "black"))
styles.add_keyframes("fade", CSSKeyframe("from", ("opacity", 0)), CSSKeyframe("to", ("opacity", 1)))

doc = (
    HtmlDocument(title="Hello HTML5")
    .add_head(*google_fonts_assets("Inter"))
    .add_head(bootstrap5_stylesheet())
    .add_head(tailwind_script())
    .add_head(bootstrap5_bundle_script())
    .add_head(google_charts_loader())
    .add_body(Div(H1("Hello, world!"), Img(src="hero.png", style=inline_style(("border_radius", "8px")))))
)

print(doc.render())

chart_loader = google_charts_package_loader(["corechart", "table"], callback="drawChart")
writer = MarkupWriter()
writer.write_html("dist/index.html", doc)
writer.write_css("dist/site.css", styles)
writer.write_html("dist/charts.html", HtmlDocument(title="Charts").add_head(chart_loader))
```

## JavaScript Helpers

Use `javascript_link()` and `javascript_script()` for arbitrary script tags and inline code. The library also exposes `bootstrap5_bundle_script()` and Google Charts helpers so you can wire up common browser libraries without hand-building script tags.

## Asset Helpers

Tailwind is injected with the official Play CDN script because that is the fastest supported browser-side setup for this library. Bootstrap 5 is injected as a CSS stylesheet from jsDelivr. Google Fonts are emitted as a preconnect pair plus a CSS2 stylesheet link so browsers can establish connections early and only download the fonts you ask for.

Common Tailwind class families that pair well with the helpers:

- Layout: `container`, `mx-auto`, `flex`, `grid`, `gap-*`, `items-center`, `justify-between`
- Spacing: `p-*`, `px-*`, `py-*`, `m-*`, `space-x-*`, `space-y-*`
- Typography: `text-*`, `font-*`, `leading-*`, `tracking-*`
- Surface: `bg-*`, `text-*`, `border-*`, `rounded-*`, `shadow-*`
- Responsive prefixes: `sm:`, `md:`, `lg:`, `xl:`, `2xl:`

Common Bootstrap 5 class families that pair well with the helpers:

- Layout and grid: `container`, `container-fluid`, `row`, `col`, `g-*`, `row-cols-*`
- Spacing and display: `m-*`, `p-*`, `d-flex`, `d-grid`, `gap-*`, `justify-content-*`, `align-items-*`
- Typography: `lead`, `fw-bold`, `fst-italic`, `text-muted`, `text-center`, `text-nowrap`
- Components: `btn`, `btn-primary`, `card`, `badge`, `alert`, `navbar`, `modal`
- Responsive prefixes: `sm`, `md`, `lg`, `xl`, `xxl`

Google Fonts examples:

- `google_fonts_assets("Inter")`
- `google_fonts_assets("Inter", "Open Sans")`
- `google_fonts_assets("Roboto", weights=(400, 700), text="Hello world")`

## Layout

- `src/html5/document.py` contains the HTML5 document and element primitives.
- `src/html5/elements.py` contains generated classes for standard HTML5 tags.
- `src/html5/css.py` contains CSS node classes for comments, declarations, rules, at-rules, keyframes, inline styles, and `<style>` generation.
- `src/html5/js.py` contains JavaScript helpers for inline scripts, external scripts, Bootstrap 5, and Google Charts.
- `src/html5/writer.py` contains a disk writer for rendered HTML and CSS outputs.
- `src/html5/version.py` stores the semantic version string used by packaging.

## Versioning

This project uses semantic versioning. The current package version is `0.2.0`, and the release history is documented in [CHANGELOG.md](CHANGELOG.md).
