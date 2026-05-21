"""Design tokens & matplotlib setup untuk poster Tubes 1 Fase 2.

Single source of truth untuk warna, tipografi, dan rcParams.
Selaras dengan docs-system-development/spec_desain.md.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# Color tokens
# ─────────────────────────────────────────────────────────────

# Palette revisi (feedback bu Desi + tim):
# - Parity (5) ganti ke HIJAU-TEAL: metafora "aman/baik" yang jelas berbeda
#   dari spektrum merah. Bukan lagi "merah pucat = agak buruk" trap.
# - Worst (1) tetap dark red saturated.
# - Unknown (9) dipisah dari spektrum merah: KUNING gold dengan dot pattern
#   subtle = "buruk tapi ambigu", warning warna universal.
# - No-data dipindah ke hatched line (sebelumnya tekstur Unknown).
LOOP_SUMM_COLORS = {
    1.0: "#A50F15",   # worst: gender inequality + girls <=13
    2.0: "#DE2D26",   # inequality AND girls 14-17
    3.0: "#FCAE91",   # inequality OR girls 14-17 (salmon)
    5.0: "#76B900",   # parity + min 18+ — NVIDIA green (revisi tim)
    9.0: "#FFD60A",   # unknown — bright yellow (revisi tim)
}
PARITY_ALPHA = 0.80        # opacity hijau parity (revisi tim, bukan 100%)
UNKNOWN_HATCH = "..."      # dot pattern padat/crowded (revisi tim)
NO_DATA_COLOR = "#D9D9D9"  # light grey
NO_DATA_HATCH = "///"      # hatched line untuk no-data

COLOR_FEMALE = "#C71E3A"
COLOR_MALE = "#1F4E79"

COLOR_HEADLINE = "#0F4C5C"
COLOR_BODY = "#2D3142"
COLOR_MUTED = "#8A8F9A"
COLOR_ACCENT = "#E07A5F"
COLOR_BG = "#F8F9FA"      # Cool off-white (revisi tim, sebelumnya warm beige)
COLOR_GRIDLINE = "#DDE0E3"  # Cool grey gridline selaras background

COLOR_DANGER = "#C71E3A"
COLOR_SAFE = "#2A9D8F"


# ─────────────────────────────────────────────────────────────
# Typography scale
# ─────────────────────────────────────────────────────────────

FONT_FAMILIES = {
    "serif":     ["Playfair Display", "DejaVu Serif", "serif"],
    "sans":      ["Source Sans 3", "Source Sans Pro", "DejaVu Sans", "sans-serif"],
    "mono":      ["IBM Plex Mono", "DejaVu Sans Mono", "monospace"],
}

# Sizes in points, kalibrasi untuk A2 print (420x594mm)
FONT_SCALE = {
    "title":        {"family": "serif", "size": 56, "weight": "black"},
    "subtitle":     {"family": "sans",  "size": 22, "weight": "regular"},
    "hook_number":  {"family": "serif", "size": 72, "weight": "black"},
    "panel_title":  {"family": "serif", "size": 28, "weight": "bold"},
    "panel_kicker": {"family": "sans",  "size": 14, "weight": "semibold"},
    "chart_label":  {"family": "sans",  "size": 11, "weight": "regular"},
    "annotation":   {"family": "sans",  "size": 10, "weight": "semibold"},
    "data_number":  {"family": "mono",  "size": 12, "weight": "medium"},
    "caption":      {"family": "sans",  "size": 9,  "weight": "regular"},
    "footer":       {"family": "sans",  "size": 8,  "weight": "regular"},
}


def font_kwargs(token: str) -> dict:
    """Return matplotlib kwargs dict untuk token tipografi."""
    spec = FONT_SCALE[token]
    family_name = {
        "serif": "serif",
        "sans": "sans-serif",
        "mono": "monospace",
    }[spec["family"]]
    weight_map = {
        "black": 900, "bold": 700, "semibold": 600,
        "medium": 500, "regular": 400,
    }
    return {
        "family": family_name,
        "size": spec["size"],
        "weight": weight_map.get(spec["weight"], 400),
        "color": COLOR_BODY,
    }


# ─────────────────────────────────────────────────────────────
# Region → display order untuk small multiples
# ─────────────────────────────────────────────────────────────

REGION_ORDER = [
    "Europe & Central Asia",
    "South Asia",
    "Middle East & North Africa",
    "Sub-Saharan Africa",
    "Americas",
    "East Asia & Pacific",
]

REGION_HIGHLIGHT = {
    "Europe & Central Asia": COLOR_SAFE,     # success story parity
    "East Asia & Pacific":   COLOR_ACCENT,    # stagnant outlier
}


# ─────────────────────────────────────────────────────────────
# Matplotlib rcParams setup
# ─────────────────────────────────────────────────────────────

def setup_matplotlib() -> None:
    """Terapkan rcParams global selaras dengan design system.

    Aman dipanggil berulang. Fonts jatuh ke DejaVu kalau Google Fonts
    belum ter-install — palette & layout tetap konsisten.
    """
    # PDF/SVG font embedding (Type 42 = publisher standard)
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["svg.fonttype"] = "none"

    # Font fallback chains
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.serif"] = FONT_FAMILIES["serif"]
    plt.rcParams["font.sans-serif"] = FONT_FAMILIES["sans"]
    plt.rcParams["font.monospace"] = FONT_FAMILIES["mono"]

    # Axes & ticks
    plt.rcParams["axes.edgecolor"] = COLOR_BODY
    plt.rcParams["axes.linewidth"] = 0.6
    plt.rcParams["axes.labelcolor"] = COLOR_BODY
    plt.rcParams["axes.titlecolor"] = COLOR_HEADLINE
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["xtick.color"] = COLOR_BODY
    plt.rcParams["ytick.color"] = COLOR_BODY
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9

    # Background
    plt.rcParams["figure.facecolor"] = COLOR_BG
    plt.rcParams["axes.facecolor"] = COLOR_BG
    plt.rcParams["savefig.facecolor"] = COLOR_BG

    # Grid
    plt.rcParams["grid.color"] = COLOR_GRIDLINE
    plt.rcParams["grid.linewidth"] = 0.4


def register_local_fonts(fonts_dir: str | Path = "poster/fonts") -> list[str]:
    """Load .ttf/.otf dari direktori lokal ke font manager matplotlib.

    Return daftar nama font yang berhasil di-load.
    Berguna kalau Google Fonts di-drop ke `poster/fonts/` tanpa install sistem.
    """
    fonts_dir = Path(fonts_dir)
    if not fonts_dir.exists():
        return []

    loaded = []
    for font_file in fonts_dir.rglob("*.ttf"):
        fm.fontManager.addfont(str(font_file))
        loaded.append(font_file.stem)
    for font_file in fonts_dir.rglob("*.otf"):
        fm.fontManager.addfont(str(font_file))
        loaded.append(font_file.stem)
    return loaded
