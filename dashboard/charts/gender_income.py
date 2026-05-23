"""Section 2a — Gender × Pendapatan.

Grouped bar: persentase negara dengan usia minimum pernikahan ≥ 18 tahun
(kode 5 pada minage_*_any), dipecah per income group dan per gender. Bila bar
Perempuan lebih rendah dari Laki-laki → ada kesenjangan gender; perbandingan
antar income group menunjukkan gradien pendapatan.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

import theme as T


def _pct_protected(sub: pd.DataFrame, col: str) -> float | None:
    valid = sub[col].notna().sum()
    if not valid:
        return None
    return (sub[col] == 5).sum() / valid * 100


def render(fdf) -> go.Figure:
    incomes = [g for g in T.INCOME_ORDER if g in fdf["wb_econ_label"].unique()]
    fem_vals, mal_vals, fem_n, mal_n = [], [], [], []
    for g in incomes:
        sub = fdf[fdf["wb_econ_label"] == g]
        fem_vals.append(_pct_protected(sub, "minage_fem_any"))
        mal_vals.append(_pct_protected(sub, "minage_mal_any"))
        fem_n.append(int(sub["minage_fem_any"].notna().sum()))
        mal_n.append(int(sub["minage_mal_any"].notna().sum()))

    fig = go.Figure()
    fig.add_bar(
        x=incomes, y=fem_vals, name="Perempuan",
        marker_color=T.COLOR_FEMALE, customdata=fem_n,
        hovertemplate="<b>%{x}</b><br>Perempuan ≥18: %{y:.0f}%<br>(%{customdata} negara)<extra></extra>",
    )
    fig.add_bar(
        x=incomes, y=mal_vals, name="Laki-laki",
        marker_color=T.COLOR_MALE, customdata=mal_n,
        hovertemplate="<b>%{x}</b><br>Laki-laki ≥18: %{y:.0f}%<br>(%{customdata} negara)<extra></extra>",
    )
    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        barmode="group",
        height=340,
        yaxis=dict(title="% negara usia min. ≥ 18 thn", range=[0, 105],
                   ticksuffix="%", gridcolor=T.COLOR_GRIDLINE),
        xaxis=dict(title=None),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return T.lock_static(fig)
