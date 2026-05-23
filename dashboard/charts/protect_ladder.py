"""Section A — Tangga Perlindungan per Umur (protect_girl_* / protect_boy_*).

Small multiples 3 panel side-by-side (umur 13 / 15 / 17) menunjukkan distribusi
4 tingkat perlindungan saat anak umur tersebut: tanpa pembatasan, izin ortu /
adat, court approval / kehamilan, atau dilarang secara hukum.

Pakai kolom protect_girl_13/15/17 (atau protect_boy_*) yang sebelumnya tidak
disentuh dashboard. Pertanyaan yang dijawab: "untuk anak umur X, di berapa
negara hukum benar-benar melindungi mereka?"

Teknik viz baru: stacked horizontal bar + small multiples comparison.
"""
from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import theme as T


AGES = (13, 15, 17)


def render(fdf, gender: str = "girl") -> go.Figure:
    """Render 3 panel small multiples stacked horizontal bar.

    Parameters
    ----------
    fdf : DataFrame negara terfilter (basis hitungan).
    gender : "girl" atau "boy" → memilih kolom protect_girl_* atau protect_boy_*.
    """
    prefix = "protect_girl" if gender == "girl" else "protect_boy"

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[f"Umur {a} tahun" for a in AGES],
        horizontal_spacing=0.06,
        shared_yaxes=True,
    )

    # Untuk legend: hanya tampil 1x (di trace pertama tiap kategori).
    legend_shown: set[float] = set()

    for col_i, age in enumerate(AGES, start=1):
        column = f"{prefix}_{age}"
        # Hitung jumlah negara per kategori (urutan = paling protektif → paling parah)
        for code in T.PROTECT_ORDER:
            n = int((fdf[column] == code).sum())
            show = code not in legend_shown
            legend_shown.add(code)
            fig.add_trace(
                go.Bar(
                    y=["Distribusi"],
                    x=[n],
                    orientation="h",
                    name=T.PROTECT_LABELS[code],
                    marker_color=T.PROTECT_COLORS[code],
                    legendgroup=f"prot_{code}",
                    showlegend=show,
                    text=str(n) if n > 0 else "",
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white", size=12),
                    hovertemplate=(
                        f"<b>Umur {age} thn</b><br>"
                        f"{T.PROTECT_LABELS[code]}: %{{x}} negara<extra></extra>"
                    ),
                ),
                row=1, col=col_i,
            )

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=240,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.45,
            xanchor="center", x=0.5, font=dict(size=10),
            traceorder="normal",
        ),
        bargap=0.5,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)
    return fig
