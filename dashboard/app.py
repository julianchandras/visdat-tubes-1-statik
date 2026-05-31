"""Dasbor Interaktif — Hukum Pernikahan Dini Global (Tugas Besar 2 IF4061).

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
    page_title="Dasbor Pernikahan Dini Global",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = datalib.load_data()

# ── Global CSS ───────────────────────────────────────────
# Panel detail (st.container border=True) kesan floating overlay.
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 0 2px 8px rgba(15, 76, 92, 0.08);
        backdrop-filter: blur(2px);
        padding-bottom: 0.6rem !important;
    }
    /* Caption — default muted (~#A0A4AB) terlalu menyatu dgn bg; bump kontras
       + sedikit lebih besar (revisi tim). */
    [data-testid="stCaption"], [data-testid="stCaptionContainer"] {
        color: #4D525E !important;
        font-size: 0.86rem !important;
        line-height: 1.45 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────
# State sync — proses event terjadwal SEBELUM widget di-render.
# ────────────────────────────────────────────────────────────
SEV_KEY = "sev_widget"           # multiselect label tingkat perlindungan
COUNTRY_KEY = "country_picker"   # selectbox pemilihan negara

# Klik negara di peta pada run sebelumnya → set country picker.
if "pending_map_iso3" in st.session_state:
    iso3 = st.session_state.pop("pending_map_iso3")
    if iso3:
        match = df.loc[df["iso3"] == iso3, "country"]
        if not match.empty:
            st.session_state[COUNTRY_KEY] = match.iloc[0]

# Klik tombol close panel detail → reset country picker ke None (placeholder).
if st.session_state.pop("pending_close_detail", False):
    st.session_state[COUNTRY_KEY] = None


# ────────────────────────────────────────────────────────────
# Sidebar — filter (atas) + unduh data (bawah)
# ────────────────────────────────────────────────────────────
def render_sidebar_filters(df):
    """Render bagian FILTER. Return (regions, incomes, severities) dgn value
    internal Inggris (untuk filter pandas), display label Indonesia di UI."""
    st.sidebar.header("Filter")
    # Region — display Indonesia, value Inggris
    region_picks_id = st.sidebar.multiselect(
        "Wilayah",
        options=[T.region_id(r) for r in T.REGION_ORDER],
        default=[],
        help="Kosong = semua wilayah. Pilih 1 wilayah → peta otomatis zoom.",
    )
    id_to_region = {T.region_id(r): r for r in T.REGION_ORDER}
    regions = [id_to_region[r] for r in region_picks_id]

    # Pendapatan
    income_picks_id = st.sidebar.multiselect(
        "Tingkat Pendapatan",
        options=[T.income_id(g) for g in T.INCOME_ORDER],
        default=[],
        help="Klasifikasi World Bank.",
    )
    id_to_income = {T.income_id(g): g for g in T.INCOME_ORDER}
    incomes = [id_to_income[g] for g in income_picks_id]

    # Tingkat perlindungan (sudah bahasa Indonesia di T.LOOP_SUMM_LABELS)
    sev_label_to_code = {T.LOOP_SUMM_LABELS[c]: c for c in T.LOOP_SUMM_ORDER}
    sev_picked = st.sidebar.multiselect(
        "Tingkat Perlindungan", options=list(sev_label_to_code.keys()),
        key=SEV_KEY,
        help="Filter berdasarkan ringkasan loophole hukum.",
    )
    severities = [sev_label_to_code[s] for s in sev_picked]
    return regions, incomes, severities


def render_sidebar_downloads(df, fdf):
    """Render bagian UNDUH DATA + caption sumber."""
    st.sidebar.divider()
    st.sidebar.markdown("**Unduh Data**")
    # Streamlit ≥1.34 mendukung Material icon native via `:material/<name>:`.
    st.sidebar.download_button(
        f"Data lengkap ({len(df)} negara)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="hukum-pernikahan-anak-2023-lengkap.csv",
        mime="text/csv",
        help="Dataset 193 negara hasil pembersihan.",
        use_container_width=True,
        icon=":material/download:",
    )
    st.sidebar.download_button(
        f"Data sesuai filter ({len(fdf)} negara)",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="hukum-pernikahan-anak-2023-terfilter.csv",
        mime="text/csv",
        help="Subset sesuai filter di atas.",
        use_container_width=True,
        icon=":material/download:",
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
    st.title("Dasbor Pernikahan Dini Global")
    st.markdown(
        "Tidak semua negara melindungi anak dari pernikahan dini "
        "(pernikahan dengan salah satu pasangan berusia di bawah 18 tahun). "
        "Pada dasbor ini Anda dapat melakukan eksplorasi terhadap data hukum "
        "terkait pernikahan dini di **193 negara anggota PBB** "
        "(WORLD Policy Analysis Center, 2023). Gunakan filter di sisi kiri "
        "untuk menelusuri pola berdasarkan wilayah, pendapatan, dan tingkat "
        "perlindungan."
    )
    k = datalib.kpi_metrics(fdf)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Negara terpilih", len(fdf))
    c2.metric("Mengizinkan Pernikahan Dini", k["under18"])
    c3.metric("Memiliki Celah Hukum", k["loophole"])
    c4.metric("Memungkinkan Pernikahan Usia ≤ 13 Thn", k["worst"])


# ────────────────────────────────────────────────────────────
# Panel detail negara
# ────────────────────────────────────────────────────────────
def render_country_detail(detail: dict | None) -> None:
    """Render panel detail. Font kompak, tanpa emoji, kesimpulan bold
    merah (buruk) atau hijau (bersih). Tombol close di pojok."""
    if not detail:
        st.info(
            "Cari negara di kotak pencarian, atau klik salah satu negara "
            "di peta, untuk melihat detail hukum pernikahannya."
        )
        return

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
        if st.button("✕", key="close_detail", help="Tutup panel detail"):
            st.session_state["pending_close_detail"] = True
            st.rerun()

    # Tampilkan wilayah & pendapatan dlm bahasa Indonesia (display label).
    region_display = T.region_id(detail['region']) if detail['region'] else "—"
    income_display = T.income_id(detail['income']) if detail['income'] else "—"
    st.markdown(
        f"<div style='font-size:0.82rem; color:{T.COLOR_BODY}; "
        f"line-height:1.55; margin-top:0.4rem;'>"
        f"<b>Wilayah:</b> {region_display}<br>"
        f"<b>Pendapatan:</b> {income_display}<br>"
        f"<b>Perlindungan:</b> {detail['perlindungan'] or '—'}<br>"
        f"<b>Usia min. perempuan:</b> {detail['minage_fem'] or '—'}<br>"
        f"<b>Usia min. laki-laki:</b> {detail['minage_mal'] or '—'}"
        f"</div>",
        unsafe_allow_html=True,
    )

    flags = []
    if detail["has_loophole_fem"]:
        flags.append("Memiliki celah hukum untuk perempuan")
    if detail["has_loophole_mal"]:
        flags.append("Memiliki celah hukum untuk laki-laki")
    if detail["has_gender_gap"]:
        flags.append("Memiliki kesenjangan usia antar gender")

    if flags:
        body = "<br>".join(flags)
        color = T.COLOR_DANGER
    else:
        body = "Tidak ada celah hukum maupun kesenjangan gender"
        color = T.COLOR_SAFE

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
render_sidebar_downloads(df, fdf)

render_header(fdf)
st.divider()

if fdf.empty:
    st.warning("Tidak ada negara yang cocok dengan filter. Longgarkan filter di sidebar.")
    st.stop()

zoom_region = regions[0] if len(regions) == 1 else None

MAP_CFG = {"displayModeBar": True, "scrollZoom": True,
           "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"]}
STATIC_CFG = {"displayModeBar": False, "scrollZoom": False, "staticPlot": False}

# ── Section 1: Peta + (Detail panel) + Pie ──
st.subheader("Peta Perlindungan Anak dari Pernikahan Dini")
st.caption(
    "Telusuri peta untuk melihat sebaran tingkat perlindungan anak. "
    "Klik negara mana pun atau gunakan kotak pencarian di bawah untuk "
    "membuka panel detail. Anda dapat menggeser dan memperbesar peta."
)

country_names = sorted(df["country"].dropna().unique().tolist())
# Selectbox tanpa string placeholder di options — pakai native index=None +
# placeholder argument (revisi tim grup G).
picked_name = st.selectbox(
    "Cari negara untuk lihat detail",
    options=country_names,
    key=COUNTRY_KEY,
    index=None,
    placeholder="Ketik atau pilih nama negara...",
)
focus_iso3 = None
detail = None
if picked_name:
    iso3 = df.loc[df["country"] == picked_name, "iso3"]
    if not iso3.empty:
        focus_iso3 = iso3.iloc[0]
        detail = datalib.country_detail(df, focus_iso3)

# Layout: revisi tim — peta TETAP BESAR; panel detail diperkecil saat aktif.
# Bukan 30:70 (overlay yg menutupi 70% peta) tapi 65:35 (peta dominan).
if focus_iso3:
    map_col, detail_col, donut_col = st.columns([2.0, 1.3, 1.0])
else:
    map_col, donut_col = st.columns([2.5, 1])
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
        with st.container(border=True):
            render_country_detail(detail)

with donut_col:
    st.markdown("<div style='height: 140px'></div>", unsafe_allow_html=True)
    st.plotly_chart(
        composition.render(df, severity_filter=severities),
        width="stretch", config=STATIC_CFG,
        key="pie",
    )

# ── Shared legend (HTML) — VERTIKAL di bawah pie (revisi tim grup E) ──
# Tiap warna di-stack vertikal dgn keterangan di samping, lebih jelas
# membaca skala warna ordinal dari hijau (terbaik) ke merah (terburuk).
def _swatch_row(color: str, label: str) -> str:
    return (
        f'<div style="display:flex; align-items:center; '
        f'margin:0.18em 0; font-size:11.5px; color:#2D3142;">'
        f'<span style="display:inline-block; width:18px; height:14px; '
        f'background:{color}; border:1px solid #FFF; border-radius:3px; '
        f'margin-right:0.5em; flex-shrink:0;"></span>'
        f'<span>{label}</span></div>'
    )

# Ide tim: keterangan legenda lebih ringkas tanpa prefix "1 masalah: ..."
SHORT_LEGEND_LABELS = {
    5.0: "Setara, ≥ 18 tahun",
    3.0: "Ada kesenjangan ATAU usia 14-17",
    2.0: "Ada kesenjangan DAN usia 14-17",
    1.0: "Bisa menikah ≤ 13 tahun",
    9.0: "Adat / agama",
}
# Vertical legend di kolom donut (di bawah pie chart). Pakai container width
# supaya tidak terlalu lebar.
with donut_col:
    legend_inner = '<div style="padding:0.5em 0.4em 0.2em 0.4em;">'
    legend_inner += '<div style="font-size:11px; color:#8A8F9A; '
    legend_inner += 'margin-bottom:0.3em; font-weight:600;">Tingkat Perlindungan</div>'
    for code in T.LOOP_SUMM_ORDER:
        legend_inner += _swatch_row(T.LOOP_SUMM_COLORS[code], SHORT_LEGEND_LABELS[code])
    legend_inner += _swatch_row(T.NO_DATA_COLOR, T.LABEL_NO_DATA)
    legend_inner += '</div>'
    st.markdown(legend_inner, unsafe_allow_html=True)

# ── Handler peta click ──
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

# ── Section 2 (urutan baru per revisi tim): Sankey Erosi Hukum ──
# Dipindah ke sini (sebelumnya di bawah Gender×Income | Loophole) supaya
# alur naratif: overview geografis (peta+pie) → mekanisme erosi (Sankey) →
# breakdown analitik kategorik (gender + loophole) → deep dive umur+temporal.
st.subheader("Erosi Hukum: Aliran Negara Antar Layer Hukum")
st.caption(
    "Aliran negara antar 3 layer hukum: Legal (tanpa exception) → Loop "
    "(+izin orang tua / adat) → Any (+kehamilan & persetujuan pengadilan). "
    "Lebar pita = jumlah negara. Pita yang turun dari ≥ 18 ke kategori usia "
    "lebih muda menandakan erosi perlindungan akibat exception yang diakui hukum."
)
st.plotly_chart(
    erosion_sankey.render(fdf),
    width="stretch", config=STATIC_CFG,
)

st.divider()

# ── Section 3: Kesenjangan Gender × Pendapatan ║ Celah Hukum ──
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Kesenjangan Gender menurut Pendapatan")
    st.caption(
        "Persentase negara di tiap tingkat pendapatan yang mengatur usia "
        "minimum pernikahan ≥ 18 tahun, dipisahkan menurut gender. Selisih "
        "antara bar perempuan dan laki-laki menunjukkan adanya kesenjangan."
    )
    st.plotly_chart(gender_income.render(fdf), width="stretch", config=STATIC_CFG)
with col_right:
    st.subheader("Celah Hukum Pernikahan Anak")
    st.caption(
        "Apa saja alasan yang memungkinkan terjadinya pernikahan dini akibat "
        "celah hukum? Diagram menunjukkan jumlah negara yang mengizinkan "
        "pernikahan dini untuk tiap alasan, dipecah menurut tingkat pendapatan. "
        "Celah hukum = ketentuan yang memungkinkan pernikahan di bawah usia "
        "minimum yang ditetapkan hukum umum."
    )
    st.plotly_chart(loopholes.render(fdf), width="stretch", config=STATIC_CFG)

st.divider()

# ── Section 4: Tangga Umur ║ Timeseries ──
bot_left, bot_right = st.columns([1, 1])
with bot_left:
    st.subheader("Tangga Perlindungan menurut Umur Anak")
    st.caption(
        "Untuk anak umur ini, di berapa negara mereka secara hukum dilarang "
        "menikah, hanya boleh dengan persetujuan pengadilan/kehamilan, boleh "
        "dengan izin orang tua, atau tanpa pembatasan?  \n"
        "**P** = Perempuan · **L** = Laki-laki"
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
        "Persentase negara dengan usia minimum pernikahan ≥ 18 tahun "
        "(dengan izin orang tua) sepanjang tahun. Pilih rentang tahun untuk "
        "fokus ke periode tertentu."
    )
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
st.caption(
    "Dataset: WORLD Policy Analysis Center, Child Marriage Laws 2023 · "
    "DOI: 10.25828/v8s6-jz31 · Lisensi CC-BY-SA. "
    "Dasbor: Kelompok 11 IF4061 Visualisasi Data, Institut Teknologi Bandung."
)
