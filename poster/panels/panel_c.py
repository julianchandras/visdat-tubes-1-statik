"""Panel C — Stacked bar breakdown mekanisme loophole.

Menunjukkan 3 tipe celah hukum (parental consent, religious/customary,
pregnancy exception) dihitung per `wb_econ` income group. Editorial hook:
bahkan negara high-income masih menyisakan celah parental consent sebagai
mekanisme dominan.

Selaras dengan docs-system-development/spec_desain.md bagian 6.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from poster import theme as T


# ────────────────────────────────────────────────────────────
# Palette — stack color per income group
# ────────────────────────────────────────────────────────────
STACK_COLORS = {
    "Low-income":    "#0F4C5C",   # darkest teal
    "Middle-income": "#5A8F95",   # medium teal
    "High-income":   "#B5D0CC",   # lightest teal
}
INCOME_ORDER = ["Low-income", "Middle-income", "High-income"]


# Kategori loophole — label + sublabel deskriptif (jawab "ini apa?")
# Sublabel diperpendek dengan format paralel "via X" supaya muat di
# half-width Panel C, tidak menjorok ke Panel B.
LOOPHOLE_CATEGORIES = [
    {
        "label":   "Izin Orang Tua",
        "column":  "except_pc",
        "codes":   [2, 3],
        "sublabel": "Pengecualian via izin orang tua / wali",
    },
    {
        "label":   "Hukum Adat/Agama",
        "column":  "except_crlaw",
        "codes":   [2],
        "sublabel": "Pengecualian via hukum adat / agama",
    },
    {
        "label":   "Kehamilan",
        "column":  "except_preg",
        "codes":   [2],
        "sublabel": "Pengecualian via kehamilan / kelahiran",
    },
]


def _compute_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Matrix count: baris = kategori loophole, kolom = income group."""
    rows = []
    for cat in LOOPHOLE_CATEGORIES:
        row = {"category": cat["label"]}
        flag = df[cat["column"]].isin(cat["codes"])
        for inc in INCOME_ORDER:
            row[inc] = int(((df["wb_econ_label"] == inc) & flag).sum())
        row["total"] = int(flag.sum())
        rows.append(row)
    return pd.DataFrame(rows)


def _count_no_protection(df: pd.DataFrame) -> int:
    """Negara dengan value 1 di setidaknya satu kolom exception.

    Value 1 berarti "girls can be married under 18 in all circumstances"
    — bukan exception, tapi struktural tidak melindungi. Ditampilkan
    sebagai footer context, bukan di bar utama.
    """
    mask = (
        (df["except_pc"] == 1)
        | (df["except_crlaw"] == 1)
        | (df["except_preg"] == 1)
    )
    return int(mask.sum())


def render_panel_c(
    df: pd.DataFrame,
    fig: plt.Figure | None = None,
    host_subplot_spec=None,
) -> plt.Figure:
    counts = _compute_counts(df)
    n_no_protect = _count_no_protection(df)
    max_total = counts["total"].max()

    # ── Figure/axes setup ──
    # Footer ratio diperbesar (0.55 → 1.0) supaya muat 2 baris Catatan
    # + 1 baris Sumber tanpa tabrakan.
    if fig is None:
        fig = plt.figure(figsize=(8.2, 5.8), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[1.0, 3.0, 1.0],
            hspace=0.30,
            left=0.04, right=0.98, top=0.95, bottom=0.06,
        )
        title_ax = fig.add_subplot(outer[0])
        chart_ax = fig.add_subplot(outer[1])
        footer_ax = fig.add_subplot(outer[2])
    else:
        assert host_subplot_spec is not None
        inner = GridSpecFromSubplotSpec(
            nrows=3, ncols=1,
            subplot_spec=host_subplot_spec,
            height_ratios=[1.0, 3.0, 1.0],
            hspace=0.30,
        )
        title_ax = fig.add_subplot(inner[0])
        chart_ax = fig.add_subplot(inner[1])
        footer_ax = fig.add_subplot(inner[2])

    # ── Title block ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.85,
        "Apa Saja Celah Hukum Pernikahan Anak?",
        transform=title_ax.transAxes,
        family="serif", fontsize=14, weight=900, color=T.COLOR_HEADLINE,
        va="top",
    )
    title_ax.text(
        0.0, 0.42,
        "Banyak negara mengizinkan pernikahan anak atas alasan izin\n"
        "orang tua, hukum adat/agama, maupun kehamilan.",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=10, color=T.COLOR_MUTED,
        va="top", linespacing=1.4,
    )

    # ── Simple horizontal bar — single color, no income breakdown ──
    y_positions = np.arange(len(counts))[::-1]   # terbesar di atas
    bar_height = 0.55
    BAR_COLOR = T.COLOR_HEADLINE   # deep teal selaras font color headline

    for yi, (_, row) in zip(y_positions, counts.iterrows()):
        chart_ax.barh(
            yi, row["total"], height=bar_height,
            color=BAR_COLOR, edgecolor="none",
        )
        # Total count annotation di ujung bar
        chart_ax.text(
            row["total"] + max_total * 0.015, yi,
            f"{row['total']} negara",
            ha="left", va="center",
            family="serif", fontsize=13, weight=700,
            color=T.COLOR_HEADLINE,
        )

    # ── Category labels kiri — cukup label utama (sublabel dihapus per revisi tim)
    for yi, (_, row) in zip(y_positions, counts.iterrows()):
        chart_ax.text(
            -max_total * 0.02, yi,
            row["category"],
            ha="right", va="center",
            family="serif", fontsize=12, weight=700,
            color=T.COLOR_HEADLINE,
        )

    # Axis styling — minimalist
    chart_ax.set_xlim(-max_total * 0.65, max_total * 1.22)
    chart_ax.set_ylim(-0.7, len(counts) - 0.3)
    chart_ax.set_yticks([])
    chart_ax.set_xticks([])
    for spine in ["top", "right", "bottom", "left"]:
        chart_ax.spines[spine].set_visible(False)
    chart_ax.tick_params(length=0)

    # ── Footer caption dengan konteks "no protection" ──
    footer_ax.axis("off")
    # Catatan di top, Sumber di bottom — gap explicit lewat va anchor
    footer_ax.text(
        0.0, 0.92,
        f"{n_no_protect} negara lainnya tidak memiliki perlindungan sama sekali. "
        f"Anak dengan usia\n"
        f"di bawah 18 tahun dibolehkan menikah secara hukum tanpa syarat tambahan apapun.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=9, color=T.COLOR_ACCENT,
        weight=600, va="top", linespacing=1.4,
    )
    # Sumber dihapus — sudah ada di footer poster utama

    return fig


# ────────────────────────────────────────────────────────────
# CLI untuk render standalone preview
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render Panel C standalone.")
    parser.add_argument(
        "--data", default="data/world-cml-2023-cleaned.csv",
        help="Path CSV dataset cleaned.",
    )
    parser.add_argument(
        "--output", default="output/panel_c_preview.png",
        help="Path output PNG preview.",
    )
    parser.add_argument(
        "--pdf", action="store_true",
        help="Juga export versi PDF vektor.",
    )
    args = parser.parse_args()

    T.setup_matplotlib()
    T.register_local_fonts()

    df = pd.read_csv(args.data)
    fig = render_panel_c(df)

    fig.savefig(args.output, dpi=150, bbox_inches="tight",
                facecolor=T.COLOR_BG)
    print(f"[OK] PNG preview: {args.output}")

    if args.pdf:
        pdf_path = args.output.rsplit(".", 1)[0] + ".pdf"
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight",
                    facecolor=T.COLOR_BG)
        print(f"[OK] PDF vektor : {pdf_path}")
