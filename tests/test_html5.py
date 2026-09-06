from __future__ import annotations

from pathlib import Path

import pytest

from html5 import (
    CSSAtRule,
    CSSDeclaration,
    CSSKeyframe,
    CSSLayerRule,
    CSSMediaRule,
    CSSStyleElement,
    CSSStyleSheet,
    CSSSupportsRule,
    Div,
    H1,
    HtmlDocument,
    Img,
    JSScript,
    MarkupWriter,
    __version__,
    bootstrap5_bundle_script,
    bootstrap5_stylesheet,
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
    assert __version__ == "0.3.0"
    assert __version__.count(".") == 2


# ---------------------------------------------------------------------------
# HtmlDocument
# ---------------------------------------------------------------------------

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
        .add_body(Div(H1("Hello, world!"), Img(src="hero.png", style=inline_style(("border_radius", "8px")))))
    )
    rendered = doc.render()
    assert rendered.startswith("<!doctype html>")
    assert "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" in rendered
    assert "https://cdn.tailwindcss.com" in rendered
    assert "https://fonts.googleapis.com/css2?" in rendered
    assert "Inter:wght@400;500;700" in rendered
    assert "/* base styles */" in rendered
    assert '@import url("reset.css");' in rendered
    assert "@keyframes fade" in rendered
    assert "border-radius: 8px;" in rendered


def test_html_document_non_default_lang() -> None:
    doc = HtmlDocument(title="French page", lang="fr")
    assert 'lang="fr"' in doc.render()


def test_html_document_default_lang_is_en() -> None:
    assert 'lang="en"' in HtmlDocument(title="Default").render()


# ---------------------------------------------------------------------------
# CSS helpers
# ---------------------------------------------------------------------------

def test_google_fonts_url_supports_multiple_families() -> None:
    url = google_fonts_url("Inter", "Open Sans", weights=(300, 400), display="swap")
    assert url.startswith("https://fonts.googleapis.com/css2?")
    assert "family=Inter:wght@300;400" in url
    assert "family=Open+Sans:wght@300;400" in url
    assert "display=swap" in url


def test_google_fonts_url_text_parameter() -> None:
    url = google_fonts_url("Roboto", text="Hello")
    assert "text=Hello" in url


def test_bootstrap_and_tailwind_helpers_return_expected_tags() -> None:
    assert bootstrap5_stylesheet().render() == (
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">'
    )
    assert bootstrap5_bundle_script().render() == (
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'
    )
    assert tailwind_script().render() == '<script src="https://cdn.tailwindcss.com"></script>'


def test_css_at_rule_with_block() -> None:
    rule = CSSAtRule(name="charset", prelude='"UTF-8"', block=False)
    assert rule.render() == '@charset "UTF-8";'


def test_css_at_rule_without_prelude() -> None:
    rule = CSSAtRule(name="layer", body=(CSSAtRule(name="base", prelude="", body=(), block=True),))
    rendered = rule.render()
    assert rendered.startswith("@layer {")


def test_css_supports_rule() -> None:
    from html5 import CSSRule
    rule = CSSSupportsRule("(display: grid)", CSSRule("div", ("display", "grid")))
    rendered = rule.render()
    assert "@supports (display: grid)" in rendered
    assert "div { display: grid; }" in rendered


def test_css_layer_rule() -> None:
    from html5 import CSSRule
    rule = CSSLayerRule("utilities", CSSRule(".hidden", ("display", "none")))
    rendered = rule.render()
    assert "@layer utilities {" in rendered
    assert ".hidden { display: none; }" in rendered


def test_css_media_rule() -> None:
    from html5 import CSSRule
    rule = CSSMediaRule("(prefers-color-scheme: dark)", CSSRule("body", ("background", "#000")))
    rendered = rule.render()
    assert "@media (prefers-color-scheme: dark)" in rendered
    assert "body { background: #000; }" in rendered


def test_css_keyframe_render() -> None:
    frame = CSSKeyframe("50%", ("opacity", "0.5"), ("transform", "scale(1.1)"))
    rendered = frame.render()
    assert "50% {" in rendered
    assert "opacity: 0.5;" in rendered
    assert "transform: scale(1.1);" in rendered


def test_style_tag_with_css_style_element_no_double_wrap() -> None:
    inner = CSSStyleSheet().add_rule("p", ("color", "red"))
    element = CSSStyleElement(stylesheet=inner)
    rendered = style_tag(element).render()
    assert rendered.count("<style>") == 1
    assert rendered.count("</style>") == 1
    assert "color: red;" in rendered


def test_style_tag_with_stylesheet() -> None:
    sheet = CSSStyleSheet().add_rule("h1", ("font_size", "2rem"))
    rendered = style_tag(sheet).render()
    assert rendered.startswith("<style>")
    assert "font-size: 2rem;" in rendered


# ---------------------------------------------------------------------------
# JavaScript helpers
# ---------------------------------------------------------------------------

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


def test_javascript_link_returns_jsscript() -> None:
    result = javascript_link("https://example.com/app.js")
    assert isinstance(result, JSScript)


def test_jsscript_rejects_both_src_and_code() -> None:
    with pytest.raises(ValueError, match="cannot set both"):
        JSScript(src="https://example.com/app.js", code="console.log(1)")


def test_jsscript_src_only() -> None:
    s = JSScript(src="https://example.com/app.js")
    assert 'src="https://example.com/app.js"' in s.render()


def test_jsscript_code_only() -> None:
    s = JSScript(code="alert(1)")
    assert "alert(1)" in s.render()
    assert "src" not in s.render()


# ---------------------------------------------------------------------------
# MarkupWriter
# ---------------------------------------------------------------------------

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


def test_markup_writer_rejects_root_as_path(tmp_path: Path) -> None:
    writer = MarkupWriter(root=tmp_path)
    with pytest.raises(ValueError):
        writer.write_text(".", "content")


def test_markup_writer_rejects_dotdot_traversal(tmp_path: Path) -> None:
    writer = MarkupWriter(root=tmp_path)
    with pytest.raises(ValueError):
        writer.write_html("../escape.html", HtmlDocument(title="bad"))


# ---------------------------------------------------------------------------
# Element helpers
# ---------------------------------------------------------------------------

def test_void_html_elements_reject_children() -> None:
    with pytest.raises(ValueError):
        Img("unexpected child", src="hero.png")
