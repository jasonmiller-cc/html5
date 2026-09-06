"""HTML5 document and CSS3 helpers."""

from .css import (
    CSSAtRule,
    CSSComment,
    CSSCustomProperties,
    CSSDeclaration,
    CSSLink,
    CSSImportRule,
    CSSInlineStyle,
    CSSKeyframe,
    CSSKeyframesRule,
    CSSLayerRule,
    CSSMediaRule,
    CSSNode,
    CSSRule,
    CSSStyleElement,
    CSSStyleSheet,
    CSSSupportsRule,
    BOOTSTRAP5_CSS_URL,
    GOOGLE_FONTS_PRECONNECT_URL,
    GOOGLE_FONTS_STATIC_URL,
    TAILWIND_PLAY_CDN_URL,
    bootstrap5_stylesheet,
    css_var,
    google_fonts_assets,
    google_fonts_url,
    inline_style,
    tailwind_script,
    style_tag,
)
from .loader import css_loader, html_loader
from .document import Comment, Doctype, Element, HtmlDocument, Node, Raw, Text, comment, doctype, doctype_node, element, raw, text
from .elements import *
from .version import __version__
from .writer import MarkupWriter
from .js import (
    JSNode,
    JSScript,
    bootstrap5_bundle_script,
    google_charts_loader,
    google_charts_package_loader,
    javascript_link,
    javascript_script,
)