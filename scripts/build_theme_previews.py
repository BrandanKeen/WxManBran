#!/usr/bin/env python3
"""Generate static light and dark mode preview pages for the WxManBran site."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
import textwrap
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
PREVIEW_DIR = ROOT / "ui" / "previews"

NAV_ITEMS = [
    {"title": "Home", "url": "/", "icon": "home"},
    {"title": "Tropical Updates", "url": "/tropical-updates/", "icon": "updates"},
    {"title": "Previous Storms", "url": "/previous-storms/", "icon": "storm"},
    {"title": "About", "url": "/about/", "icon": "about"},
]


def _load_page_content() -> str:
    index_path = ROOT / "index.html"
    raw = index_path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise RuntimeError("index.html is missing front matter; cannot locate content block")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise RuntimeError("Unexpected front matter structure in index.html")
    content = parts[2]
    # Drop a single leading newline for cleaner indentation.
    if content.startswith("\n"):
        content = content[1:]
    return content.rstrip() + "\n"


def _load_icons() -> Dict[str, str]:
    icon_dir = ROOT / "_includes" / "icons"
    icons: Dict[str, str] = {}
    for item in NAV_ITEMS:
        name = item.get("icon")
        if not name:
            continue
        icon_path = icon_dir / f"{name}.svg"
        svg = icon_path.read_text(encoding="utf-8").strip()
        icons[name] = svg
    return icons


def _build_nav(theme: str, icons: Dict[str, str]) -> str:
    parts: List[str] = ["<nav class=\"site-nav\">", "  <ul class=\"site-nav__links\">"]
    current_url = "/"
    for item in NAV_ITEMS:
        url = item["url"]
        title = item["title"]
        icon_name = item.get("icon")
        icon_svg = icons.get(icon_name, "")
        is_current = url == current_url
        aria_current = " aria-current=\"page\"" if is_current else ""
        active_class = " is-active" if is_current else ""
        parts.append(
            "    <li>\n"
            f"      <a href=\"{url}\" class=\"nav-link{active_class}\"{aria_current}>\n"
            f"        <span class=\"nav-icon\" aria-hidden=\"true\">{icon_svg}</span>\n"
            f"        <span class=\"nav-label\">{title}</span>\n"
            "      </a>\n"
            "    </li>"
        )

    pressed = "true" if theme == "dark" else "false"
    toggle_label = "Switch to light mode" if theme == "dark" else "Switch to dark mode"
    parts.append(
        "    <li class=\"site-nav__theme\">\n"
        "      <details class=\"nav-gear\" data-theme-gear>\n"
        "        <summary class=\"nav-gear__button\" aria-label=\"Theme settings\">\n"
        "          <span class=\"nav-gear__icon\" aria-hidden=\"true\">\n"
        "            <svg viewBox=\"0 0 24 24\" role=\"presentation\" focusable=\"false\">\n"
        "              <path d=\"M12 15.25a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n"
        "              <path d=\"M20.5 13.46V10.6l-2.13-.53a6.35 6.35 0 0 0-.62-1.5l1.17-1.87-2.02-2.02-1.87 1.17c-.5-.24-1.03-.44-1.58-.58L12.4 3.5h-2.86l-.55 2.27c-.55.14-1.08.34-1.58.58L5.54 5.18 3.52 7.2l1.17 1.87c-.28.48-.5.98-.65 1.51l-2.04.5v2.86l2.13.53c.14.55.35 1.09.62 1.59l-1.17 1.87 2.02 2.02 1.87-1.17c.48.23.99.42 1.52.56l.55 2.24h2.86l.55-2.24c.52-.14 1.03-.33 1.52-.56l1.87 1.17 2.02-2.02-1.17-1.87c.27-.5.48-1.03.62-1.58l2.04-.5Z\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n"
        "            </svg>\n"
        "          </span>\n"
        "          <span class=\"visually-hidden\">Open theme settings</span>\n"
        "        </summary>\n"
        "        <div class=\"nav-gear__panel\">\n"
        "          <button type=\"button\"\n"
        "                  class=\"theme-toggle__button\"\n"
        "                  data-theme-toggle\n"
        f"                  aria-pressed=\"{pressed}\"\n"
        f"                  aria-label=\"{toggle_label}\"\n"
        f"                  title=\"{toggle_label}\">\n"
        "            <span class=\"theme-toggle__track\" aria-hidden=\"true\">\n"
        "              <span class=\"theme-toggle__label theme-toggle__label--day\">Light</span>\n"
        "              <span class=\"theme-toggle__thumb\">\n"
        "                <span class=\"theme-toggle__icon theme-toggle__icon--sun\" aria-hidden=\"true\">\n"
        "                  <svg viewBox=\"0 0 24 24\" role=\"presentation\" focusable=\"false\">\n"
        "                    <circle cx=\"12\" cy=\"12\" r=\"4.25\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n"
        "                    <path d=\"M12 2.5v3.2M12 18.3v3.2M4.54 4.54l2.26 2.26M17.2 17.2l2.26 2.26M2.5 12h3.2M18.3 12h3.2M4.54 19.46l2.26-2.26M17.2 6.8l2.26-2.26\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n"
        "                  </svg>\n"
        "                </span>\n"
        "                <span class=\"theme-toggle__icon theme-toggle__icon--moon\" aria-hidden=\"true\">\n"
        "                  <svg viewBox=\"0 0 24 24\" role=\"presentation\" focusable=\"false\">\n"
        "                    <path d=\"M21 14.25a8.26 8.26 0 0 1-10.78-10.5 8.27 8.27 0 1 0 10.78 10.5Z\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n"
        "                  </svg>\n"
        "                </span>\n"
        "              </span>\n"
        "              <span class=\"theme-toggle__label theme-toggle__label--night\">Dark</span>\n"
        "            </span>\n"
        f"            <span class=\"visually-hidden\" data-theme-toggle-text>{toggle_label}</span>\n"
        "          </button>\n"
        "        </div>\n"
        "      </details>\n"
        "    </li>"
    )
    parts.append("  </ul>")
    parts.append("</nav>")
    return "\n".join(parts)


def _build_page(theme: str, page_content: str, icons: Dict[str, str]) -> str:
    nav_html = _build_nav(theme, icons)
    mode_title = "Light" if theme == "light" else "Dark"
    year = _dt.datetime.now().year
    indented_content = textwrap.indent(page_content.rstrip(), "      ")
    return (
        "<!doctype html>\n"
        f"<html lang=\"en\" data-theme=\"{theme}\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\">\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "    <base href=\"/\">\n"
        f"    <title>{mode_title} Mode Preview | WxManBran</title>\n"
        "    <link rel=\"stylesheet\" href=\"/assets/css/brand-colors.css\">\n"
        "    <link rel=\"stylesheet\" href=\"/assets/css/site.css\">\n"
        "  </head>\n"
        "  <body class=\"site\">\n"
        "    <a class=\"skip-link\" href=\"#content\">Skip to content</a>\n"
        "    <header class=\"site-header\">\n"
        f"      {nav_html}\n"
        "    </header>\n"
        "    <main id=\"content\" class=\"site-content\">\n"
        f"{indented_content}\n"
        "    </main>\n"
        "    <footer class=\"site-footer\">\n"
        "      <div class=\"site-footer__inner\">\n"
        f"        <p>&copy; {year} WxManBran. Forecasts with heart from Weather Man Bran.</p>\n"
        "        <p><a href=\"mailto:hello@wxmanbran.com\">Contact</a></p>\n"
        "      </div>\n"
        "    </footer>\n"
        "  </body>\n"
        "</html>\n"
    )


def _build_gallery() -> str:
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\">\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "    <title>Theme Preview Gallery | WxManBran</title>\n"
        "    <style>\n"
        "      body {\n"
        "        margin: 0;\n"
        "        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n"
        "        background: #0f111a;\n"
        "        color: #f8fafc;\n"
        "      }\n"
        "      main {\n"
        "        min-height: 100vh;\n"
        "        padding: clamp(1rem, 5vw, 3rem);\n"
        "        display: grid;\n"
        "        gap: clamp(1.5rem, 4vw, 3rem);\n"
        "        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));\n"
        "        box-sizing: border-box;\n"
        "      }\n"
        "      figure {\n"
        "        margin: 0;\n"
        "        display: flex;\n"
        "        flex-direction: column;\n"
        "        gap: 0.75rem;\n"
        "      }\n"
        "      figcaption {\n"
        "        font-weight: 600;\n"
        "        letter-spacing: 0.03em;\n"
        "        text-transform: uppercase;\n"
        "        font-size: 0.85rem;\n"
        "      }\n"
        "      iframe {\n"
        "        width: 100%;\n"
        "        aspect-ratio: 3 / 4;\n"
        "        border: 0;\n"
        "        border-radius: 18px;\n"
        "        box-shadow: 0 20px 45px rgba(15, 17, 26, 0.55);\n"
        "        background: #fff;\n"
        "      }\n"
        "      iframe.dark-preview {\n"
        "        background: #0f1431;\n"
        "      }\n"
        "    </style>\n"
        "  </head>\n"
        "  <body>\n"
        "    <main>\n"
        "      <figure>\n"
        "        <figcaption>Light mode</figcaption>\n"
        "        <iframe src=\"theme-preview-light.html\" title=\"Light mode preview\" loading=\"lazy\"></iframe>\n"
        "      </figure>\n"
        "      <figure>\n"
        "        <figcaption>Dark mode</figcaption>\n"
        "        <iframe class=\"dark-preview\" src=\"theme-preview-dark.html\" title=\"Dark mode preview\" loading=\"lazy\"></iframe>\n"
        "      </figure>\n"
        "    </main>\n"
        "  </body>\n"
        "</html>\n"
    )


def main() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    page_content = _load_page_content()
    icons = _load_icons()

    for theme in ("light", "dark"):
        html = _build_page(theme, page_content, icons)
        (PREVIEW_DIR / f"theme-preview-{theme}.html").write_text(html, encoding="utf-8")

    (PREVIEW_DIR / "index.html").write_text(_build_gallery(), encoding="utf-8")


if __name__ == "__main__":
    main()
