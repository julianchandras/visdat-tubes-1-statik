"""Dashboard Interaktif — Hukum Pernikahan Anak (Tugas Besar 2 IF4061).

Entry point Streamlit. Jalankan lokal:
    streamlit run dashboard/app.py

Struktur & rasional: docs-system-development/tubes2/spec_dashboard.md
"""
from __future__ import annotations

import streamlit as st

import theme as T
import data as datalib
from charts import (
    map_choropleth, gender_income, loopholes, timeseries, composition,
    protect_ladder, erosion_sankey,
)

# ── Page config ──
st.set_page_config(
    page_title="Hukum Pernikahan Anak — Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = datalib.load_data()

# ── Global CSS injection ──────────────────────────────────────────
# Beri panel detail (st.container border=True) kesan "floating overlay":
# background semi-transparan + shadow halus. Streamlit tidak punya true
# overlay/popup; ini pendekatan terdekat. Targeting via stVerticalBlock-
# BorderWrapper data-testid (Streamlit ≥1.34).
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.85);
        box-shadow: 0 2px 8px rgba(15, 76, 92, 0.08);
        backdrop-filter: blur(2px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────
# State sync — proses event terjadwal SEBELUM widget di-render.
# Pola: handler menulis ke session_state[<flag>], di awal run kita pop &
# mutasi widget keys, lalu widget akan terbaca dgn value baru di run ini.
# ────────────────────────────────────────────────────────────
SEV_KEY = "sev_widget"           # multiselect label tingkat perlindungan
COUNTRY_KEY = "country_picker"   # selectbox pemilihan negara
PLACEHOLDER = "— Pilih atau ketik nama negara —"  # def di atas; dipakai handler + selectbox

# Klik negara di peta pada run sebelumnya → set country picker.
if "pending_map_iso3" in st.session_state:
    iso3 = st.session_state.pop("pending_map_iso3")
    if iso3:
        match = df.loc[df["iso3"] == iso3, "country"]
        if not match.empty:
            st.session_state[COUNTRY_KEY] = match.iloc[0]

# Klik tombol close panel detail → reset country picker SECARA EKSPLISIT ke
# PLACEHOLDER (bukan del session_state) supaya widget benar2 reset visual.
# Approach del kadang gagal sync di Streamlit Cloud karena widget retention.
if st.session_state.pop("pending_close_detail", False):
    st.session_state[COUNTRY_KEY] = PLACEHOLDER


# ────────────────────────────────────────────────────────────
# Sidebar — filter global (atas) + tombol unduh data (bawah)
# ────────────────────────────────────────────────────────────
def render_sidebar_filters(df):
    """Render bagian FILTER di sidebar. Return (regions, incomes, severities)."""
    st.sidebar.header("Filter")
    regions = st.sidebar.multiselect(
        "Region", options=T.REGION_ORDER, default=[],
        help="Kosong = semua region. Pilih 1 region → peta otomatis zoom.",
    )
    incomes = st.sidebar.multiselect(
        "Tingkat pendapatan", options=T.INCOME_ORDER, default=[],
        help="Klasifikasi World Bank.",
    )
    sev_label_to_code = {T.LOOP_SUMM_LABELS[c]: c for c in T.LOOP_SUMM_ORDER}
    sev_picked = st.sidebar.multiselect(
        "Tingkat perlindungan", options=list(sev_label_to_code.keys()),
        key=SEV_KEY,
        help="Filter berdasarkan ringkasan loophole (loop_summ).",
    )
    severities = [sev_label_to_code[s] for s in sev_picked]
    return regions, incomes, severities


def render_sidebar_downloads(df, fdf):
    """Render bagian UNDUH DATA + caption sumber di bawah sidebar."""
    st.sidebar.divider()
    st.sidebar.markdown("**Unduh data**")
    st.sidebar.download_button(
        f"Data lengkap ({len(df)} negara)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="hukum-pernikahan-anak-2023-lengkap.csv",
        mime="text/csv",
        help="Dataset 193 negara hasil pembersihan.",
        use_container_width=True,
    )
    st.sidebar.download_button(
        f"Data sesuai filter ({len(fdf)} negara)",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="hukum-pernikahan-anak-2023-terfilter.csv",
        mime="text/csv",
        help="Subset sesuai filter di atas.",
        use_container_width=True,
    )
    st.sidebar.divider()
    st.sidebar.caption(
        "Sumber: WORLD Policy Analysis Center, Child Marriage Laws 2023 "
        "(193 negara anggota PBB). Lisensi CC-BY-SA."
    )


# ────────────────────────────────────────────────────────────
# Header + KPI
# ────────────────────────────────────────────────────────────
def render_header(fdf):
    st.title("Tidak Semua Negara Melindungi Anak dari Pernikahan Dini")
    st.markdown(
        "Eksplorasi hukum usia minimum pernikahan di **193 negara anggota PBB** "
        "(WORLD Policy Analysis Center, 2023). Gunakan filter di sisi kiri untuk "
        "menelusuri pola berdasarkan region, pendapatan, dan tingkat perlindungan."
    )
    k = datalib.kpi_metrics(fdf)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Negara terpilih", len(fdf))
    c2.metric("Mengizinkan nikah < 18 thn", k["under18"])
    c3.metric("Punya celah hukum", k["loophole"])
    c4.metric("Ada path nikah ≤ 13 thn", k["worst"])


# ────────────────────────────────────────────────────────────
# Panel detail negara
# ────────────────────────────────────────────────────────────
def render_country_detail(detail: dict | None) -> None:
    """Render panel detail negara di kolom kanan saat peta menyempit.

    Revisi tim: font kecil & proporsional, tanpa emoji, kesimpulan bold
    dgn warna merah (buruk) atau hijau (bersih). Tombol close di pojok.
    """
    if not detail:
        st.info(
            "Cari negara di kotak pencarian, atau klik salah satu negara "
            "di peta, untuk melihat detail hukum pernikahannya."
        )
        return

    # Header: nama + ISO + tombol close pojok kanan
    hdr_left, hdr_right = st.columns([5, 1])
    with hdr_left:
        st.markdown(
            f"<div style='font-size:1rem; font-weight:700; color:{T.COLOR_HEADLINE};'>"
            f"{detail['country']}"
            f" <span style='font-size:0.75rem; color:{T.COLOR_MUTED}; "
            f"font-weight:400;'>· {detail['iso3']}</span></div>",
            unsafe_allow_html=True,
        )
    with hdr_right:
        # Silang "✕" — simbol close standar yang universal dikenal.
        if st.button("✕", key="close_detail", help="Tutup panel detail"):
            st.session_state["pending_close_detail"] = True
            st.rerun()

    # Body — kompak, single block tanpa horizontal rule
    st.markdown(
        f"<div style='font-size:0.82rem; color:{T.COLOR_BODY}; "
        f"line-height:1.55; margin-top:0.4rem;'>"
        f"<b>Region:</b> {detail['region']}<br>"
        f"<b>Pendapatan:</b> {detail['income'] or '—'}<br>"
        f"<b>Perlindungan:</b> {detail['perlindungan'] or '—'}<br>"
        f"<b>Usia min. perempuan:</b> {detail['minage_fem'] or '—'}<br>"
        f"<b>Usia min. laki-laki:</b> {detail['minage_mal'] or '—'}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Kesimpulan: bold, MERAH bila ada celah/gap; HIJAU bila bersih.
    # Tanpa emoji (revisi tim).
    flags = []
    if detail["has_loophole_fem"]:
        flags.append("Ada celah hukum untuk perempuan")
    if detail["has_loophole_mal"]:
        flags.append("Ada celah hukum untuk laki-laki")
    if detail["has_gender_gap"]:
        flags.append("Ada kesenjangan usia antar gender")

    if flags:
        body = "<br>".join(flags)
        color = T.COLOR_DANGER       # #C71E3A — merah
    else:
        body = "Tidak ada celah hukum maupun kesenjangan gender"
        color = T.COLOR_SAFE         # #2A9D8F — hijau-teal

    st.markdown(
        f"<div style='font-size:0.85rem; color:{color}; font-weight:700; "
        f"margin-top:0.6rem; line-height:1.45;'>{body}</div>",
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────
regions, incomes, severities = render_sidebar_filters(df)
fdf = datalib.filter_data(df, regions, incomes, severities)
render_sidebar_downloads(df, fdf)   # tombol unduh di bawah filter (revisi tim)

render_header(fdf)
st.divider()

if fdf.empty:
    st.warning("Tidak ada negara yang cocok dengan filter. Longgarkan filter di sidebar.")
    st.stop()

# Auto-zoom ke region bila persis 1 region dipilih (revisi tim).
zoom_region = regions[0] if len(regions) == 1 else None

# Plotly config:
# - Peta: zoom & pan diaktifkan tapi dibatasi (geo bounds di chart).
# - Non-peta: mode bar off — chart lain tak perlu di-zoom.
MAP_CFG = {"displayModeBar": True, "scrollZoom": True,
           "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"]}
STATIC_CFG = {"displayModeBar": False, "scrollZoom": False, "staticPlot": False}

# ── Section 1: Peta hero + Search + (Detail panel) + Donut komposisi ──
st.subheader("Peta Perlindungan Anak dari Pernikahan Dini")
st.caption(
    "Arahkan kursor untuk detail; klik negara atau cari di kotak pencarian "
    "untuk membuka panel detail; scroll/drag untuk zoom & geser peta."
)

country_names = sorted(df["country"].dropna().unique().tolist())
options = [PLACEHOLDER] + country_names
# Simpel: index dihitung dari nilai session_state saat ini supaya reset
# benar2 sinkron setelah pending_close_detail handler.
current_pick = st.session_state.get(COUNTRY_KEY, PLACEHOLDER)
current_idx = options.index(current_pick) if current_pick in options else 0
picked_name = st.selectbox(
    "Cari negara untuk lihat detail",
    options=options,
    key=COUNTRY_KEY,
    index=current_idx,
)
focus_iso3 = None
detail = None
if picked_name and picked_name != PLACEHOLDER:
    iso3 = df.loc[df["country"] == picked_name, "iso3"]
    if not iso3.empty:
        focus_iso3 = iso3.iloc[0]
        detail = datalib.country_detail(df, focus_iso3)

# Layout kondisional: jika ada negara fokus → peta menyempit, detail muncul
# di sebelah; jika tidak → peta + donut side-by-side seperti biasa.
if focus_iso3:
    map_col, detail_col, donut_col = st.columns([1.2, 2.0, 1.2])
else:
    map_col, donut_col = st.columns([2, 1])
    detail_col = None

with map_col:
    map_event = st.plotly_chart(
        map_choropleth.render(
            df,
            selected_iso3=fdf["iso3"].tolist(),
            focus_iso3=focus_iso3,
            zoom_region=zoom_region,
        ),
        width="stretch", config=MAP_CFG,
        on_select="rerun", selection_mode=["points"], key="map",
    )

if detail_col is not None:
    with detail_col:
        # Bordered container → CSS global memberikan bg semi-transparan +
        # shadow halus, kesan panel floating yang "opacity sedikit".
        with st.container(border=True):
            render_country_detail(detail)

with donut_col:
    # Spacer untuk vertically center pie (240px) terhadap peta (520px).
    # (520 - 240) / 2 ≈ 140px. Streamlit kolom default mengisi dari atas;
    # tanpa spacer pie menggantung di top, banyak whitespace di bawahnya.
    st.markdown("<div style='height: 140px'></div>", unsafe_allow_html=True)
    # Pie chart DIBATALKAN sbg filter trigger (Streamlit Cloud Plotly Pie
    # selection tidak reliable lintas versi). Hanya display + hover.
    st.plotly_chart(
        composition.render(df, severity_filter=severities),
        width="stretch", config=STATIC_CFG,
        key="pie",
    )

# ── Shared legend (HTML) — di tengah, full-width di bawah row peta+pie ──
# Plotly legend terikat per-figure & tidak bisa spanning antar kolom Streamlit.
# Solusinya: render legend custom via HTML supaya benar2 center di antara peta
# & pie (jadi satu visual unit), tidak menumpuk di pojok kanan peta.
def _swatch(color: str, label: str) -> str:
    return (
        f'<span style="display:inline-flex; align-items:center; '
        f'margin:0 0.6em; font-size:12px; color:#2D3142;">'
        f'<span style="display:inline-block; width:14px; height:14px; '
        f'background:{color}; border:1px solid #FFF; border-radius:3px; '
        f'margin-right:0.4em;"></span>{label}</span>'
    )

legend_html = '<div style="text-align:center; padding:0.4em 0 0.8em 0;">'
legend_html += '<span style="font-size:12px; color:#8A8F9A; margin-right:0.5em;">Tingkat perlindungan:</span>'
for code in T.LOOP_SUMM_ORDER:
    legend_html += _swatch(T.LOOP_SUMM_COLORS[code], T.LOOP_SUMM_LABELS[code])
legend_html += _swatch(T.NO_DATA_COLOR, T.LABEL_NO_DATA)
legend_html += '</div>'
st.markdown(legend_html, unsafe_allow_html=True)

# ── Handler event: peta click → schedule country picker update.
# Klik bisa hit DUA jenis trace:
#   1) Polygon choropleth → point dict punya field "location" (= iso3)
#   2) Bubble scatter_geo → tidak ada "location"; pakai customdata[5] = iso3
# Handler harus toleran terhadap dua-duanya supaya bubble dot juga klikabel.
map_pts = (map_event.get("selection", {}) or {}).get("points", []) if map_event else []
if map_pts:
    pt = map_pts[0]
    clicked_iso3 = pt.get("location")
    if not clicked_iso3:
        cd = pt.get("customdata")
        if cd and len(cd) > 5:
            clicked_iso3 = cd[5]
    if clicked_iso3 and clicked_iso3 != focus_iso3:
        st.session_state["pending_map_iso3"] = clicked_iso3
        st.rerun()

st.divider()

# ── Section 2 (urutan baru): Gender×Income | Loophole — analisis kategorik ──
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Kesenjangan Gender menurut Pendapatan")
    st.caption("% negara dengan usia minimum pernikahan ≥ 18 tahun.")
    st.plotly_chart(gender_income.render(fdf), width="stretch", config=STATIC_CFG)
with col_right:
    st.subheader("Celah Hukum Pernikahan Anak")
    st.caption("Jumlah negara per tipe celah hukum, dipecah tingkat pendapatan.")
    st.plotly_chart(loopholes.render(fdf), width="stretch", config=STATIC_CFG)

st.divider()

# ── Section 3 (urutan baru): Sankey Erosi Hukum — mekanisme & layer story ──
st.subheader("Erosi Hukum: Aliran Negara Antar Layer Hukum")
st.caption(
    "Aliran negara antar 3 layer hukum: Legal (tanpa exception) → Loop "
    "(+izin ortu/adat) → Any (+kehamilan & court approval). Lebar pita = jumlah "
    "negara. Pita yang 'jatuh' dari ≥18 ke kategori usia lebih muda = erosi "
    "perlindungan akibat exception yang diakui hukum."
)
st.plotly_chart(
    erosion_sankey.render(fdf),
    width="stretch", config=STATIC_CFG,
)

st.divider()

# ── Section 4 (paling bawah): Tangga Umur ║ Timeseries — deep dive granular ──
bot_left, bot_right = st.columns([1, 1])
with bot_left:
    st.subheader("Tangga Perlindungan menurut Umur Anak")
    st.caption(
        "Untuk anak umur ini, di berapa negara mereka secara hukum dilarang "
        "menikah, hanya boleh dgn pengadilan/kehamilan, boleh dgn izin orang tua, "
        "atau tanpa pembatasan?"
    )
    age_choice = st.radio(
        "Umur anak",
        options=[13, 15, 17],
        horizontal=True,
        format_func=lambda a: f"{a} tahun",
        key="protect_age",
        label_visibility="collapsed",
    )
    st.plotly_chart(
        protect_ladder.render(fdf, age=age_choice),
        width="stretch", config=STATIC_CFG,
    )
with bot_right:
    st.subheader("Perkembangan Perlindungan Hukum, 1995–2023")
    st.caption(
        "% negara dengan usia min. ≥ 18 (dengan izin orang tua). Geser rentang "
        "tahun untuk fokus periode tertentu."
    )
    # Filter tahun: 2 selectbox terpisah (start & end), end constrained ≥ start
    # supaya tidak ada kombinasi invalid. Lebih presisi drpd slider dual-handle.
    YEARS = list(range(1995, 2024))
    y_col1, y_col2 = st.columns(2)
    with y_col1:
        start_year = st.selectbox(
            "Tahun mulai", options=YEARS, index=0, key="ts_start_year",
        )
    with y_col2:
        end_options = [y for y in YEARS if y >= start_year]
        end_year = st.selectbox(
            "Tahun akhir", options=end_options,
            index=len(end_options) - 1, key="ts_end_year",
        )
    st.plotly_chart(
        timeseries.render(fdf, year_range=(start_year, end_year)),
        width="stretch", config=STATIC_CFG,
    )

st.divider()

# ── Footer caption (tombol unduh sudah dipindah ke sidebar) ──
st.caption(
    "Dataset: WORLD Policy Analysis Center, Child Marriage Laws 2023 · "
    "DOI: 10.25828/v8s6-jz31 · Lisensi CC-BY-SA. "
    "Dashboard: Kelompok 11 IF4061 Visualisasi Data, Institut Teknologi Bandung."
)
