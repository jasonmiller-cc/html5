# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-09-06

- Renamed PyPI distribution from `html5` (taken) to `html5cc`. Import name is unchanged: `import html5`.

## [0.3.0] - 2026-09-05

- Fixed `style_tag()` isinstance check order to prevent double-wrapping of `CSSStyleElement`.
- `JSScript` now raises `ValueError` when both `src` and `code` are set simultaneously.
- Removed redundant `JSLink` class; `javascript_link()` now returns `JSScript` directly.
- Fixed `MarkupWriter` path guard to reject `"."` (root directory) and `..`-based escapes.
- Added `BOOTSTRAP5_CSS_URL` to `css.__all__`.
- Fixed `pyproject.toml` `Homepage` URL (was placeholder `example.com`); added Documentation, Source, and Changelog URLs.
- Added CI workflow (`ci.yml`) running pytest across Python 3.10, 3.11, and 3.12.
- Added publish workflow (`publish.yml`) for GitHub Packages on version tags.
- Expanded test coverage: `CSSAtRule`, `CSSSupportsRule`, `CSSLayerRule`, `CSSMediaRule`, `CSSKeyframe`, `style_tag` double-wrap guard, `JSScript` validation, `MarkupWriter` path traversal, `google_fonts_url(text=…)`, `HtmlDocument(lang=…)`.
- Added Installation documentation page with pip, requirements.txt, uv, and Poetry examples.

## [0.2.0] - 2026-09-05

- Added CDN helpers for Bootstrap 5 and Tailwind CSS.
- Added optimized Google Fonts asset generation.
- Added a disk writer utility for HTML and CSS outputs.
- Added semantic version metadata and pytest coverage configuration.

## [0.1.0] - 2026-09-04

- Initial HTML5 and CSS3 markup helpers.
