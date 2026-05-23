"""Section A — Tangga Perlindungan per Umur.

Small multiples 3 panel side-by-side (umur 13 / 15 / 17). Per panel: DUA
bar horizontal sandingkan — Perempuan & Laki-laki — supaya kesenjangan
gender per umur langsung terlihat. Setiap bar = 1 negara segmen warna
sesuai 4 kategori protect_*.

Pakai kolom protect_girl_13/15/17 + protect_boy_13/15/17 (sebelumnya tidak
disentuh dashboard). Teknik viz: small multiples + paired horizontal
stacked bars.
"""
from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import theme as T


AGES = (13, 15, 17)
GENDERS = (("girl", "Perempuan"), ("boy", "Laki-laki"))


def render(fdf) -> go.Figure:
    """Render 3 panel small multiples, masing-masing 2 horizontal stacked bars
    sandingkan Perempuan dan Laki-laki.

    Defensive: kolom hilang → figure pesan informatif (bukan crash).
    """
    needed = [f"protect_{g}_{a}" for g, _ in GENDERS for a in AGES]
    missing = [c for c in needed if c not in fdf.columns]
    if missing:
        fig = go.Figure()
        fig.add_annotation(
            text=(
                "Data belum lengkap (kolom " + ", ".join(missing[:3]) +
                "… hilang).<br>Coba refresh halaman."
            ),
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=13, color=T.COLOR_MUTED),
        )
        fig.update_layout(height=240, **{k: v for k, v in T.PLOTLY_LAYOUT.items()
                                         if k not in ("colorway", "margin")})
        fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
        return fig

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[f"Umur {a} tahun" for a in AGES],
        horizontal_spacing=0.07,
        shared_yaxes=True,
    )

    legend_shown: set[float] = set()
    # y axis pakai Perempuan di ATAS, Laki-laki di BAWAH (urutan visual: P-L).
    y_categories = ["Laki-laki", "Perempuan"]   # Plotly horizontal bar bawah→atas

    for col_i, age in enumerate(AGES, start=1):
        for code in T.PROTECT_ORDER:
            xs, ys, hover_lines = [], [], []
            for gkey, glabel in GENDERS:
                column = f"protect_{gkey}_{age}"
                n = int((fdf[column] == code).sum())
                xs.append(n)
                ys.append(glabel)
                hover_lines.append(
                    f"<b>{glabel}, umur {age} thn</b><br>"
                    f"{T.PROTECT_LABELS[code]}: {n} negara"
                )
            show = code not in legend_shown
            legend_shown.add(code)
            fig.add_trace(
                go.Bar(
                    y=ys,
                    x=xs,
                    orientation="h",
                    name=T.PROTECT_LABELS[code],
                    marker_color=T.PROTECT_COLORS[code],
                    legendgroup=f"prot_{code}",
                    showlegend=show,
                    text=[str(n) if n > 0 else "" for n in xs],
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white", size=11),
                    hovertext=hover_lines,
                    hovertemplate="%{hovertext}<extra></extra>",
                ),
                row=1, col=col_i,
            )

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=260,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.45,
            xanchor="center", x=0.5, font=dict(size=10),
            traceorder="normal",
        ),
        bargap=0.30,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        categoryorder="array", categoryarray=y_categories,
        tickfont=dict(size=10),
    )
    return T.lock_static(fig)
