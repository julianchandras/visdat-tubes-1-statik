"""Section bottom-left — Tangga Perlindungan menurut Umur Anak.

Single-age view: untuk umur yang dipilih (13/15/17 via radio di app.py), render
horizontal stacked bars untuk gender yang aktif (P, L, atau keduanya — via 2
checkbox Streamlit di app.py).

Y-axis pakai short label "P" / "L" (revisi tim: keterangan panjang ada di
checkbox filter ("Perempuan (P)" / "Laki-laki (L)"), y-axis tidak perlu
diulang).

Angka per segment via Plotly built-in trace `text` (textposition='inside') →
otomatis ikut visibility saat user toggle kategori di legend (no orphan).

Legend 4 kategori dipaksa 2×2 grid via entrywidth fraction (revisi tim:
"seluas apapun layoutnya pastikan dia ada dua row").
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T

# (key column, short y-axis label, long checkbox label)
GENDERS = (
    ("girl", "P", "Perempuan (P)"),
    ("boy",  "L", "Laki-laki (L)"),
)


def _text_color_for_bg(hex_color: str) -> str:
    """Pilih warna text (dark navy vs white) berdasarkan luminance bg."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    Y = 0.299 * r + 0.587 * g + 0.114 * b
    return "#2D3142" if Y > 140 else "white"


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=12, color=T.COLOR_MUTED),
    )
    fig.update_layout(height=280, **{k: v for k, v in T.PLOTLY_LAYOUT.items()
                                     if k not in ("colorway", "margin")})
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    return T.lock_static(fig)


def render(fdf, age: int = 13) -> go.Figure:
    """Render single-age view dgn KEDUA gender (P & L) selalu ditampilkan.

    Revisi tim: filter checkbox P/L dihapus (tidak perlu); keterangan
    mapping P=Perempuan, L=Laki-laki ada di caption Tangga di app.py.
    """
    genders = list(GENDERS)
    needed = [f"protect_{g[0]}_{age}" for g in genders]
    missing = [c for c in needed if c not in fdf.columns]
    if missing:
        return _empty_figure(
            f"Data umur {age} belum lengkap. Coba refresh halaman."
        )

    # Hitung count per (gender, kategori).
    gender_counts: dict[str, dict[float, int]] = {}
    for gkey, gshort, _ in genders:
        column = f"protect_{gkey}_{age}"
        gender_counts[gshort] = {
            code: int((fdf[column] == code).sum()) for code in T.PROTECT_ORDER
        }

    fig = go.Figure()
    for code in T.PROTECT_ORDER:
        xs = [gender_counts[gshort][code] for _, gshort, _ in genders]
        ys = [gshort for _, gshort, _ in genders]
        hover_lines = [
            f"<b>{glong}, umur {age} thn</b><br>"
            f"{T.PROTECT_LABELS[code]}: {n} negara"
            for (_, _, glong), n in zip(genders, xs)
        ]
        text_color = _text_color_for_bg(T.PROTECT_COLORS[code])
        fig.add_trace(go.Bar(
            y=ys, x=xs, orientation="h",
            name=T.PROTECT_LABELS[code],
            marker_color=T.PROTECT_COLORS[code],
            text=[f"<b>{n}</b>" if n > 0 else "" for n in xs],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=10, color=text_color),
            hovertext=hover_lines,
            hovertemplate="%{hovertext}<extra></extra>",
        ))

    # Y-axis order: P di atas, L di bawah (Plotly horizontal bar bawah → atas).
    y_categories_reverse = [g[1] for g in reversed(GENDERS)]   # ["L", "P"]

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k not in ("colorway", "margin")}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=380,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(size=12),
            traceorder="normal",
            entrywidthmode="fraction",
            entrywidth=0.45,
            itemsizing="constant",
        ),
        margin=dict(l=10, r=10, t=85, b=10),
        bargap=0.40,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        categoryorder="array",
        categoryarray=y_categories_reverse,
        tickfont=dict(size=12, color=T.COLOR_HEADLINE),
    )
    return T.lock_static(fig)
