"""Section B — "Erosi Hukum: Aliran Negara Antar Layer Hukum" (Sankey).

Menggantikan heatmap matrix yang sebelumnya. Sankey 3-layer menunjukkan
**aliran** negara antar 3 layer hukum (Legal → Loop → Any) per kategori usia
minimum nikah perempuan. Lebar pita = jumlah negara yang berpindah.

Narasi: dari N negara yang `≥18 di Legal`, M masih `≥18 di Loop`, K masih
`≥18 di Any`. Pita yang "jatuh" dari kelas ≥18 ke kelas usia lebih muda =
erosi hukum perlindungan akibat exception.

Teknik viz: alluvial/Sankey flow — lebih story-driven dari heatmap matrix.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T


LAYERS = [
    ("minage_fem_leg",  "Hukum Standar\n(tanpa pengecualian)"),
    ("minage_fem_loop", "+ Celah Izin Orang Tua\natau Adat / Agama"),
    ("minage_fem_any",  "+ Semua Pengecualian\n(kehamilan, pengadilan, dll)"),
]
# Urutan kategori dari atas ke bawah dalam tiap layer (visual top→bottom).
CAT_ORDER = [5.0, 3.0, 2.0, 1.0, 9.0]
CAT_LABELS = {
    5.0: "≥ 18 tahun",
    3.0: "16-17 tahun",
    2.0: "14-15 tahun",
    1.0: "≤ 13 tahun",
    9.0: "Tidak diketahui",
}
CAT_COLORS = T.MINAGE_COLORS    # selaras heatmap palette ordinal


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.2f})"


def render(fdf) -> go.Figure:
    needed = [c for c, _ in LAYERS]
    missing = [c for c in needed if c not in fdf.columns]
    if missing:
        fig = go.Figure()
        fig.add_annotation(
            text="Data layer hukum belum lengkap. Coba refresh halaman.",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=13, color=T.COLOR_MUTED),
        )
        fig.update_layout(height=420, **{k: v for k, v in T.PLOTLY_LAYOUT.items()
                                         if k not in ("colorway", "margin")})
        fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
        return fig

    # ── Bangun node list: 3 layer × 5 kategori = 15 nodes.
    # Posisi node EKSPLISIT supaya urutan dalam tiap kolom konsisten
    # top→bottom dari terbaik (≥18) ke terburuk (≤13) + ambigu (Tidak
    # diketahui) di paling bawah. Tanpa ini Plotly auto-arrange berbasis
    # berat link → posisi node "Tidak diketahui" loncat antar kolom
    # (revisi tim).
    LAYER_X = [0.01, 0.5, 0.99]   # column x (relatif domain Sankey)
    CAT_Y = {
        5.0: 0.05,   # ≥ 18 thn — paling atas (terbaik)
        3.0: 0.28,   # 16-17
        2.0: 0.50,   # 14-15
        1.0: 0.73,   # ≤ 13
        9.0: 0.95,   # Tidak diketahui — paling bawah (ambigu)
    }
    node_labels: list[str] = []
    node_colors: list[str] = []
    node_x: list[float] = []
    node_y: list[float] = []
    node_idx: dict[tuple[int, float], int] = {}     # (layer_i, code) -> node index
    for li, (_, layer_label) in enumerate(LAYERS):
        for code in CAT_ORDER:
            node_idx[(li, code)] = len(node_labels)
            node_labels.append(CAT_LABELS[code])
            node_colors.append(CAT_COLORS[code])
            node_x.append(LAYER_X[li])
            node_y.append(CAT_Y[code])

    # ── Bangun link list: untuk tiap transisi (layer i → i+1), agregasi count.
    source, target, value, link_colors, link_labels = [], [], [], [], []
    for li in range(len(LAYERS) - 1):
        col_a = LAYERS[li][0]
        col_b = LAYERS[li + 1][0]
        # Pasangan kategori (a,b) → jumlah negara.
        pair_counts = (
            fdf.dropna(subset=[col_a, col_b])
               .groupby([col_a, col_b]).size()
               .reset_index(name="n")
        )
        for _, row in pair_counts.iterrows():
            cat_a = float(row[col_a])
            cat_b = float(row[col_b])
            if cat_a not in CAT_ORDER or cat_b not in CAT_ORDER:
                continue
            src = node_idx[(li, cat_a)]
            tgt = node_idx[(li + 1, cat_b)]
            source.append(src)
            target.append(tgt)
            value.append(int(row["n"]))
            # Warna link: pakai source category warna dgn alpha rendah supaya
            # tetap terlihat halus tanpa menutupi label node.
            link_colors.append(_hex_to_rgba(CAT_COLORS[cat_a], 0.35))
            link_labels.append(
                f"{CAT_LABELS[cat_a]} → {CAT_LABELS[cat_b]}: {int(row['n'])} negara"
            )

    # Sankey domain shrink ke [0.06, 0.94] supaya node leftmost (Legal) &
    # rightmost (Any) tidak menempel tepi. Plotly Sankey merender label node
    # DI LUAR node (kiri utk leftmost col, kanan utk rightmost) — kalau node
    # mepet tepi, label "Legal"/"Any" ter-clip oleh margin.
    SANKEY_X_START, SANKEY_X_END = 0.06, 0.94

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        domain=dict(x=[SANKEY_X_START, SANKEY_X_END]),
        # textfont eksplisit: warna dark + family Arial supaya label node tidak
        # tampak "hollow".
        textfont=dict(color=T.COLOR_BODY, size=13, family="Arial, sans-serif"),
        node=dict(
            label=node_labels,
            color=node_colors,
            x=node_x,
            y=node_y,
            pad=18,
            thickness=18,
            line=dict(color="white", width=0.5),
            hovertemplate="<b>%{label}</b><br>%{value} negara<extra></extra>",
        ),
        link=dict(
            source=source, target=target, value=value,
            color=link_colors,
            customdata=link_labels,
            hovertemplate="%{customdata}<extra></extra>",
        ),
        valueformat=".0f",
    ))

    # Anotasi header layer DI ATAS masing-masing kolom Sankey. Posisi x
    # diselaraskan dengan domain Sankey (bukan paper 0..1) supaya label
    # tepat di atas node-nya.
    annotations = []
    for li, (_, layer_label) in enumerate(LAYERS):
        # Map li=[0,1,2] → x dalam range SANKEY_X_START..END
        x_pos = SANKEY_X_START + (SANKEY_X_END - SANKEY_X_START) * li / (len(LAYERS) - 1)
        annotations.append(dict(
            x=x_pos, y=1.08, xref="paper", yref="paper",
            text=f"<b>{layer_label.replace(chr(10), '<br>')}</b>",
            showarrow=False,
            font=dict(family=T.FONT_SANS, size=11, color=T.COLOR_HEADLINE),
            xanchor="center",
        ))

    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items()
              if k not in ("colorway", "margin")}
    fig.update_layout(
        **layout,
        height=460,
        annotations=annotations,
        # Margin l/r besar supaya label node leftmost/rightmost (text di luar
        # node) ada ruang menampung (tidak ter-clip oleh tepi figure).
        margin=dict(l=90, r=90, t=60, b=20),
    )
    return T.lock_static(fig)
