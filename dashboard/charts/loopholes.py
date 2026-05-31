"""Section 2b — Celah hukum (loophole) pernikahan anak.

Horizontal stacked bar: jumlah negara yang menyisakan 3 tipe celah hukum,
dipecah per income group. Editorial hook: bahkan negara high-income masih
menyisakan celah "izin orang tua".
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T

CATEGORIES = [
    ("Izin Orang Tua", "except_pc", [2, 3]),
    ("Hukum Adat/Agama", "except_crlaw", [2]),
    ("Kehamilan", "except_preg", [2]),
]


def render(fdf) -> go.Figure:
    cats = [c[0] for c in CATEGORIES]
    incomes = [g for g in T.INCOME_ORDER if g in fdf["wb_econ_label"].unique()]

    fig = go.Figure()
    for g in incomes:
        sub = fdf[fdf["wb_econ_label"] == g]
        counts = [int(sub[col].isin(codes).sum()) for _, col, codes in CATEGORIES]
        g_display = T.income_id(g)   # display label Indonesia
        fig.add_bar(
            y=cats, x=counts, name=g_display, orientation="h",
            marker_color=T.INCOME_COLORS[g],
            hovertemplate="<b>%{y}</b><br>" + g_display + ": %{x} negara<extra></extra>",
        )

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k not in ("colorway", "margin")}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=340,
        xaxis=dict(title="Jumlah negara", gridcolor=T.COLOR_GRIDLINE),
        yaxis=dict(title=None, autorange="reversed"),
        # Legend di bawah chart (revisi tim — label "Berpendapatan ..." panjang,
        # di atas y=1.02 ter-truncate krn half-width).
        legend=dict(orientation="h", yanchor="top", y=-0.18,
                    xanchor="center", x=0.5, font=dict(size=11)),
        margin=dict(l=10, r=10, t=20, b=70),
    )
    return T.lock_static(fig)
