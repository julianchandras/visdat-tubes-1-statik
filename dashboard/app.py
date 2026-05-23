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
# Sidebar — filter global
# ────────────────────────────────────────────────────────────
def render_sidebar(df):
    st.sidebar.header("Filter")

    regions = st.sidebar.multiselect(
        "Region", options=T.REGION_ORDER, default=[],
        help="Kosong = semua region.",
    )
    incomes = st.sidebar.multiselect(
        "Tingkat pendapatan", options=T.INCOME_ORDER, default=[],
        help="Klasifikasi World Bank.",
    )
    sev_labels = {T.LOOP_SUMM_LABELS[c]: c for c in T.LOOP_SUMM_ORDER}
    sev_picked = st.sidebar.multiselect(
        "Tingkat perlindungan", options=list(sev_labels.keys()), default=[],
        help="Ringkasan loophole (loop_summ).",
    )
    severities = [sev_labels[s] for s in sev_picked]

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
    n = len(fdf)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Negara terpilih", n)
    c2.metric("Mengizinkan nikah < 18 thn", k["under18"])
    c3.metric("Punya celah hukum", k["loophole"])
    c4.metric("Ada path nikah ≤ 13 thn", k["worst"])


# ────────────────────────────────────────────────────────────
# Panel detail negara (klik peta + selectbox fallback)
# ────────────────────────────────────────────────────────────
def render_country_detail(detail: dict | None) -> None:
    if not detail:
        st.info("Klik salah satu negara di peta, atau pilih dari dropdown di atas, "
                "untuk melihat detail hukum pernikahannya.")
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

# Config Plotly:
# - Peta: zoom & pan diaktifkan (tapi dibatasi via geo bounds di chart-nya)
# - Non-peta: mode bar off, scrollZoom off — diagram lain tak perlu di-zoom.
MAP_CFG = {"displayModeBar": True, "scrollZoom": True,
           "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"]}
STATIC_CFG = {"displayModeBar": False, "scrollZoom": False, "staticPlot": False}

# ── Section 1+4a: Peta (hero) + Donut komposisi side-by-side ──
st.subheader("Peta Perlindungan Anak dari Pernikahan Dini")
st.caption("Arahkan kursor untuk detail; klik negara untuk panel detail; "
           "scroll/drag untuk zoom & geser peta.")

map_col, donut_col = st.columns([2, 1])
with map_col:
    map_event = st.plotly_chart(
        map_choropleth.render(df, selected_iso3=fdf["iso3"].tolist()),
        width="stretch", config=MAP_CFG,
        on_select="rerun", selection_mode=["points"], key="map",
    )
with donut_col:
    st.markdown("**Komposisi (negara terfilter)**")
    st.plotly_chart(composition.render(fdf), width="stretch", config=STATIC_CFG)

# Panel detail negara — di bawah peta, full-width
st.markdown("#### Detail Negara")
sel_col, info_col = st.columns([1, 3])
with sel_col:
    country_names = sorted(df["country"].dropna().unique().tolist())
    # Tentukan default: kalau ada klik peta, pakai iso3 klik; else None.
    clicked_iso3 = None
    try:
        pts = (map_event.get("selection", {}) or {}).get("points", [])
        if pts:
            clicked_iso3 = pts[0].get("location")
    except (AttributeError, TypeError):
        pass
    default_name = None
    if clicked_iso3:
        match = df[df["iso3"] == clicked_iso3]
        if not match.empty:
            default_name = match.iloc[0]["country"]
    picked_name = st.selectbox(
        "Lihat detail negara",
        options=["(Pilih atau klik peta)"] + country_names,
        index=(country_names.index(default_name) + 1) if default_name else 0,
        key="country_picker",
    )
with info_col:
    detail = None
    if picked_name and picked_name != "(Pilih atau klik peta)":
        iso3 = df.loc[df["country"] == picked_name, "iso3"].iloc[0]
        detail = datalib.country_detail(df, iso3)
    elif clicked_iso3:
        detail = datalib.country_detail(df, clicked_iso3)
    render_country_detail(detail)

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
    region_opt = st.selectbox(
        "Region", options=["Semua region"] + T.REGION_ORDER, index=0,
    )
    year_range = st.slider(
        "Rentang tahun", min_value=1995, max_value=2023, value=(1995, 2023),
    )
region_arg = None if region_opt == "Semua region" else region_opt
with ts_col1:
    st.plotly_chart(
        timeseries.render(fdf, year_range=year_range, region=region_arg),
        width="stretch", config=STATIC_CFG,
    )

st.divider()

# ── Section 4b: Tabel data ──
st.subheader("Data Negara Terpilih")
table_cols = ["country", "region", "wb_econ_label", "loop_summ_label",
              "minage_fem_loop_label", "minage_mal_loop_label"]
show = fdf[table_cols].rename(columns={
    "country": "Negara", "region": "Region", "wb_econ_label": "Pendapatan",
    "loop_summ_label": "Perlindungan",
    "minage_fem_loop_label": "Usia min. P", "minage_mal_loop_label": "Usia min. L",
})
st.dataframe(show, width="stretch", height=320, hide_index=True)
st.download_button(
    "⬇️ Unduh data terpilih (CSV)",
    data=fdf.to_csv(index=False).encode("utf-8"),
    file_name="hukum-pernikahan-anak-terpilih.csv",
    mime="text/csv",
)

# ── Footer ──
st.divider()
st.caption(
    "Dataset: WORLD Policy Analysis Center, Child Marriage Laws 2023 · "
    "DOI: 10.25828/v8s6-jz31 · Lisensi CC-BY-SA. "
    "Dashboard: Kelompok 11 IF4061 Visualisasi Data, Institut Teknologi Bandung."
)
