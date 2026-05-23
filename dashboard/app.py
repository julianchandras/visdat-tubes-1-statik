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

# ────────────────────────────────────────────────────────────
# State sync — proses event terjadwal SEBELUM widget di-render.
# Pola: handler menulis ke session_state[<flag>], di awal run kita pop &
# mutasi widget keys, lalu widget akan terbaca dgn value baru di run ini.
# ────────────────────────────────────────────────────────────
SEV_KEY = "sev_widget"          # multiselect label tingkat perlindungan
COUNTRY_KEY = "country_picker"  # selectbox pemilihan negara

# Klik slice pie pada run sebelumnya → set filter perlindungan ke kategori itu.
if "pending_pie_label" in st.session_state:
    lbl = st.session_state.pop("pending_pie_label")
    if lbl is None:
        st.session_state[SEV_KEY] = []
    else:
        st.session_state[SEV_KEY] = [lbl]

# Klik negara di peta pada run sebelumnya → set country picker.
if "pending_map_iso3" in st.session_state:
    iso3 = st.session_state.pop("pending_map_iso3")
    if iso3:
        match = df.loc[df["iso3"] == iso3, "country"]
        if not match.empty:
            st.session_state[COUNTRY_KEY] = match.iloc[0]


# ────────────────────────────────────────────────────────────
# Sidebar — filter global
# ────────────────────────────────────────────────────────────
def render_sidebar(df):
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
        help="Bisa juga dipilih dengan klik slice pie chart komposisi.",
    )
    severities = [sev_label_to_code[s] for s in sev_picked]

    st.sidebar.divider()
    st.sidebar.caption(
        "Sumber: WORLD Policy Analysis Center, Child Marriage Laws 2023 "
        "(193 negara anggota PBB). Lisensi CC-BY-SA."
    )
    return regions, incomes, severities


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
    if not detail:
        st.info(
            "🔍 Cari negara di kotak pencarian, atau klik salah satu negara "
            "di peta, untuk melihat detail hukum pernikahannya."
        )
        return
    st.markdown(f"### {detail['country']}  ·  `{detail['iso3']}`")
    st.markdown(
        f"**Region:** {detail['region']}  \n"
        f"**Pendapatan:** {detail['income'] or '—'}  \n"
        f"**Perlindungan:** {detail['perlindungan'] or '—'}"
    )
    st.markdown("---")
    st.markdown(
        f"**Usia minimum nikah (dengan loophole):**  \n"
        f"• Perempuan: {detail['minage_fem'] or '—'}  \n"
        f"• Laki-laki: {detail['minage_mal'] or '—'}"
    )
    flags = []
    if detail["has_loophole_fem"]:
        flags.append("⚠️ Ada celah hukum untuk perempuan")
    if detail["has_loophole_mal"]:
        flags.append("⚠️ Ada celah hukum untuk laki-laki")
    if detail["has_gender_gap"]:
        flags.append("⚠️ Ada kesenjangan usia antar gender")
    if flags:
        for f in flags:
            st.markdown(f)
    else:
        st.markdown("✅ Tidak ada celah hukum maupun kesenjangan gender.")


# ────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────
regions, incomes, severities = render_sidebar(df)
fdf = datalib.filter_data(df, regions, incomes, severities)

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
    "untuk membuka panel detail; scroll/drag untuk zoom & geser peta. "
    "Klik slice di pie chart untuk memfilter tingkat perlindungan."
)

country_names = sorted(df["country"].dropna().unique().tolist())
PLACEHOLDER = "— Pilih atau ketik nama negara —"
# Search/select negara (selectbox Streamlit otomatis searchable saat options >10).
picked_name = st.selectbox(
    "🔍 Cari negara untuk lihat detail",
    options=[PLACEHOLDER] + country_names,
    key=COUNTRY_KEY,
    index=0 if st.session_state.get(COUNTRY_KEY, PLACEHOLDER) == PLACEHOLDER else None,
    placeholder="Ketik untuk mencari…",
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
        render_country_detail(detail)

with donut_col:
    pie_event = st.plotly_chart(
        composition.render(df, severity_filter=severities),
        width="stretch", config=STATIC_CFG,
        on_select="rerun", selection_mode=["points"], key="pie",
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

# ── Handler event: pie click → schedule severities update untuk run berikutnya
pie_pts = (pie_event.get("selection", {}) or {}).get("points", []) if pie_event else []
if pie_pts:
    clicked_label = pie_pts[0].get("label")
    # Toggle: kalau slice sudah satu-satunya yang aktif, hapus filter; else SET.
    current = st.session_state.get(SEV_KEY, [])
    if clicked_label and clicked_label != T.LABEL_NO_DATA:
        if current == [clicked_label]:
            st.session_state["pending_pie_label"] = None
        else:
            st.session_state["pending_pie_label"] = clicked_label
        st.rerun()

# ── Handler event: peta click → schedule country picker update
map_pts = (map_event.get("selection", {}) or {}).get("points", []) if map_event else []
if map_pts:
    clicked_iso3 = map_pts[0].get("location")
    if clicked_iso3 and clicked_iso3 != focus_iso3:
        st.session_state["pending_map_iso3"] = clicked_iso3
        st.rerun()

st.divider()

# ── Section 1b: Tangga Perlindungan per Umur (P & L sandingkan per umur) ──
st.subheader("Tangga Perlindungan menurut Umur Anak")
st.caption(
    "Untuk anak umur 13, 15, dan 17 tahun — di berapa negara mereka secara hukum "
    "dilarang menikah, hanya boleh dgn pengadilan / kehamilan, boleh dgn izin orang "
    "tua, atau tanpa pembatasan sama sekali? Perempuan dan laki-laki disandingkan."
)
st.plotly_chart(
    protect_ladder.render(fdf),
    width="stretch", config=STATIC_CFG,
)

st.divider()

# ── Section 1c: Sankey Erosi Hukum (menggantikan heatmap) ──
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

# ── Section 2: Gender×Income | Loophole ──
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

# ── Section 3: Timeseries ──
st.subheader("Perkembangan Perlindungan Hukum, 1995–2023")
ts_col1, ts_col2 = st.columns([3, 1])
with ts_col2:
    year_range = st.slider(
        "Rentang tahun", min_value=1995, max_value=2023, value=(1995, 2023),
    )
with ts_col1:
    st.plotly_chart(
        timeseries.render(fdf, year_range=year_range),
        width="stretch", config=STATIC_CFG,
    )

st.divider()

# ── Footer: 2 tombol unduh + sumber ──
dl_col1, dl_col2, _ = st.columns([1.2, 1.2, 1])
with dl_col1:
    st.download_button(
        f"⬇️ Unduh data lengkap ({len(df)} negara)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="hukum-pernikahan-anak-2023-lengkap.csv",
        mime="text/csv",
        help="Dataset 193 negara hasil pembersihan, siap dipakai ulang.",
    )
with dl_col2:
    st.download_button(
        f"⬇️ Unduh data sesuai filter ({len(fdf)} negara)",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="hukum-pernikahan-anak-2023-terfilter.csv",
        mime="text/csv",
        help="Subset sesuai filter di sidebar.",
    )

st.divider()
st.caption(
    "Dataset: WORLD Policy Analysis Center, Child Marriage Laws 2023 · "
    "DOI: 10.25828/v8s6-jz31 · Lisensi CC-BY-SA. "
    "Dashboard: Kelompok 11 IF4061 Visualisasi Data, Institut Teknologi Bandung."
)
