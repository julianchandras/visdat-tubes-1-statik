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

    # Kumpulkan annotations untuk angka outside (di atas bar P, di bawah bar L).
    # Pendekatan ini menggantikan inline text — segment kecil (mis. 5 negara) yang
    # sebelumnya tertelan border antar segment sekarang terbaca jelas.
    annotations_data = []   # tuples (col_i, glabel, mid_x, n, color)

    for col_i, age in enumerate(AGES, start=1):
        # Counts per (gender, kategori) untuk subplot ini, plus cumulative
        # midpoints utk anchor annotation.
        gender_counts: dict[str, dict[float, int]] = {}
        for gkey, glabel in GENDERS:
            column = f"protect_{gkey}_{age}"
            gender_counts[glabel] = {
                code: int((fdf[column] == code).sum())
                for code in T.PROTECT_ORDER
            }
            # Hitung midpoint kumulatif (untuk anchor angka)
            cum = 0
            for code in T.PROTECT_ORDER:
                n = gender_counts[glabel][code]
                if n > 0:
                    annotations_data.append(
                        (col_i, glabel, cum + n / 2, n, T.PROTECT_COLORS[code])
                    )
                cum += n

        for code in T.PROTECT_ORDER:
            xs = [gender_counts[glabel][code] for _, glabel in GENDERS]
            ys = [glabel for _, glabel in GENDERS]
            hover_lines = [
                f"<b>{glabel}, umur {age} thn</b><br>"
                f"{T.PROTECT_LABELS[code]}: {n} negara"
                for (_, glabel), n in zip(GENDERS, xs)
            ]
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
                    hovertext=hover_lines,
                    hovertemplate="%{hovertext}<extra></extra>",
                ),
                row=1, col=col_i,
            )

    # Tambah annotations outside: P di ATAS bar (yshift +14px),
    # L di BAWAH bar (yshift -14px). Hindari menumpuk antar dua bar.
    for col_i, glabel, mid_x, n, color in annotations_data:
        yshift = 14 if glabel == "Perempuan" else -14
        fig.add_annotation(
            xref=f"x{col_i}", yref=f"y{col_i}",
            x=mid_x, y=glabel,
            yshift=yshift,
            text=f"<b>{n}</b>",
            showarrow=False,
            font=dict(size=10, color=color, family=T.FONT_SANS),
            xanchor="center",
        )

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=320,   # naik dari 260 supaya ada ruang untuk annotations atas+bawah
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.40,
            xanchor="center", x=0.5, font=dict(size=10),
            traceorder="normal",
        ),
        bargap=0.55,   # bargap besar = ruang vertikal lebih untuk annotations
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        categoryorder="array", categoryarray=y_categories,
        tickfont=dict(size=10),
    )
    return T.lock_static(fig)
