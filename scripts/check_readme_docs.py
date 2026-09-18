#!/usr/bin/env python3
# Generate and verify SWIR Progress SVG PRO documentation assets.
from __future__ import annotations
import argparse
import html
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "progress.json"
CARD = ROOT / "assets" / "readme" / "progress-card.svg"
MINI = ROOT / "assets" / "readme" / "progress-mini.svg"
README = ROOT / "README.md"
STATUS = ROOT / "docs" / "STATUS.md"
TRACK_WIDTH = 1100.0
LEGACY_PATTERNS = (re.compile(r"[█▓▒░■□▪▫]{5,}"), re.compile(r"\[[#=\-]{8,}\]"),)

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)

def load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    pct = data.get("percentage")
    if pct is not None:
        pct = float(pct)
        if not math.isfinite(pct) or not 0 <= pct <= 100:
            raise ValueError("percentage must be finite and between 0 and 100")
    return data

def card_svg(data: dict) -> str:
    project, scope, pct = esc(data["project"]), esc(data["scope"]), data.get("percentage")
    label = "N/A" if pct is None else f"{pct:.1f}%"
    fill = "" if pct is None or pct <= 0 else f'<rect x="50" y="124" width="{TRACK_WIDTH * pct / 100:.3f}" height="14" rx="7" fill="url(#accent)"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-labelledby="title desc">
<title id="title">{project} product progress: {label}</title>
<desc id="desc">{scope}. {esc(data["reason"])}</desc>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient><linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient><pattern id="grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0V34" fill="none" stroke="#62E5FF" stroke-opacity=".045"/></pattern></defs>
<rect x="1" y="1" width="1198" height="178" rx="22" fill="url(#bg)" stroke="#62E5FF" stroke-opacity=".25"/><rect x="1" y="1" width="1198" height="178" rx="22" fill="url(#grid)"/>
<text x="50" y="38" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="3">SWIR PROGRESS</text>
<text x="50" y="76" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="27" font-weight="800">{project}</text>
<text x="50" y="103" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="14">{scope}</text>
<text x="1150" y="75" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="31" font-weight="800">{label}</text>
<text x="1150" y="101" text-anchor="end" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="700">PRODUCT PROGRESS</text>
<rect x="50" y="124" width="1100" height="14" rx="7" fill="#0B1928" stroke="#62E5FF" stroke-opacity=".16"/>{fill}
<text x="50" y="158" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">No authoritative roadmap percentage is available; release state is reported separately.</text>
</svg>'''

def mini_svg(data: dict) -> str:
    project, scope, pct = esc(data["project"]), esc(data["scope"]), data.get("percentage")
    label = "N/A" if pct is None else f"{pct:.1f}%"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-labelledby="title desc">
<title id="title">{project} product progress: {label}</title>
<desc id="desc">{scope}. {esc(data["reason"])}</desc>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient></defs>
<rect x="1" y="1" width="898" height="70" rx="16" fill="url(#bg)" stroke="#62E5FF" stroke-opacity=".25"/>
<text x="24" y="29" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="17" font-weight="700">{project}</text>
<text x="24" y="51" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">{scope}</text>
<text x="876" y="31" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="22" font-weight="800">{label}</text>
<text x="876" y="51" text-anchor="end" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="11" font-weight="700">PRODUCT PROGRESS</text>
</svg>'''

def validate_xml(text: str) -> None:
    root = ET.fromstring(text)
    if root.tag.split("}")[-1] != "svg": raise ValueError("not an SVG root")
    for elem in root.iter():
        for key in ("x", "y", "width", "height", "rx", "ry"):
            if key in elem.attrib:
                value = elem.attrib[key]
                if value.endswith("%"): continue
                try: num = float(value)
                except ValueError: continue
                if not math.isfinite(num) or num < 0: raise ValueError(f"invalid geometry: {key}={value}")

def legacy_meter(text: str) -> bool:
    return any(p.search(text) for p in LEGACY_PATTERNS)

def verify_docs(card: str, mini: str) -> None:
    readme, status = README.read_text(encoding="utf-8"), STATUS.read_text(encoding="utf-8")
    required = ("<!-- SWIR-README-STANDARD:v2 -->", "assets/readme/hero.svg", "assets/readme/progress-card.svg", "## 🔎 Search Keywords")
    missing = [item for item in required if item not in readme]
    if missing: raise ValueError("README missing: " + ", ".join(missing))
    if "../assets/readme/progress-mini.svg" not in status: raise ValueError("STATUS.md does not embed progress-mini.svg")
    for name, text in (("README.md", readme), ("docs/STATUS.md", status)):
        if legacy_meter(text): raise ValueError(f"legacy progress meter found in {name}")
    validate_xml(card); validate_xml(mini)

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); args = ap.parse_args()
    data = load(); card = card_svg(data); mini = mini_svg(data); verify_docs(card, mini)
    if args.check:
        if CARD.read_text(encoding="utf-8") != card: raise SystemExit("progress-card.svg is stale")
        if MINI.read_text(encoding="utf-8") != mini: raise SystemExit("progress-mini.svg is stale")
        ET.parse(ROOT / "assets" / "readme" / "progress-template.svg")
        print("README/SVG documentation check: PASS"); return 0
    CARD.parent.mkdir(parents=True, exist_ok=True); CARD.write_text(card, encoding="utf-8"); MINI.write_text(mini, encoding="utf-8")
    print("Generated progress-card.svg and progress-mini.svg"); return 0

if __name__ == "__main__": sys.exit(main())
