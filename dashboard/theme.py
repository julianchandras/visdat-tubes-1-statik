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

NO_DATA_COLOR = "#9A9A9A"   # medium grey — kontras lebih kuat dari 'di luar filter'
LABEL_NO_DATA = "Tanpa data"

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
