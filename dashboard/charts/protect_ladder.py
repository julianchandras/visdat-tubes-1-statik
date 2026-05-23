"""Section bottom-left — Tangga Perlindungan menurut Umur Anak (single age).

Saat user pilih umur (13 / 15 / 17 tahun lewat widget filter di app.py), render
DUA bar horizontal sandingkan: Perempuan & Laki-laki, masing-masing 4 kategori
stack (Dilarang / Court+pregnancy / Izin ortu / Tanpa pembatasan).

Sebelumnya: small multiples 3 panel (1×3) — semua umur sekaligus. Diganti ke
single-age + filter (revisi tim): chart lebih kompak (slot half-width bersama
timeseries di bottom row), annotation lebih lega untuk segment kecil terbaca.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T


GENDERS = (("girl", "Perempuan"), ("boy", "Laki-laki"))


def render(fdf, age: int = 13) -> go.Figure:
    """Render single-age view.

    Parameters
    ----------
    fdf : DataFrame negara terfilter.
    age : 13, 15, atau 17 → memilih kolom protect_girl_{age} & protect_boy_{age}.
    """
    needed = [f"protect_{g}_{age}" for g, _ in GENDERS]
    missing = [c for c in needed if c not in fdf.columns]
    if missing:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Data umur {age} belum lengkap. Coba refresh halaman.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12, color=T.COLOR_MUTED),
        )
        fig.update_layout(height=280, **{k: v for k, v in T.PLOTLY_LAYOUT.items()
                                         if k not in ("colorway", "margin")})
        fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
        return T.lock_static(fig)

    # Hitung count per (gender, kategori) + posisi midpoint kumulatif untuk
    # anchor annotation outside bar.
    gender_counts: dict[str, dict[float, int]] = {}
    annotations_data = []
    for gkey, glabel in GENDERS:
        column = f"protect_{gkey}_{age}"
        gender_counts[glabel] = {
            code: int((fdf[column] == code).sum()) for code in T.PROTECT_ORDER
        }
        cum = 0
        for code in T.PROTECT_ORDER:
            n = gender_counts[glabel][code]
            if n > 0:
                annotations_data.append(
                    (glabel, cum + n / 2, n, T.PROTECT_COLORS[code])
                )
            cum += n

    fig = go.Figure()
    for code in T.PROTECT_ORDER:
        xs = [gender_counts[glabel][code] for _, glabel in GENDERS]
        ys = [glabel for _, glabel in GENDERS]
        hover_lines = [
            f"<b>{glabel}, umur {age} thn</b><br>"
            f"{T.PROTECT_LABELS[code]}: {n} negara"
            for (_, glabel), n in zip(GENDERS, xs)
        ]
        fig.add_trace(go.Bar(
            y=ys, x=xs, orientation="h",
            name=T.PROTECT_LABELS[code],
            marker_color=T.PROTECT_COLORS[code],
            hovertext=hover_lines,
            hovertemplate="%{hovertext}<extra></extra>",
        ))

    # Annotations: keduanya di ATAS bar (yshift +22), warna sesuai kategori.
    for glabel, mid_x, n, color in annotations_data:
        fig.add_annotation(
            x=mid_x, y=glabel,
            yshift=22,
            text=f"<b>{n}</b>",
            showarrow=False,
            font=dict(size=10, color=color, family=T.FONT_SANS),
            xanchor="center",
        )

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=280,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.40,
            xanchor="center", x=0.5, font=dict(size=10),
            traceorder="normal",
        ),
        bargap=0.55,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        categoryorder="array",
        categoryarray=["Laki-laki", "Perempuan"],
        tickfont=dict(size=11),
    )
    return T.lock_static(fig)
