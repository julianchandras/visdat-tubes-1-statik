"""Section 3 — Perkembangan perlindungan hukum 1995–2023.

Line chart: % negara dengan usia minimum pernikahan ≥ 18 (dengan izin orang tua),
Perempuan vs Laki-laki. Area di antara dua garis = kesenjangan gender. Mendukung
filter range tahun + opsi per-region.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T
import data as datalib


def render(fdf, year_range=(1995, 2023), region=None) -> go.Figure:
    ts = datalib.region_timeseries(fdf, region=region)

    fig = go.Figure()
    # Area kesenjangan (antara M dan F)
    fig.add_trace(go.Scatter(
        x=ts["year"], y=ts["Laki-laki"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=ts["year"], y=ts["Perempuan"], mode="lines",
        line=dict(width=0), fill="tonexty",
        fillcolor="rgba(199,30,58,0.12)", showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=ts["year"], y=ts["Laki-laki"], mode="lines",
        name="Laki-laki", line=dict(color=T.COLOR_MALE, width=2.2),
        hovertemplate="%{x}<br>Laki-laki: %{y:.0f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=ts["year"], y=ts["Perempuan"], mode="lines",
        name="Perempuan", line=dict(color=T.COLOR_FEMALE, width=2.2),
        hovertemplate="%{x}<br>Perempuan: %{y:.0f}%<extra></extra>",
    ))

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k not in ("colorway", "margin")}
    fig.update_layout(
        **layout,
        height=380,
        xaxis=dict(title=None, range=[year_range[0], year_range[1]],
                   gridcolor=T.COLOR_GRIDLINE),
        yaxis=dict(title="% negara usia min. ≥ 18 thn", range=[0, 105],
                   ticksuffix="%", gridcolor=T.COLOR_GRIDLINE),
        legend=dict(orientation="h", yref="container", y=1.0, yanchor="top",
                    xanchor="center", x=0.5, font=dict(size=13)),
        margin=dict(l=10, r=10, t=80, b=10),
        hovermode="x unified",
    )
    return T.lock_static(fig)
