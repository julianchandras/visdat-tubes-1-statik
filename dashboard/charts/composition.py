"""Section pie — Komposisi tingkat perlindungan (donut).

SELALU menampilkan komposisi UTUH 193 negara (tidak ikut filter). Saat filter
tingkat perlindungan aktif, slice yang ada di filter tetap opak; slice lain
diredupkan (opacity rendah). Angka pada slice juga ikut redup → visual fokus
pindah ke warna slice (sesuai keluhan tim ttg ketidakterbacaan angka di slice
salmon saat di-highlight).

Catatan: fitur klik slice → set filter SUDAH DIBATALKAN (Streamlit Cloud Plotly
Pie selection tidak reliable lintas versi). on_select tidak dipakai lagi.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T

DIM_OPACITY = 0.25
HIGHLIGHTED_TEXT_COLOR = "#2D3142"   # dark, kontras tinggi
DIMMED_TEXT_COLOR = "#C9CACC"        # sangat pudar, fade dgn slice yg dim


def render(full_df, severity_filter: list[float] | None = None) -> go.Figure:
    """Render donut komposisi.

    Parameters
    ----------
    full_df : DataFrame 193 negara (SELALU, tidak ikut filter).
    severity_filter : list kode loop_summ yang aktif di filter perlindungan.
        Bila empty/None → semua slice opak, semua angka warna kontras.
        Bila ada isi → slice/angka dalam filter opak penuh, sisanya redup.
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

    def _hex_to_rgba(hex_color: str, alpha: float) -> str:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha:.2f})"

    rgba_colors = [_hex_to_rgba(c, a) for c, a in zip(colors, opacities)]

    # Per-slice text dgn warna inline HTML: highlighted = dark bold,
    # dimmed = sangat pudar. Plotly Pie textinfo='text' menerima HTML span.
    texts = []
    for code, v in zip(codes, values):
        is_active = (not has_filter) or (code in active)
        color = HIGHLIGHTED_TEXT_COLOR if is_active else DIMMED_TEXT_COLOR
        texts.append(f"<b style='color:{color}'>{v}</b>")

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=rgba_colors, line=dict(color="white", width=1.5)),
        sort=False, direction="clockwise",
        text=texts, textinfo="text", textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>%{value} negara (%{percent})<extra></extra>",
    ))
    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k != "colorway"}
    fig.update_layout(
        **layout,
        height=240,
        showlegend=False,    # legenda di-share lewat HTML legend di app.py
    )
    return T.lock_static(fig)
