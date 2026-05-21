"""Section 1 — Peta choropleth (HERO): tingkat perlindungan anak per negara.

Pakai geometri ISO-3 bawaan Plotly (tanpa geopandas/shapefile). Warna kategorikal
loop_summ selaras palet poster Tubes 1.
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

import theme as T


def render(fdf) -> go.Figure:
    d = fdf.copy()
    # loop_summ NaN → label "Tanpa data" supaya tetap tampil abu-abu.
    d["loop_summ_label"] = d["loop_summ_label"].fillna("Tanpa data")

    color_map = {T.LOOP_SUMM_LABELS[c]: T.LOOP_SUMM_COLORS[c] for c in T.LOOP_SUMM_ORDER}
    color_map["Tanpa data"] = T.NO_DATA_COLOR
    order = [T.LOOP_SUMM_LABELS[c] for c in T.LOOP_SUMM_ORDER] + ["Tanpa data"]

    fig = px.choropleth(
        d,
        locations="iso3",
        locationmode="ISO-3",
        color="loop_summ_label",
        color_discrete_map=color_map,
        category_orders={"loop_summ_label": order},
        custom_data=["country", "loop_summ_label", "minage_fem_loop_label",
                     "minage_mal_loop_label", "wb_econ_label"],
    )
    fig.update_traces(
        marker_line_color="white",
        marker_line_width=0.4,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Perlindungan: %{customdata[1]}<br>"
            "Usia min. perempuan: %{customdata[2]}<br>"
            "Usia min. laki-laki: %{customdata[3]}<br>"
            "Pendapatan: %{customdata[4]}<extra></extra>"
        ),
    )
    fig.update_geos(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=False,
        bgcolor="rgba(0,0,0,0)",
        landcolor="#ECEDEF",
    )
    fig.update_layout(
        **T.PLOTLY_LAYOUT,
        height=460,
        legend=dict(
            title="Tingkat perlindungan",
            orientation="h", yanchor="bottom", y=-0.18,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
    )
    return fig
