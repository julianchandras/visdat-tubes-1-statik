"""Section 1 — Peta choropleth (HERO): tingkat perlindungan anak per negara.

Geometri ISO-3 bawaan Plotly + overlay bubble markers (scatter_geo) untuk
membuat negara kecil tetap terlihat & jadi sasaran klik yang reliable.

Revisi tim:
- Filter tidak menghapus negara dari peta — semua 193 tetap tampil; di-dim
  bila tidak masuk filter.
- Saat user fokus 1 negara (search/klik): SEMUA negara lain di-dim ke abu
  light; hanya negara fokus tetap berwarna. Tidak ada ring overlay —
  contrast dim cukup punchy.
- "Tanpa data" abu medium (#9A9A9A); "Di luar filter" abu light (#E6E7E9,
  tidak masuk legenda).
- Bubble overlay supaya negara kecil (Singapore, Nauru) terlihat & klik
  bisa mengenai polygon-pun-bubble.
- Auto-zoom ke region bila persis 1 region dipilih.
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

import theme as T

DIMMED_COLOR = "#E6E7E9"
DIMMED_LABEL = "Di luar filter"


def render(
    full_df,
    selected_iso3=None,
    focus_iso3: str | None = None,
    zoom_region: str | None = None,
) -> go.Figure:
    """Render peta choropleth + bubble overlay.

    Parameters
    ----------
    full_df : DataFrame 193 negara.
    selected_iso3 : iterable iso3 hasil filter sidebar. Negara di luar set
        ini di-dim. **DIABAIKAN** saat focus_iso3 set — saat fokus, hanya
        negara fokus yg di-highlight; sisanya semua di-dim.
    focus_iso3 : 1 iso3 dari search/klik. Saat set, override mode dim:
        hanya 1 negara berwarna.
    zoom_region : nama region; auto-fit bbox saat persis 1 region terpilih.
    """
    d = full_df.copy()

    # Mode dim: kalau focus aktif, hanya focus yg "selected" (semua lain dim).
    # Else: ikuti selected_iso3 (filter sidebar).
    if focus_iso3:
        selected = {focus_iso3}
    elif selected_iso3 is not None:
        selected = set(selected_iso3)
    else:
        selected = set(d["iso3"])
    is_selected = d["iso3"].isin(selected)

    short = d["loop_summ"].map(T.LOOP_SUMM_SHORT).fillna(T.LABEL_NO_DATA)
    d["perlindungan"] = short.where(is_selected, DIMMED_LABEL)
    d["loop_summ_label"] = d["loop_summ_label"].fillna(T.LABEL_NO_DATA)

    color_map = {T.LOOP_SUMM_SHORT[c]: T.LOOP_SUMM_COLORS[c] for c in T.LOOP_SUMM_ORDER}
    color_map[T.LABEL_NO_DATA] = T.NO_DATA_COLOR
    color_map[DIMMED_LABEL] = DIMMED_COLOR
    order = [T.LOOP_SUMM_SHORT[c] for c in T.LOOP_SUMM_ORDER] + [T.LABEL_NO_DATA]
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
    for trace in fig.data:
        if trace.name == DIMMED_LABEL:
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 0.3
            trace.showlegend = False
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

    # ── Bubble overlay: dot kecil di centroid setiap negara, warna sesuai
    # kategori. Membuat negara kecil terlihat + bubble klikabel (handler
    # app.py membaca customdata[0] = country name untuk lookup iso3).
    if "lon" in d.columns and "lat" in d.columns:
        bubble = d.dropna(subset=["lon", "lat"]).copy()
        bubble_colors = [
            DIMMED_COLOR if cat == DIMMED_LABEL
            else color_map.get(cat, T.NO_DATA_COLOR)
            for cat in bubble["perlindungan"]
        ]
        # Negara fokus dot lebih besar supaya menonjol; sisanya size standar.
        if focus_iso3:
            sizes = [10 if i == focus_iso3 else 5 for i in bubble["iso3"]]
        else:
            sizes = 6
        fig.add_trace(go.Scattergeo(
            lon=bubble["lon"], lat=bubble["lat"],
            mode="markers",
            marker=dict(
                size=sizes,
                color=bubble_colors,
                line=dict(width=0.6, color="#FFFFFF"),
                opacity=0.95,
            ),
            customdata=bubble[["country", "loop_summ_label",
                               "minage_fem_loop_label", "minage_mal_loop_label",
                               "wb_econ_label", "iso3"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Perlindungan: %{customdata[1]}<br>"
                "Usia min. perempuan: %{customdata[2]}<br>"
                "Usia min. laki-laki: %{customdata[3]}<br>"
                "Pendapatan: %{customdata[4]}"
                "<extra>Klik untuk detail</extra>"
            ),
            showlegend=False,
            name="bubble",
        ))

    # ── Geo config ──
    geo_kwargs = dict(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=False,
        bgcolor="rgba(0,0,0,0)",
        landcolor="#ECEDEF",
    )
    if zoom_region and zoom_region in T.REGION_BBOX:
        lon_min, lon_max, lat_min, lat_max = T.REGION_BBOX[zoom_region]
        geo_kwargs.update(
            lonaxis=dict(range=[lon_min, lon_max]),
            lataxis=dict(range=[lat_min, lat_max]),
        )
    else:
        geo_kwargs.update(
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-58, 85]),
        )
    fig.update_geos(**geo_kwargs)

    fig.update_layout(
        **T.PLOTLY_LAYOUT,
        height=520,
        showlegend=False,   # legenda di-share via HTML di app.py
        clickmode="event+select",
    )
    return fig
