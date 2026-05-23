"""Section 1 — Peta choropleth (HERO): tingkat perlindungan anak per negara.

Geometri ISO-3 bawaan Plotly + overlay bubble markers (scatter_geo) untuk
membuat negara kecil tetap terlihat. Highlight tegas untuk negara fokus (hasil
search atau klik). Auto-zoom ke region bila persis 1 region terpilih.

Revisi tim:
- Filter tidak menghapus negara dari peta — semua 193 tetap tampil; di-dim
  bila tidak masuk filter. Kategori "Di luar filter" TIDAK ditampilkan di
  legenda (visual noise).
- "Tanpa data" pakai abu medium kontras (#9A9A9A) yang dibedakan dari
  "di luar filter" (#E6E7E9 light).
- Bubble overlay supaya negara kecil (Singapore, Nauru, Tuvalu) terlihat.
- Negara fokus (search/klik) di-highlight ring tebal kontras.
- Auto-zoom ke region bila persis 1 region dipilih.
"""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go

import theme as T

DIMMED_COLOR = "#E6E7E9"
DIMMED_LABEL = "Di luar filter"
FOCUS_RING_COLOR = "#0F4C5C"   # deep teal selaras COLOR_HEADLINE


def render(
    full_df,
    selected_iso3=None,
    focus_iso3: str | None = None,
    zoom_region: str | None = None,
) -> go.Figure:
    """Render peta choropleth + bubble overlay + focus highlight.

    Parameters
    ----------
    full_df : DataFrame 193 negara.
    selected_iso3 : iterable iso3 hasil filter. Negara di luar set ini di-dim.
    focus_iso3 : 1 iso3 untuk highlight tegas (hasil search/klik).
    zoom_region : nama region. Bila set, peta auto-fit bounding box-nya.
    """
    d = full_df.copy()
    selected = set(selected_iso3) if selected_iso3 is not None else set(d["iso3"])
    is_selected = d["iso3"].isin(selected)

    # Label kategori per negara: di luar filter ATAU label tingkat perlindungan.
    short = d["loop_summ"].map(T.LOOP_SUMM_SHORT).fillna(T.LABEL_NO_DATA)
    d["perlindungan"] = short.where(is_selected, DIMMED_LABEL)
    d["loop_summ_label"] = d["loop_summ_label"].fillna(T.LABEL_NO_DATA)

    color_map = {T.LOOP_SUMM_SHORT[c]: T.LOOP_SUMM_COLORS[c] for c in T.LOOP_SUMM_ORDER}
    color_map[T.LABEL_NO_DATA] = T.NO_DATA_COLOR
    color_map[DIMMED_LABEL] = DIMMED_COLOR
    # Urutan legend (tidak termasuk DIMMED — sengaja hidden dari legend).
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
    # Border + hide "Di luar filter" dari legend.
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
    # tingkat perlindungan. Membuat negara kecil (Singapore, Nauru) tetap
    # visible meski poligon-nya hampir tak terlihat di world view.
    if "lon" in d.columns and "lat" in d.columns:
        bubble = d.dropna(subset=["lon", "lat"]).copy()
        bubble_colors = [
            DIMMED_COLOR if cat == DIMMED_LABEL
            else color_map.get(cat, T.NO_DATA_COLOR)
            for cat in bubble["perlindungan"]
        ]
        fig.add_trace(go.Scattergeo(
            lon=bubble["lon"], lat=bubble["lat"],
            mode="markers",
            marker=dict(
                size=6,
                color=bubble_colors,
                line=dict(width=0.5, color="#FFFFFF"),
                opacity=0.95,
            ),
            text=bubble["country"],
            customdata=bubble[["country", "loop_summ_label",
                               "minage_fem_loop_label", "minage_mal_loop_label",
                               "wb_econ_label"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Perlindungan: %{customdata[1]}<br>"
                "Usia min. perempuan: %{customdata[2]}<br>"
                "Usia min. laki-laki: %{customdata[3]}<br>"
                "Pendapatan: %{customdata[4]}"
                "<extra></extra>"
            ),
            showlegend=False,
            name="bubble",
        ))

    # ── Focus highlight: ring tegas di negara terpilih (search/klik). Render
    # paling akhir supaya berada di atas semua trace lain.
    # Defensive: skip kalau kolom lon/lat tidak ada (cache lama yg belum sync).
    if focus_iso3 and "lon" in d.columns and "lat" in d.columns:
        focus_row = d[d["iso3"] == focus_iso3]
        if not focus_row.empty and focus_row["lon"].notna().all():
            fig.add_trace(go.Scattergeo(
                lon=focus_row["lon"], lat=focus_row["lat"],
                mode="markers",
                marker=dict(
                    size=22,
                    color="rgba(0,0,0,0)",
                    line=dict(width=3, color=FOCUS_RING_COLOR),
                ),
                hoverinfo="skip",
                showlegend=False,
                name="focus",
            ))

    # ── Geo configuration: projection + zoom bounds ──
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
        # World view dengan batas wajar (tidak bisa zoom-out sampai titik).
        geo_kwargs.update(
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-58, 85]),
        )
    fig.update_geos(**geo_kwargs)

    fig.update_layout(
        **T.PLOTLY_LAYOUT,
        height=520,
        legend=dict(
            title="Tingkat perlindungan",
            orientation="h", yanchor="bottom", y=-0.12,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        clickmode="event+select",
    )
    return fig
