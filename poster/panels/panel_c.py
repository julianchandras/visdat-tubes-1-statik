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


# Kategori loophole — label display + kolom + kriteria kode
LOOPHOLE_CATEGORIES = [
    {
        "label":   "Parental Consent",
        "column":  "except_pc",
        "codes":   [2, 3],
        "sublabel": "Izin ortu jadi celah — paling lunak di muka hukum",
    },
    {
        "label":   "Hukum Adat / Agama",
        "column":  "except_crlaw",
        "codes":   [2],
        "sublabel": "Paralel sistem hukum civil yang tidak tegas",
    },
    {
        "label":   "Kehamilan",
        "column":  "except_preg",
        "codes":   [2],
        "sublabel": "Dibolehkan kalau sudah hamil / melahirkan",
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
    if fig is None:
        fig = plt.figure(figsize=(8.2, 5.8), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[1.0, 3.5, 0.55],
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
            height_ratios=[1.0, 3.5, 0.55],
            hspace=0.30,
        )
        title_ax = fig.add_subplot(inner[0])
        chart_ax = fig.add_subplot(inner[1])
        footer_ax = fig.add_subplot(inner[2])

    # ── Title block ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.75, "DARI MANA CELAHNYA BOCOR?",
        transform=title_ax.transAxes,
        family="serif", fontsize=20, weight=900, color=T.COLOR_HEADLINE,
    )
    title_ax.text(
        0.0, 0.18,
        "Jumlah negara yang memiliki pengecualian atas batas usia 18, per mekanisme hukum",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=11, color=T.COLOR_MUTED,
    )

    # ── Stacked horizontal bars ──
    y_positions = np.arange(len(counts))[::-1]   # terbesar di atas
    bar_height = 0.55

    for yi, (_, row) in zip(y_positions, counts.iterrows()):
        left = 0.0
        for inc in INCOME_ORDER:
            v = row[inc]
            if v == 0:
                continue
            chart_ax.barh(
                yi, v, height=bar_height, left=left,
                color=STACK_COLORS[inc],
                edgecolor=T.COLOR_BG, linewidth=1.5,
            )
            # Label segment value: inside bar kalau cukup lebar, else
            # outside dengan connector tipis (semua angka TERLIHAT)
            if v >= max_total * 0.05:
                chart_ax.text(
                    left + v / 2, yi, str(v),
                    ha="center", va="center",
                    family="monospace", fontsize=10, weight=500,
                    color=("white" if inc == "Low-income" else T.COLOR_HEADLINE),
                )
            else:
                # Small segment: label di atas bar dengan vertical offset
                chart_ax.annotate(
                    str(v),
                    xy=(left + v / 2, yi + bar_height / 2),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom",
                    family="monospace", fontsize=9, weight=500,
                    color=STACK_COLORS[inc],
                )
            left += v

        # Total count annotation di ujung bar
        chart_ax.text(
            row["total"] + max_total * 0.015, yi,
            f"{row['total']} negara",
            ha="left", va="center",
            family="serif", fontsize=16, weight=700,
            color=T.COLOR_HEADLINE,
        )

    # ── Category labels kiri ──
    for yi, (_, row) in zip(y_positions, counts.iterrows()):
        cat_meta = next(c for c in LOOPHOLE_CATEGORIES
                        if c["label"] == row["category"])
        chart_ax.text(
            -max_total * 0.02, yi + 0.18,
            row["category"],
            ha="right", va="center",
            family="serif", fontsize=13, weight=700,
            color=T.COLOR_HEADLINE,
        )
        chart_ax.text(
            -max_total * 0.02, yi - 0.18,
            cat_meta["sublabel"],
            ha="right", va="center",
            family="sans-serif", fontsize=9, style="italic",
            color=T.COLOR_MUTED,
        )

    # Axis styling — minimalist
    chart_ax.set_xlim(-max_total * 0.65, max_total * 1.22)
    chart_ax.set_ylim(-0.7, len(counts) - 0.3)
    chart_ax.set_yticks([])
    chart_ax.set_xticks([])
    for spine in ["top", "right", "bottom", "left"]:
        chart_ax.spines[spine].set_visible(False)
    chart_ax.tick_params(length=0)

    # ── Legend in-panel (pojok kanan atas) ──
    legend_y = len(counts) - 0.35
    legend_x_base = max_total * 0.50
    chart_ax.text(
        legend_x_base, legend_y + 0.25, "Kelompok pendapatan:",
        family="sans-serif", fontsize=9, color=T.COLOR_MUTED,
        weight=600,
    )
    for i, inc in enumerate(INCOME_ORDER):
        xi = legend_x_base + i * (max_total * 0.22)
        chart_ax.add_patch(
            plt.Rectangle(
                (xi, legend_y - 0.10), max_total * 0.035, 0.22,
                facecolor=STACK_COLORS[inc], edgecolor="none",
            )
        )
        chart_ax.text(
            xi + max_total * 0.045, legend_y + 0.01,
            inc,
            family="sans-serif", fontsize=9, color=T.COLOR_BODY,
            va="center",
        )

    # ── Footer caption dengan konteks "no protection" ──
    footer_ax.axis("off")
    footer_ax.text(
        0.0, 0.8,
        f"Catatan: {n_no_protect} negara lainnya tidak memiliki perlindungan sama sekali "
        f"(usia di bawah 18 dibolehkan tanpa syarat apapun — di luar 3 kategori di atas).",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=9, color=T.COLOR_ACCENT,
        weight=600, va="top",
    )
    footer_ax.text(
        0.0, 0.25,
        "Sumber: WORLD Policy Analysis Center, Child Marriage Laws 2023. "
        "Kategori berdasarkan kode except_pc = 2 atau 3, except_crlaw = 2, except_preg = 2.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=8, color=T.COLOR_MUTED,
        va="top",
    )

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
