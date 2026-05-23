"""Section 1 — Peta choropleth (HERO): tingkat perlindungan anak per negara.

Geometri ISO-3 bawaan Plotly + overlay bubble markers (scatter_geo) untuk
membuat negara kecil tetap terlihat & jadi sasaran klik yang reliable.

Mode dim (revisi tim):
- **Focus mode** (user pilih 1 negara via search/klik): negara non-focus
  diburamkan dgn WARNA ASLI loop_summ + opacity rendah (tetap dapat konteks
  perlindungan tetangga).
- **Filter mode** (sidebar filter aktif, tanpa focus): negara non-filter
  GRAY POLOS — user eksplisit exclude dari analisis, warna dihilangkan.
- **None**: semua negara warna asli.

Tambah:
- "Tanpa data" abu medium (#9A9A9A); selalu di legenda.
- Bubble overlay supaya negara kecil terlihat & klik reliable.
- Auto-zoom ke region dari negara fokus (bukan bbox negara individu).
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

import theme as T

DIMMED_COLOR = "#E6E7E9"
DIMMED_LABEL = "Di luar filter"
DIM_SUFFIX = " (dim)"   # marker kategori dim-variant untuk mode focus


def _build_color_map_and_categories(focus_iso3, has_filter):
    """Bangun color_map + category order sesuai mode aktif."""
    color_map = {T.LOOP_SUMM_SHORT[c]: T.LOOP_SUMM_COLORS[c] for c in T.LOOP_SUMM_ORDER}
    color_map[T.LABEL_NO_DATA] = T.NO_DATA_COLOR
    base_order = [T.LOOP_SUMM_SHORT[c] for c in T.LOOP_SUMM_ORDER] + [T.LABEL_NO_DATA]
    if focus_iso3:
        # Tambah dim variants (warna asli + alpha rendah)
        for c in T.LOOP_SUMM_ORDER:
            color_map[T.LOOP_SUMM_SHORT[c] + DIM_SUFFIX] = T.LOOP_SUMM_COLORS_DIM[c]
        color_map[T.LABEL_NO_DATA + DIM_SUFFIX] = T.NO_DATA_COLOR_DIM
    if has_filter and not focus_iso3:
        color_map[DIMMED_LABEL] = DIMMED_COLOR
    return color_map, base_order


def render(
    full_df,
    selected_iso3=None,
    focus_iso3: str | None = None,
    zoom_region: str | None = None,
) -> go.Figure:
    """Render peta choropleth + bubble overlay."""
    d = full_df.copy()
    short_base = d["loop_summ"].map(T.LOOP_SUMM_SHORT).fillna(T.LABEL_NO_DATA)
    d["loop_summ_label"] = d["loop_summ_label"].fillna(T.LABEL_NO_DATA)

    # ── Tentukan kategori 'perlindungan' per negara sesuai mode aktif ──
    if focus_iso3:
        # MODE FOCUS: non-focus → variant DIM (warna asli buram)
        is_focus = d["iso3"] == focus_iso3
        d["perlindungan"] = short_base.where(is_focus, short_base + DIM_SUFFIX)
        has_filter_view = False
    elif selected_iso3 is not None and len(selected_iso3) < len(d):
        # MODE FILTER: non-filter → DIMMED_LABEL (gray polos)
        selected = set(selected_iso3)
        is_selected = d["iso3"].isin(selected)
        d["perlindungan"] = short_base.where(is_selected, DIMMED_LABEL)
        has_filter_view = True
    else:
        # NO DIM: semua warna asli
        d["perlindungan"] = short_base
        has_filter_view = False

    color_map, base_order = _build_color_map_and_categories(focus_iso3, has_filter_view)
    order = list(base_order)
    if has_filter_view:
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
    # Border + sembunyikan trace dim/filter-dim dari legend (clutter).
    for trace in fig.data:
        name = trace.name or ""
        is_dim_variant = DIM_SUFFIX in name
        is_filter_dim = name == DIMMED_LABEL
        if is_dim_variant or is_filter_dim:
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

    # ── Bubble overlay ──
    if "lon" in d.columns and "lat" in d.columns:
        bubble = d.dropna(subset=["lon", "lat"]).copy()
        # Bubble dim mengikuti mode peta: rgba dim untuk focus mode,
        # DIMMED_COLOR gray untuk filter mode.
        def _bubble_color(row):
            cat = row["perlindungan"]
            if cat == DIMMED_LABEL:
                return DIMMED_COLOR
            return color_map.get(cat, T.NO_DATA_COLOR)
        bubble_colors = bubble.apply(_bubble_color, axis=1).tolist()
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

    # ── Geo config — focus → region; else zoom_region; else world ──
    geo_kwargs = dict(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=False,
        bgcolor="rgba(0,0,0,0)",
        landcolor="#ECEDEF",
    )
    zoom_set = False
    if focus_iso3:
        focus_row = d[d["iso3"] == focus_iso3]
        if not focus_row.empty:
            focus_region = focus_row.iloc[0].get("region")
            if focus_region in T.REGION_BBOX:
                lon_min, lon_max, lat_min, lat_max = T.REGION_BBOX[focus_region]
                geo_kwargs.update(
                    lonaxis=dict(range=[lon_min, lon_max]),
                    lataxis=dict(range=[lat_min, lat_max]),
                )
                zoom_set = True
    if not zoom_set and zoom_region and zoom_region in T.REGION_BBOX:
        lon_min, lon_max, lat_min, lat_max = T.REGION_BBOX[zoom_region]
        geo_kwargs.update(
            lonaxis=dict(range=[lon_min, lon_max]),
            lataxis=dict(range=[lat_min, lat_max]),
        )
        zoom_set = True
    if not zoom_set:
        geo_kwargs.update(
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-58, 85]),
        )
    fig.update_geos(**geo_kwargs)

    fig.update_layout(
        **T.PLOTLY_LAYOUT,
        height=520,
        showlegend=False,   # legenda di-share lewat HTML legend di app.py
        clickmode="event+select",
    )
    return fig
