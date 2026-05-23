"""Section 4a — Komposisi tingkat perlindungan (donut).

Donut SELALU menampilkan komposisi UTUH 193 negara (tidak ikut filter). Saat
filter tingkat perlindungan aktif, slice yang ada di filter tetap opak; slice
lain diredupkan (opacity rendah). Saat tidak ada filter perlindungan, semua
slice opak penuh.

Revisi tim:
- Pie chart utuh full data (bukan subset terfilter).
- Filter perlindungan → redupkan kategori non-filter, jangan hilangkan.
- Tanpa judul (st.markdown sudah menanganinya).
- Tanpa legend internal (shared dengan legenda peta).
- Klik slice → emit event ke app (handled via on_select di app.py).
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T

DIM_OPACITY = 0.25


def render(full_df, severity_filter: list[float] | None = None) -> go.Figure:
    """Render donut komposisi.

    Parameters
    ----------
    full_df : DataFrame 193 negara (SELALU; tidak boleh subset terfilter).
    severity_filter : list kode loop_summ yang aktif di filter perlindungan.
        Bila empty/None → semua slice opak.
        Bila ada isi → slice dalam filter opak, sisanya redup.
    """
    active = set(severity_filter or [])
    has_filter = len(active) > 0

    labels, values, colors, opacities, codes = [], [], [], [], []
    for code in T.LOOP_SUMM_ORDER:
        n = int((full_df["loop_summ"] == code).sum())
        if n:
            labels.append(T.LOOP_SUMM_LABELS[code])
            values.append(n)
            colors.append(T.LOOP_SUMM_COLORS[code])
            opacities.append(1.0 if (not has_filter or code in active) else DIM_OPACITY)
            codes.append(code)
    n_nodata = int(full_df["loop_summ"].isna().sum())
    if n_nodata:
        labels.append(T.LABEL_NO_DATA)
        values.append(n_nodata)
        colors.append(T.NO_DATA_COLOR)
        opacities.append(1.0 if not has_filter else DIM_OPACITY)
        codes.append(None)

    # Plotly Pie marker_colors tidak terima alpha per-slice langsung. Bake
    # opacity ke hex rgba untuk setiap slice (lebih reliable lintas versi).
    def _hex_to_rgba(hex_color: str, alpha: float) -> str:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha:.2f})"

    rgba_colors = [_hex_to_rgba(c, a) for c, a in zip(colors, opacities)]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=rgba_colors, line=dict(color="white", width=1.5)),
        sort=False, direction="clockwise",
        textinfo="value", textfont=dict(size=13),
        hovertemplate="<b>%{label}</b><br>%{value} negara (%{percent})<extra></extra>",
        # customdata = kode loop_summ untuk handler klik di app.py.
        customdata=codes,
    ))
    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        height=360,
        showlegend=False,    # legenda di-share dengan peta
        clickmode="event+select",
    )
    return fig
