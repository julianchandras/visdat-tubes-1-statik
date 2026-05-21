"""Section 4a — Komposisi tingkat perlindungan (donut).

Donut distribusi loop_summ untuk subset terfilter. Menambah ragam jenis grafik
(pie/donut) sesuai spesifikasi tugas.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T


def render(fdf) -> go.Figure:
    labels, values, colors = [], [], []
    for code in T.LOOP_SUMM_ORDER:
        n = int((fdf["loop_summ"] == code).sum())
        if n:
            labels.append(T.LOOP_SUMM_LABELS[code])
            values.append(n)
            colors.append(T.LOOP_SUMM_COLORS[code])
    n_nodata = int(fdf["loop_summ"].isna().sum())
    if n_nodata:
        labels.append("Tanpa data")
        values.append(n_nodata)
        colors.append(T.NO_DATA_COLOR)

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="white", width=1.5)),
        sort=False, direction="clockwise",
        textinfo="value", textfont=dict(size=13),
        hovertemplate="<b>%{label}</b><br>%{value} negara (%{percent})<extra></extra>",
    ))
    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        height=360,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, x=1.0, font=dict(size=10)),
    )
    return fig
