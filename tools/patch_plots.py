#!/usr/bin/env python3
import os, re, pathlib, shutil, glob

SRC_ROOT = "assets/plots"
BACKUP_DIR = "backup_plots_before_patch"

MOBILE_CSS = """<style>/* WMB touch-action helper */\nhtml, body { overscroll-behavior: contain; }\n.js-plotly-plot, .plot-container, .svg-container { touch-action: none; }\n</style>"""

def patch_html(html: str) -> str:
    # 0) Add mobile CSS helper once
    if "</head>" in html and "WMB touch-action helper" not in html:
        html = html.replace("</head>", MOBILE_CSS + "</head>")

    # 1) Remove explicit hovermode argument in Plotly.Fx.hover to avoid subplot routing conflicts
    html = re.sub(
        r"Plotly\.Fx\.hover\(\s*gd\s*,\s*uniquePoints\s*,\s*\{[^}]*\}\s*\)",
        "Plotly.Fx.hover(gd, uniquePoints)",
        html
    )

    # 2) Get the main inline JS after <div id="chart">
    start_div = html.find('<div id="chart"')
    if start_div == -1:
        return html
    s = html.find("<script", start_div)
    if s == -1:
        return html
    s = html.find(">", s) + 1
    e = html.find("</script>", s)
    if e == -1:
        return html

    js = html[s:e]
    changed = False

    # 3) Throttle hover updates via requestAnimationFrame and route all synthetic hover through it
    if "function scheduleHover" not in js and "applyHoverForTime" in js and "moveScrub" in js:
        js = js.replace(
            "const moveScrub = (touch) => {",
            "let rafPending = false;\n"
            "let rafTargetTime = null;\n"
            "function scheduleHover(targetTime) {\n"
            "  rafTargetTime = targetTime;\n"
            "  if (rafPending) return;\n"
            "  rafPending = true;\n"
            "  requestAnimationFrame(() => {\n"
            "    rafPending = false;\n"
            "    const t = rafTargetTime; rafTargetTime = null;\n"
            "    if (Number.isFinite(t)) { applyHoverForTime(t); }\n"
            "  });\n"
            "}\n"
            "const moveScrub = (touch) => {"
        )
        js = js.replace("applyHoverForTime(targetTime);", "scheduleHover(targetTime);")
        js = js.replace("applyHoverForTime(state.targetTime);", "scheduleHover(state.targetTime);")
        changed = True

    # 4) De-duplicate expensive restyles inside applyHoverForTime
    #    This prevents layout thrash while scrubbing quickly
    if "const lastHighlight = new Map()" not in js and "applyHoverForTime" in js:
        js = js.replace(
            "function applyHoverForTime(targetTime) {",
            "const lastHighlight = new Map();\nfunction applyHoverForTime(targetTime) {"
        )
        js = js.replace(
            "Plotly.restyle(gd, { x: [[match.x]], y: [[match.y]], visible: true }, highlightIdx);",
            "const prev = lastHighlight.get(highlightIdx);\n"
            "          if (!prev || prev.x != match.x || prev.y != match.y || prev.visible !== true) {\n"
            "            Plotly.restyle(gd, { x: [[match.x]], y: [[match.y]], visible: true }, highlightIdx);\n"
            "            lastHighlight.set(highlightIdx, {x: match.x, y: match.y, visible: true});\n"
            "          }"
        )
        js = js.replace(
            "Plotly.restyle(gd, { visible: false }, highlightIdx);",
            "const prev2 = lastHighlight.get(highlightIdx);\n"
            "            if (!prev2 || prev2.visible !== false) {\n"
            "              Plotly.restyle(gd, { visible: false }, highlightIdx);\n"
            "              lastHighlight.set(highlightIdx, {x: null, y: null, visible: false});\n"
            "            }"
        )
        changed = True

    # 5) Edge padding to reduce OS gesture conflicts at left and right edges
    if "computeTargetTime" in js and "edgePad" not in js:
        js = js.replace(
            "const clamped = Math.min(Math.max(clientX, rect.left), rect.right);",
            "const edgePad = 4; const clamped = Math.min(Math.max(clientX, rect.left + edgePad), rect.right - edgePad);"
        )
        changed = True

    # 6) Keep hover active near edges without changing visuals
    if "const figure" in js and "\"layout\"" in js and "\"hoverdistance\"" not in js:
        js = re.sub(
            r"(const\s+figure\s*=\s*\{[^;]*\"layout\"\s*:\s*\{)",
            r'\1"hoverdistance": -1, "spikedistance": -1, ',
            js, count=1
        )
        changed = True

    # 7) Robust touch gating so setupTouchHover runs on real touch devices
    #    This ensures the scrubbing handler initializes on iOS and Android so values appear in tooltips while sliding
    if "setupTouchHover()" in js:
        js = re.sub(
            r"if\s*\(\s*isCoarsePointerDevice\(\)\s*\)\s*\{\s*setupTouchHover\(\);\s*\}",
            "const HAS_TOUCH = ((\'ontouchstart\' in window) || (navigator.maxTouchPoints > 0) || (window.matchMedia && window.matchMedia('(pointer: coarse)').matches));\n"
            "if (HAS_TOUCH) { setupTouchHover(); }",
            js
        )
        changed = True

    # 8) Guard against accidental hiding of the hoverlayer so values are visible
    #    Remove any inline CSS that would hide Plotly's hoverlayer
    if ".hoverlayer{display:none" in html.replace(" ", ""):
        html = re.sub(r"\.hoverlayer\s*\{\s*display\s*:\s*none\s*;?\s*\}", "", html)
        changed = True

    if changed:
        html = html[:s] + js + html[e:]
    return html

def main():
    # 1) Backup originals
    for path in glob.glob(os.path.join(SRC_ROOT, "**/*.html"), recursive=True):
        rel = os.path.relpath(path, SRC_ROOT)
        backup_path = os.path.join(BACKUP_DIR, rel)
        pathlib.Path(os.path.dirname(backup_path)).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(backup_path):
            shutil.copy2(path, backup_path)

    # 2) Patch in place
    for path in glob.glob(os.path.join(SRC_ROOT, "**/*.html"), recursive=True):
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        new = patch_html(txt)
        if new != txt:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)

if __name__ == "__main__":
    main()
