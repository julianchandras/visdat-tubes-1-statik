"""Section bottom-left — Tangga Perlindungan menurut Umur Anak (single age).

Saat user pilih umur (13 / 15 / 17 tahun lewat widget filter di app.py), render
DUA bar horizontal sandingkan: Perempuan & Laki-laki, masing-masing 4 kategori
stack (Dilarang / Court+pregnancy / Izin ortu / Tanpa pembatasan).

Angka per segment di-render INSIDE bar via Plotly built-in `text` (bukan
annotations layer). Trade-off:
- Inside text otomatis ikut visibility trace → saat user klik legend untuk
  toggle kategori, angka kategori ybs juga hilang (TIDAK orphan). Revisi tim:
  "anotasi angka bagi kategori dinonaktifkan seharusnya dihapus".
- Segment kecil (count < threshold) bisa kurang terbaca; mitigasi: warna
  text per-kategori berbasis luminance bg (dark text pada bg terang, white
  pada bg gelap) + bold.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T


GENDERS = (("girl", "Perempuan"), ("boy", "Laki-laki"))


def _text_color_for_bg(hex_color: str) -> str:
    """Pilih warna text (dark navy vs white) berdasarkan luminance bg.

    Threshold 140 di skala 0..255 — cukup baik untuk 4 PROTECT_COLORS:
    - hijau gelap #1A7F3C → white
    - kuning #F4B400 → dark
    - terracotta #E07A5F → dark
    - dark red #7B0000 → white
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    Y = 0.299 * r + 0.587 * g + 0.114 * b
    return "#2D3142" if Y > 140 else "white"


def render(fdf, age: int = 13) -> go.Figure:
    """Render single-age view."""
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

    # Hitung count per (gender, kategori).
    gender_counts: dict[str, dict[float, int]] = {}
    for gkey, glabel in GENDERS:
        column = f"protect_{gkey}_{age}"
        gender_counts[glabel] = {
            code: int((fdf[column] == code).sum()) for code in T.PROTECT_ORDER
        }

    fig = go.Figure()
    for code in T.PROTECT_ORDER:
        xs = [gender_counts[glabel][code] for _, glabel in GENDERS]
        ys = [glabel for _, glabel in GENDERS]
        hover_lines = [
            f"<b>{glabel}, umur {age} thn</b><br>"
            f"{T.PROTECT_LABELS[code]}: {n} negara"
            for (_, glabel), n in zip(GENDERS, xs)
        ]
        text_color = _text_color_for_bg(T.PROTECT_COLORS[code])
        fig.add_trace(go.Bar(
            y=ys, x=xs, orientation="h",
            name=T.PROTECT_LABELS[code],
            marker_color=T.PROTECT_COLORS[code],
            # Inside text — otomatis hilang saat user toggle kategori dari
            # legend (Plotly menghilangkan trace, text ikut hilang).
            text=[f"<b>{n}</b>" if n > 0 else "" for n in xs],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=10, color=text_color),
            hovertext=hover_lines,
            hovertemplate="%{hovertext}<extra></extra>",
        ))

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        barmode="stack",
        height=320,   # +40 dari 280 untuk akomodasi legend 2 row
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.55,        # turun lebih, beri ruang 2 row
            xanchor="center", x=0.5,
            font=dict(size=10),
            traceorder="normal",
            # entrywidth=0.48 (= 48% legend container per item) → 4 kategori
            # otomatis wrap jadi 2 item per row × 2 row, dengan sisa 4% jadi
            # gap implicit antar kolom. Behavior konsisten di width berapapun
            # (revisi tim: "seluas apapun layoutnya pastikan dia ada dua row").
            entrywidthmode="fraction",
            entrywidth=0.48,
        ),
        bargap=0.40,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(
        showgrid=False, zeroline=False,
        categoryorder="array",
        categoryarray=["Laki-laki", "Perempuan"],
        tickfont=dict(size=11),
    )
    return T.lock_static(fig)
