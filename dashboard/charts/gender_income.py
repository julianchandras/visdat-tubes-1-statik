"""Section 2a — Kesenjangan Gender menurut Pendapatan.

Grouped bar: persentase negara dgn usia minimum pernikahan ≥ 18 tahun
(kode 5 pada minage_*_any), dipecah per income group dan per gender.

Klarifikasi (revisi tim): persentase dihitung TERHADAP JUMLAH NEGARA DENGAN
DATA NON-NULL untuk gender tsb. Jadi denominator P dan L bisa sedikit
berbeda (krn data missing antar gender bisa berbeda). Hover sekarang
menampilkan: "X negara (Y% dari Z negara dengan data)" supaya jelas.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

import theme as T


def _pct_and_count(sub: pd.DataFrame, col: str) -> tuple[float | None, int, int]:
    """Return (pct ≥18, numerator, denominator)."""
    n_valid = int(sub[col].notna().sum())
    if not n_valid:
        return None, 0, 0
    n_protected = int((sub[col] == 5).sum())
    return n_protected / n_valid * 100, n_protected, n_valid


def render(fdf) -> go.Figure:
    incomes = [g for g in T.INCOME_ORDER if g in fdf["wb_econ_label"].unique()]
    # Display label Indonesia di x-axis (sumbu); value asli tetap untuk lookup.
    incomes_display = [T.income_id(g) for g in incomes]
    fem_vals, mal_vals = [], []
    fem_num, fem_den, mal_num, mal_den = [], [], [], []
    for g in incomes:
        sub = fdf[fdf["wb_econ_label"] == g]
        fp, fn, fd = _pct_and_count(sub, "minage_fem_any")
        mp, mn, md = _pct_and_count(sub, "minage_mal_any")
        fem_vals.append(fp); fem_num.append(fn); fem_den.append(fd)
        mal_vals.append(mp); mal_num.append(mn); mal_den.append(md)

    fig = go.Figure()
    # customdata = [num, den] per bar → hover tampilkan kedua angka.
    fig.add_bar(
        x=incomes_display, y=fem_vals, name="Perempuan",
        marker_color=T.COLOR_FEMALE,
        customdata=list(zip(fem_num, fem_den)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Perempuan: %{y:.0f}% (%{customdata[0]} dari %{customdata[1]} negara)"
            "<extra></extra>"
        ),
    )
    fig.add_bar(
        x=incomes_display, y=mal_vals, name="Laki-laki",
        marker_color=T.COLOR_MALE,
        customdata=list(zip(mal_num, mal_den)),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Laki-laki: %{y:.0f}% (%{customdata[0]} dari %{customdata[1]} negara)"
            "<extra></extra>"
        ),
    )
    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k not in ("colorway", "margin")}
    fig.update_layout(
        **layout,
        barmode="group",
        height=340,
        yaxis=dict(title="% negara usia min. ≥ 18 thn", range=[0, 105],
                   ticksuffix="%", gridcolor=T.COLOR_GRIDLINE),
        xaxis=dict(title=None),
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=30),
    )
    return T.lock_static(fig)
