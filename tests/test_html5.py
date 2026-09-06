from __future__ import annotations

from pathlib import Path

import pytest

from html5 import (
    CSSDeclaration,
    CSSKeyframe,
    CSSStyleSheet,
    Div,
    H1,
    HtmlDocument,
    Img,
    MarkupWriter,
    __version__,
    bootstrap5_stylesheet,
    bootstrap5_bundle_script,
    google_fonts_assets,
    google_fonts_url,
    google_charts_loader,
    google_charts_package_loader,
    javascript_link,
    javascript_script,
    inline_style,
    style_tag,
    tailwind_script,
)


def test_version_uses_semver() -> None:
    assert __version__ == "0.2.0"
    assert __version__.count(".") == 2


def test_html_document_renders_with_css_assets() -> None:
    stylesheet = (
        CSSStyleSheet()
        .add_comment("base styles")
        .add_import("reset.css")
        .add_rule("body", ("margin", 0), ("font_family", "system-ui"))
        .add_media("screen and (min-width: 40rem)", CSSDeclaration("color", "black"))
        .add_keyframes("fade", CSSKeyframe("from", ("opacity", 0)), CSSKeyframe("to", ("opacity", 1)))
    )

    doc = (
        HtmlDocument(title="Hello HTML5")
        .add_head(style_tag(stylesheet))
        .add_head(*google_fonts_assets("Inter"))
        .add_head(bootstrap5_stylesheet())
        .add_head(tailwind_script())
        .add_body(
            Div(
                H1("Hello, world!"),
                Img(src="hero.png", style=inline_style(("border_radius", "8px"))),
            )
        )
    )

    rendered = doc.render()
    assert rendered.startswith("<!doctype html>")
    assert "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" in rendered
    assert "https://cdn.tailwindcss.com" in rendered
    assert "https://fonts.googleapis.com/css2?" in rendered
    assert "Inter:wght@400;500;700" in rendered
    assert "/* base styles */" in rendered
    assert "@import url(\"reset.css\");" in rendered
    assert "@keyframes fade" in rendered
    assert "border-radius: 8px;" in rendered


def test_google_fonts_url_supports_multiple_families() -> None:
    url = google_fonts_url("Inter", "Open Sans", weights=(300, 400), display="swap")

    assert url.startswith("https://fonts.googleapis.com/css2?")
    assert "family=Inter:wght@300;400" in url
    assert "family=Open+Sans:wght@300;400" in url
    assert "display=swap" in url


def test_bootstrap_and_tailwind_helpers_return_expected_tags() -> None:
    assert bootstrap5_stylesheet().render() == (
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">'
    )
    assert bootstrap5_bundle_script().render() == (
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'
    )
    assert tailwind_script().render() == '<script src="https://cdn.tailwindcss.com"></script>'


def test_javascript_helpers_return_expected_tags() -> None:
    assert javascript_link("https://example.com/app.js").render() == (
        '<script src="https://example.com/app.js"></script>'
    )
    assert javascript_script("console.log('hi')").render() == (
        "<script>console.log('hi')</script>"
    )
    assert google_charts_loader().render() == (
        '<script src="https://www.gstatic.com/charts/loader.js?ver=51"></script>'
    )
    assert "google.charts.load('current'" in google_charts_package_loader(["corechart"]).render()


def test_markup_writer_writes_html_and_css(tmp_path: Path) -> None:
    writer = MarkupWriter(root=tmp_path)
    document = HtmlDocument(title="Disk Test").add_body(Div(H1("Saved")))
    stylesheet = CSSStyleSheet().add_rule("body", margin="0")

    html_path = writer.write_html("site/index.html", document)
    css_path = writer.write_css("site/site.css", stylesheet)

    assert html_path == tmp_path / "site" / "index.html"
    assert css_path == tmp_path / "site" / "site.css"
    assert html_path.read_text(encoding="utf-8").startswith("<!doctype html>")
    assert "body { margin: 0; }" in css_path.read_text(encoding="utf-8")


def test_markup_writer_rejects_absolute_paths(tmp_path: Path) -> None:
    writer = MarkupWriter(root=tmp_path)

    with pytest.raises(ValueError):
        writer.write_html("/tmp/escape.html", HtmlDocument(title="bad"))


def test_void_html_elements_reject_children() -> None:
    with pytest.raises(ValueError):
        Img("unexpected child", src="hero.png")
