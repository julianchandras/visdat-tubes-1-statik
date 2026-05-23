"""Design tokens dashboard Tubes 2 — di-port dari poster/theme.py.

Konsistensi brand Fase 1 → Fase 2: palet & label sama, tapi disusun untuk
Plotly + Streamlit (bukan matplotlib). Single source of truth warna/label.
"""
from __future__ import annotations

# ── Palet loop_summ (severity perlindungan anak) ──
# Order kebaikan: 5 (terbaik) → 3 → 2 → 1 (terburuk) → 9 (ambigu).
LOOP_SUMM_COLORS = {
    1.0: "#A50F15",   # worst: kesenjangan + ≤13 tahun
    2.0: "#DE2D26",   # kesenjangan DAN 14-17
    3.0: "#FCAE91",   # kesenjangan ATAU 14-17 (salmon)
    5.0: "#76B900",   # kesetaraan + ≥18 (hijau)
    9.0: "#FFD60A",   # unknown (kuning gold)
}

LOOP_SUMM_LABELS = {
    5.0: "Kesetaraan & usia ≥ 18 tahun",
    3.0: "1 masalah: kesenjangan ATAU usia 14-17",
    2.0: "2 masalah: kesenjangan DAN usia 14-17",
    1.0: "Bisa menikah ≤ 13 tahun",
    9.0: "Mungkin < 18 (diatur adat/agama)",
}
# Label ringkas untuk legend peta (label penuh tetap dipakai di hover & donut).
LOOP_SUMM_SHORT = {
    5.0: "Setara, ≥ 18 thn",
    3.0: "1 masalah",
    2.0: "2 masalah",
    1.0: "Bisa ≤ 13 thn",
    9.0: "Adat/agama",
}
# Urutan tampil (legend, sumbu kategori): terbaik → terburuk → ambigu.
LOOP_SUMM_ORDER = [5.0, 3.0, 2.0, 1.0, 9.0]

NO_DATA_COLOR = "#D9D9D9"
LABEL_NO_DATA = "Tanpa data"

# ── Warna gender ──
COLOR_FEMALE = "#C71E3A"
COLOR_MALE = "#1F4E79"

# ── Warna brand / UI ──
COLOR_HEADLINE = "#0F4C5C"   # deep teal
COLOR_BODY = "#2D3142"
COLOR_MUTED = "#8A8F9A"
COLOR_ACCENT = "#E07A5F"     # terracotta
COLOR_BG = "#F8F9FA"
COLOR_GRIDLINE = "#DDE0E3"
COLOR_DANGER = "#C71E3A"
COLOR_SAFE = "#2A9D8F"

# ── Palet income (selaras Panel C poster — teal monokromatik) ──
INCOME_COLORS = {
    "Low-income":    "#0F4C5C",
    "Middle-income": "#5A8F95",
    "High-income":   "#B5D0CC",
}
INCOME_ORDER = ["Low-income", "Middle-income", "High-income"]

# ── Region order (selaras poster) ──
REGION_ORDER = [
    "Europe & Central Asia",
    "South Asia",
    "Middle East & North Africa",
    "Sub-Saharan Africa",
    "Americas",
    "East Asia & Pacific",
]

# ── Font stack (Streamlit config.toml memuat font utama) ──
FONT_SERIF = "Playfair Display, Georgia, serif"
FONT_SANS = "Source Sans 3, -apple-system, Segoe UI, sans-serif"

# Template Plotly default untuk seluruh chart (konsistensi visual).
# Tanpa title_font: judul section sudah dipegang st.subheader; menyetel
# title_font tanpa teks membuat Plotly 6 merender judul literal "undefined".
PLOTLY_LAYOUT = dict(
    font=dict(family=FONT_SANS, color=COLOR_BODY, size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=30, b=10),
    hoverlabel=dict(font=dict(family=FONT_SANS, size=12)),
    colorway=[COLOR_HEADLINE, COLOR_ACCENT, COLOR_SAFE, COLOR_MALE, COLOR_FEMALE],
)
