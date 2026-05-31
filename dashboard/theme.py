"""Design tokens dashboard Tubes 2 — di-port dari poster/theme.py.

Konsistensi brand Fase 1 → Fase 2: palet & label sama, tapi disusun untuk
Plotly + Streamlit (bukan matplotlib). Single source of truth warna/label.
"""
from __future__ import annotations

# ── Palet loop_summ (severity perlindungan anak) ──
# Order kebaikan: 5 (terbaik) → 3 → 2 → 1 (terburuk) → 9 (ambigu).
LOOP_SUMM_COLORS = {
    1.0: "#A70400",   # worst: kesenjangan + ≤13 tahun (merah paling gelap)
    2.0: "#FF0700",   # kesenjangan DAN 14-17 (merah jenuh)
    3.0: "#FFA6A4",   # kesenjangan ATAU 14-17 (merah-pink pucat)
    5.0: "#76B900",   # kesetaraan + ≥18 (hijau)
    9.0: "#FFD60A",   # unknown (kuning gold)
}

# Label tingkat perlindungan — bahasa Indonesia, gaya dasbor (bukan
# infografis); prefix "1 masalah:" / "2 masalah:" dihapus per revisi tim.
LOOP_SUMM_LABELS = {
    5.0: "Kesetaraan dan usia ≥ 18 tahun",
    3.0: "Kesenjangan ATAU usia 14-17 tahun",
    2.0: "Kesenjangan DAN usia 14-17 tahun",
    1.0: "Bisa menikah ≤ 13 tahun",
    9.0: "Mungkin < 18 tahun (diatur adat/agama)",
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

NO_DATA_COLOR = "#9A9A9A"   # medium grey — kontras lebih kuat dari 'di luar filter'
LABEL_NO_DATA = "Tanpa data"

# ── Variant DIM untuk mode focus 1 negara ──
# Sebelumnya pakai alpha-only (rgba(... ,0.30)) → warna naturally pucat seperti
# pink #FFA6A4 jadi hampir indistinguishable dari non-focus pink lain.
# Solusi (revisi tim, opsi 1): DESATURATE — blend warna ke gray berdasarkan
# luminance + alpha sedang. Hasil: setiap kategori jadi muted neutral dgn
# hint warna asli (pink → beige-pink, hijau → olive-grey, dst). Plus border
# thicker pada focus trace di map_choropleth.py (opsi 3) untuk extra "pop".
DIM_GRAY_BLEND = 0.70      # 70% blend ke gray; 30% sisa warna asli
DIM_ALPHA = 0.55           # alpha menengah (tidak terlalu pucat)


def _desaturate_rgba(hex_color: str,
                     gray_blend: float = DIM_GRAY_BLEND,
                     alpha: float = DIM_ALPHA) -> str:
    """Convert hex → rgba dgn blend ke gray (luminance-based) + alpha."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    # Rec. 709 luminance approximation
    Y = 0.299 * r + 0.587 * g + 0.114 * b
    nr = int(round(r * (1 - gray_blend) + Y * gray_blend))
    ng = int(round(g * (1 - gray_blend) + Y * gray_blend))
    nb = int(round(b * (1 - gray_blend) + Y * gray_blend))
    return f"rgba({nr},{ng},{nb},{alpha:.2f})"


LOOP_SUMM_COLORS_DIM = {
    code: _desaturate_rgba(color)
    for code, color in LOOP_SUMM_COLORS.items()
}
NO_DATA_COLOR_DIM = _desaturate_rgba(NO_DATA_COLOR)

# Bounding box per region untuk auto-zoom (lon_min, lon_max, lat_min, lat_max).
# Diset agar negara di tiap region masuk frame penuh, sedikit padding di tepi.
REGION_BBOX = {
    "Europe & Central Asia":     (-25, 180,  35,  82),  # incl. Russia
    "South Asia":                ( 60,  98,   5,  38),
    "Middle East & North Africa":(-18,  65,  12,  42),
    "Sub-Saharan Africa":        (-20,  52, -36,  20),
    "Americas":                  (-170, -30, -56,  73),
    "East Asia & Pacific":       ( 73, 185, -50,  55),
}

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

# ── Palet "Tangga Perlindungan per Umur" — 4 tingkat protect_girl_* / protect_boy_*
# Urutan moral: hijau (paling protektif) → kuning → orange → merah (tanpa perlindungan).
# Sengaja TIDAK pakai 5 warna loop_summ supaya secara visual berbeda — ini variabel berbeda.
PROTECT_COLORS = {
    5.0: "#1A7F3C",   # Dilarang secara hukum — paling protektif (hijau gelap)
    3.0: "#F4B400",   # Hanya court approval / pregnancy — kuning warning
    2.0: "#E07A5F",   # Boleh dgn izin ortu / adat — terracotta accent
    1.0: "#7B0000",   # Tanpa pembatasan — merah pekat (paling parah)
}
PROTECT_LABELS = {
    5.0: "Dilarang secara hukum",
    3.0: "Hanya court approval / kehamilan",
    2.0: "Boleh dgn izin orang tua / adat",
    1.0: "Tanpa pembatasan",
}
PROTECT_ORDER = [5.0, 3.0, 2.0, 1.0]   # paling protektif → paling parah

# ── Palet usia minimum untuk Heatmap Erosi — 5 step ordinal usia.
# Dibedakan dari LOOP_SUMM_COLORS karena ini variabel berbeda (usia, bukan composite).
# Skema: makin tua usia min, makin biru-tenang; makin muda, makin merah-alert.
MINAGE_COLORS = {
    5.0: "#1F4E79",   # ≥18 thn — biru tenang (aman)
    3.0: "#7BAEBF",   # 16-17 thn
    2.0: "#E07A5F",   # 14-15 thn
    1.0: "#7B0000",   # ≤13 thn — merah gelap
    9.0: "#9A9A9A",   # Unknown adat/agama — abu netral
}
MINAGE_LABELS = {
    5.0: "≥ 18 tahun",
    3.0: "16-17 tahun",
    2.0: "14-15 tahun",
    1.0: "≤ 13 tahun",
    9.0: "Tidak diketahui",
}
MINAGE_ORDER = [5.0, 3.0, 2.0, 1.0, 9.0]

# Nama-nama layer 5-step "tangga erosi" untuk Heatmap (urutan: paling murni → paling longgar).
EROSION_LAYERS = [
    ("minage_fem_leg",   "Legal"),
    ("minage_fem_pc",    "+ Izin ortu"),
    ("minage_fem_crlaw", "+ Adat/agama"),
    ("minage_fem_loop",  "Loophole gab."),
    ("minage_fem_any",   "Semua exception"),
]

# ── Palet income (selaras Panel C poster — teal monokromatik) ──
INCOME_COLORS = {
    "Low-income":    "#0F4C5C",
    "Middle-income": "#5A8F95",
    "High-income":   "#B5D0CC",
}
INCOME_ORDER = ["Low-income", "Middle-income", "High-income"]

# ── Region order (selaras poster) ──
# Values internal = Inggris ISO (matching kolom CSV utk filter); display label
# Indonesia via REGION_LABELS_ID. Pola sama untuk wb_econ_label.
REGION_ORDER = [
    "Europe & Central Asia",
    "South Asia",
    "Middle East & North Africa",
    "Sub-Saharan Africa",
    "Americas",
    "East Asia & Pacific",
]

# ── i18n: mapping value internal (Inggris) ↔ label display (Indonesia) ──
# Single source of truth — UI di mana saja menampilkan label Indonesia,
# tapi filter pandas tetap match dgn value Inggris di CSV (no data migration).
REGION_LABELS_ID = {
    "Europe & Central Asia":      "Eropa dan Asia Tengah",
    "South Asia":                 "Asia Selatan",
    "Middle East & North Africa": "Timur Tengah dan Afrika Utara",
    "Sub-Saharan Africa":         "Afrika Sub-Sahara",
    "Americas":                   "Amerika",
    "East Asia & Pacific":        "Asia Timur dan Pasifik",
}
INCOME_LABELS_ID = {
    "Low-income":    "Berpendapatan Rendah",
    "Middle-income": "Berpendapatan Menengah",
    "High-income":   "Berpendapatan Tinggi",
}


def region_id(en: str) -> str:
    """Display label Indonesia untuk region. Fallback ke value asli."""
    return REGION_LABELS_ID.get(en, en)


def income_id(en: str) -> str:
    """Display label Indonesia untuk income group. Fallback ke value asli."""
    return INCOME_LABELS_ID.get(en, en)

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


def country_zoom_bounds(lon_min, lat_min, lon_max, lat_max,
                        pad_frac: float = 0.30, min_pad: float = 2.0):
    """Hitung bounding box auto-zoom untuk satu negara dgn padding sehat.

    Mengatasi 2 edge case:
    - Negara raksasa (Russia, USA, Canada) yang spannya >60° lon: gunakan
      centroid + lebar maks (40° lon, 25° lat) supaya tidak balik ke world view.
    - Negara lintas antimeridian (mis. Russia di shapefile NE split ke -180/+180):
      span jadi 360° padahal sebenarnya negara tersebut compact di satu sisi.
      Sama penanganannya — pakai centroid + lebar maks.

    Return (lon_lo, lon_hi, lat_lo, lat_hi) atau None bila input invalid.
    """
    import math
    if any(v is None or (isinstance(v, float) and math.isnan(v))
           for v in (lon_min, lat_min, lon_max, lat_max)):
        return None
    lon_span = lon_max - lon_min
    lat_span = lat_max - lat_min
    # Centroid bbox
    cx = (lon_min + lon_max) / 2
    cy = (lat_min + lat_max) / 2
    # Negara raksasa atau lintas antimeridian → clamp ke 40°×25° around centroid
    if lon_span > 60 or lat_span > 35:
        return cx - 20, cx + 20, cy - 12, cy + 12
    lon_pad = max(min_pad, lon_span * pad_frac)
    lat_pad = max(min_pad, lat_span * pad_frac)
    return (lon_min - lon_pad, lon_max + lon_pad,
            lat_min - lat_pad, lat_max + lat_pad)


def lock_static(fig):
    """Disable drag-pan & axis range untuk chart non-peta.

    Plotly default mengaktifkan drag-pan/box-select pada chart Cartesian
    walau mode bar di-hide via config. User minta chart selain peta benar2
    tidak bisa digeser. Hover tetap aktif (staticPlot=False di config).
    Sankey/Pie tidak punya axes tapi dragmode=False tetap berlaku global.
    """
    fig.update_layout(dragmode=False)
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig
