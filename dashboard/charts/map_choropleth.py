"""Section 1 — Peta choropleth (HERO): tingkat perlindungan anak per negara.

Pakai geometri ISO-3 bawaan Plotly (tanpa geopandas/shapefile). Warna kategorikal
loop_summ selaras palet poster Tubes 1.

Revisi tim:
- Filter tidak menghapus negara dari peta. Semua 193 negara tetap tampil;
  yang tidak terfilter diabaikan ke abu-abu muda + border tipis, yang terfilter
  pakai warna asli + border lebih tegas. Konteks geografis dipertahankan.
- Zoom dibatasi (projection scale 0.7 - 6) supaya user tidak bisa zoom-out
  sampai peta jadi titik, atau zoom-in tak terbatas.
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

import theme as T

# Warna negara yang tidak terfilter (in-context tapi diabaikan).
DIMMED_COLOR = "#E6E7E9"
DIMMED_LABEL = "Di luar filter"


def render(full_df, selected_iso3=None) -> go.Figure:
    """Render peta choropleth.

    Parameters
    ----------
    full_df : DataFrame 193 negara (selalu basis peta, supaya konteks utuh).
    selected_iso3 : iterable iso3 hasil filter. Negara di luar set ini di-abu-abukan.
        Bila None / sama dengan semua negara → tidak ada yang di-dim (semua highlight).
    """
    d = full_df.copy()
    selected = set(selected_iso3) if selected_iso3 is not None else set(d["iso3"])
    is_selected = d["iso3"].isin(selected)

    # Kolom kategori untuk pewarnaan: jika di luar filter → "Di luar filter",
    # selain itu pakai label ringkas loop_summ (NaN → "Tanpa data").
    short = d["loop_summ"].map(T.LOOP_SUMM_SHORT).fillna(T.LABEL_NO_DATA)
    d["perlindungan"] = short.where(is_selected, DIMMED_LABEL)
    d["loop_summ_label"] = d["loop_summ_label"].fillna(T.LABEL_NO_DATA)

    color_map = {T.LOOP_SUMM_SHORT[c]: T.LOOP_SUMM_COLORS[c] for c in T.LOOP_SUMM_ORDER}
    color_map[T.LABEL_NO_DATA] = T.NO_DATA_COLOR
    color_map[DIMMED_LABEL] = DIMMED_COLOR
    order = [T.LOOP_SUMM_SHORT[c] for c in T.LOOP_SUMM_ORDER] + [T.LABEL_NO_DATA]
    # Hanya tampilkan kategori "Di luar filter" di legend kalau memang ada.
    if (~is_selected).any():
        order.append(DIMMED_LABEL)

    fig = px.choropleth(
        d,
        locations="iso3",
        locationmode="ISO-3",
        color="perlindungan",
        color_discrete_map=color_map,
        category_orders={"perlindungan": order},
        custom_data=["country", "loop_summ_label", "minage_fem_loop_label",
                     "minage_mal_loop_label", "wb_econ_label"],
    )
    # Border lebih tegas untuk negara terfilter, lebih tipis untuk yang di-dim.
    for trace in fig.data:
        if trace.name == DIMMED_LABEL:
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 0.3
        else:
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 0.7
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Perlindungan: %{customdata[1]}<br>"
            "Usia min. perempuan: %{customdata[2]}<br>"
            "Usia min. laki-laki: %{customdata[3]}<br>"
            "Pendapatan: %{customdata[4]}"
            "<extra>Klik untuk detail</extra>"
        ),
    )
    fig.update_geos(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=False,
        bgcolor="rgba(0,0,0,0)",
        landcolor="#ECEDEF",
        # Batas pan/zoom — fitToBounds di world supaya tidak melayang ke kosong.
        lonaxis=dict(range=[-180, 180]),
        lataxis=dict(range=[-58, 85]),
    )
    fig.update_layout(
        **T.PLOTLY_LAYOUT,
        height=460,
        legend=dict(
            title="Tingkat perlindungan",
            orientation="h", yanchor="bottom", y=-0.18,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        clickmode="event+select",
    )
    return fig
