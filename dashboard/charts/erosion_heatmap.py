"""Section B — Heatmap "Erosi Hukum Pernikahan Anak".

Matrix: rows = negara, columns = 5 layer hukum (legal → +izin ortu → +adat/agama
→ loophole gabungan → semua exception), warna = usia minimum nikah perempuan.

Pakai kolom minage_fem_pc & minage_fem_crlaw yang sebelumnya TIDAK disentuh.
Pertanyaan yang dijawab: "dari layer mana erosi hukum sebenarnya datang?" —
apakah dari izin orang tua, hukum adat/agama, atau gabungan?

Teknik viz baru: heatmap matrix (country × indicator) — sangat efektif untuk
membandingkan banyak negara × banyak dimensi sekaligus.
"""
from __future__ import annotations

import plotly.graph_objects as go

import theme as T


# Mapping kode usia ordinal (1/2/3/5/9) → step 0..4 untuk colorscale kontinu.
# 5→4 (≥18 paling baik), 3→3, 2→2, 1→1, 9→0 (unknown ≈ paling parah moral-wise).
# NaN tetap NaN otomatis lewat .replace().
_STEP_MAP = {5.0: 4.0, 3.0: 3.0, 2.0: 2.0, 1.0: 1.0, 9.0: 0.0}
_CODE_TEXT = {5.0: "≥18", 3.0: "16-17", 2.0: "14-15", 1.0: "≤13", 9.0: "?"}


def render(fdf, top_n: int = 30) -> go.Figure:
    """Render heatmap erosi.

    Strategi pemilihan baris (negara): negara yang menunjukkan EROSI TERBESAR antar
    layer (selisih max-min dari 5 kode usia) → paling informatif untuk narasi
    "loophole datang dari mana". Top-N negara terdampak ditampilkan.
    """
    layer_cols = [c for c, _ in T.EROSION_LAYERS]
    layer_labels = [lbl for _, lbl in T.EROSION_LAYERS]

    # Defensive: graceful kalau kolom layer hilang (mis. cache CSV skema lama).
    missing = [c for c in layer_cols if c not in fdf.columns]
    if missing:
        fig = go.Figure()
        fig.add_annotation(
            text=(
                "Data belum lengkap (kolom " + ", ".join(missing) + " hilang).<br>"
                "Coba refresh halaman atau Reboot app."
            ),
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=13, color=T.COLOR_MUTED),
        )
        fig.update_layout(height=360, **{k: v for k, v in T.PLOTLY_LAYOUT.items()
                                         if k not in ("colorway", "margin")})
        fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
        return fig

    # Hitung skor "erosi" per negara: range nilai antar layer (yang non-NaN).
    sub = fdf[["country", "iso3"] + layer_cols].copy()
    sub["erosion"] = sub[layer_cols].max(axis=1) - sub[layer_cols].min(axis=1)
    # Pilih Top-N berdasarkan erosi terbesar, fallback alfabetis bila <= top_n.
    if len(sub) > top_n:
        sub = sub.nlargest(top_n, "erosion")
    sub = sub.sort_values(["erosion", "country"], ascending=[False, True])

    # Bangun matrix: rows = country, cols = layer. Pakai pandas .replace() yang
    # naturally NaN-safe (tanpa RuntimeWarning seperti np.vectorize).
    raw = sub[layer_cols]
    z = raw.replace(_STEP_MAP).to_numpy(dtype=float)
    # Annotation: kode usia asli sebagai label sel (singkat); NaN → "".
    text = raw.replace(_CODE_TEXT).fillna("").astype(str).to_numpy()

    # Colorscale diskrit 5 step (0..4) yang selaras MINAGE_COLORS.
    # Plotly butuh tuples (frac, color); kita pakai stops eksplisit.
    colorscale = [
        [0.0,  T.MINAGE_COLORS[9.0]],   # unknown / paling parah moral
        [0.20, T.MINAGE_COLORS[9.0]],
        [0.20, T.MINAGE_COLORS[1.0]],
        [0.40, T.MINAGE_COLORS[1.0]],
        [0.40, T.MINAGE_COLORS[2.0]],
        [0.60, T.MINAGE_COLORS[2.0]],
        [0.60, T.MINAGE_COLORS[3.0]],
        [0.80, T.MINAGE_COLORS[3.0]],
        [0.80, T.MINAGE_COLORS[5.0]],
        [1.0,  T.MINAGE_COLORS[5.0]],
    ]

    fig = go.Figure(go.Heatmap(
        z=z, x=layer_labels, y=sub["country"].tolist(),
        text=text, texttemplate="%{text}", textfont=dict(size=10, color="white"),
        colorscale=colorscale,
        zmin=-0.5, zmax=4.5,
        showscale=False,
        xgap=2, ygap=2,
        hovertemplate=(
            "<b>%{y}</b><br>Layer: %{x}<br>"
            "Usia minimum: %{text}<extra></extra>"
        ),
    ))
    # Buang 'margin' dari template karena kita override (top lebih lega untuk x-axis di atas).
    layout = {k: v for k, v in T.PLOTLY_LAYOUT.items() if k not in ("colorway", "margin")}
    height = max(360, 22 * len(sub) + 80)
    fig.update_layout(
        **layout,
        height=height,
        xaxis=dict(side="top", tickfont=dict(size=11)),
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        margin=dict(l=10, r=10, t=80, b=10),
    )
    return fig
