"""Panel B — Waffle chart: 1 kotak = 1 negara.

Adaptasi waffle chart dengan angka konkret. 186 negara dikelompokkan per
income tier (Low / Middle / High), dengan setiap kelompok punya color
family sendiri. Negara dengan gender gap usia pernikahan diberi warna
gelap (saturated), tanpa gap diberi warna muda (pucat).

Selaras dengan revisi tim — adaptasi unit visualization.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from poster import theme as T


# ────────────────────────────────────────────────────────────
# Konstanta
# ────────────────────────────────────────────────────────────

INCOME_ORDER = ["Low-income", "Middle-income", "High-income"]

# 3 color family EARTHY tones — terracotta, ochre, sage. Tiap family
# punya pasangan dark (gap) + light (no gap). Hue cukup distinct (20°
# orange-red, 45° golden, 90° green) supaya warna muda antar tier tidak
# membingungkan.
WAFFLE_COLORS = {
    ("Low-income",     True):  "#A0410D",   # burnt sienna deep — gap
    ("Low-income",     False): "#E8B89B",   # terracotta light — no gap
    ("Middle-income",  True):  "#996515",   # ochre / mustard deep — gap
    ("Middle-income",  False): "#E8D688",   # wheat warm light — no gap
    ("High-income",    True):  "#4A6741",   # forest moss deep — gap
    ("High-income",    False): "#B5C19D",   # sage light — no gap
}

# Grid 17 cols × 11 rows = 187 cells (1 empty untuk 186 negara)
GRID_COLS = 17
GRID_ROWS = 11


def _prepare_country_sequence(df: pd.DataFrame) -> list[tuple[str, bool, str]]:
    """Return list of (income, has_gap, country_name) ordered for waffle.

    Order: Low gap → Low no-gap → Middle gap → Middle no-gap → High gap → High no-gap.
    Dalam tiap kategori, sort alfabetis untuk reproducibility.
    """
    sub = df.dropna(subset=[
        "wb_econ_label", "minage_fem_loop", "minage_mal_loop",
    ]).copy()
    sub = sub[sub["wb_econ_label"].isin(INCOME_ORDER)]
    sub["has_gap"] = sub["minage_fem_loop"] != sub["minage_mal_loop"]

    sequence: list[tuple[str, bool, str]] = []
    for inc in INCOME_ORDER:
        for gap in (True, False):
            rows = sub[(sub["wb_econ_label"] == inc) & (sub["has_gap"] == gap)]
            for country in sorted(rows["country"]):
                sequence.append((inc, gap, country))
    return sequence


def render_panel_b(
    df: pd.DataFrame,
    fig: plt.Figure | None = None,
    host_subplot_spec=None,
) -> plt.Figure:
    sequence = _prepare_country_sequence(df)
    n_total = len(sequence)
    n_gap = sum(1 for _, gap, _ in sequence if gap)

    # ── Figure setup ──
    if fig is None:
        fig = plt.figure(figsize=(8.2, 5.8), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[1.0, 4.0, 0.45],
            hspace=0.20,
            left=0.04, right=0.98, top=0.95, bottom=0.06,
        )
        title_ax = fig.add_subplot(outer[0])
        body_spec = outer[1]
        footer_ax = fig.add_subplot(outer[2])
    else:
        assert host_subplot_spec is not None
        inner = GridSpecFromSubplotSpec(
            nrows=3, ncols=1,
            subplot_spec=host_subplot_spec,
            height_ratios=[1.0, 4.0, 0.45],
            hspace=0.20,
        )
        title_ax = fig.add_subplot(inner[0])
        body_spec = inner[1]
        footer_ax = fig.add_subplot(inner[2])

    # Sub-divide body: waffle (kiri) + legend (kanan)
    body_gs = GridSpecFromSubplotSpec(
        nrows=1, ncols=2,
        subplot_spec=body_spec,
        width_ratios=[3.0, 1.4],
        wspace=-0.05,
    )
    waffle_ax = fig.add_subplot(body_gs[0, 0])
    legend_ax = fig.add_subplot(body_gs[0, 1])

    # ── Title block ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.85,
        "Usia Pernikahan Anak, Gender, dan Pendapatan Negara",
        transform=title_ax.transAxes,
        family="serif", fontsize=14, weight=900, color=T.COLOR_HEADLINE,
        va="top",
    )
    title_ax.text(
        0.0, 0.42,
        f"Setiap kotak mewakili 1 negara.\n"
        f"Terdapat {n_gap} dari {n_total} negara (yang memiliki data lengkap) dengan kesenjangan.",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=10, color=T.COLOR_MUTED,
        va="top", linespacing=1.4,
    )

    # ── Waffle grid ──
    waffle_ax.set_xlim(-0.5, GRID_COLS - 0.5)
    waffle_ax.set_ylim(-0.5, GRID_ROWS - 0.5)
    waffle_ax.set_aspect("equal")
    waffle_ax.invert_yaxis()
    for spine in ["top", "right", "bottom", "left"]:
        waffle_ax.spines[spine].set_visible(False)
    waffle_ax.set_xticks([])
    waffle_ax.set_yticks([])

    cell_size = 0.86  # padding antar cells
    for idx, (inc, gap, country) in enumerate(sequence):
        row = idx // GRID_COLS
        col = idx % GRID_COLS
        if row >= GRID_ROWS:
            break  # safety
        color = WAFFLE_COLORS[(inc, gap)]
        rect = mpatches.Rectangle(
            (col - cell_size / 2, row - cell_size / 2),
            cell_size, cell_size,
            facecolor=color, edgecolor="none",
        )
        waffle_ax.add_patch(rect)

    # ── Legend (vertical, di sebelah kanan) ──
    legend_ax.axis("off")
    legend_entries = []
    for inc in INCOME_ORDER:
        legend_entries.append((inc, True, f"{inc}, ada gap"))
        legend_entries.append((inc, False, f"{inc}, tanpa gap"))

    n_entries = len(legend_entries)
    swatch_size = 0.10
    swatch_x = 0.05
    text_x = 0.22
    line_height = 0.92 / (n_entries + 1)

    for i, (inc, gap, label) in enumerate(legend_entries):
        y = 0.92 - (i + 1) * line_height
        color = WAFFLE_COLORS[(inc, gap)]
        legend_ax.add_patch(mpatches.Rectangle(
            (swatch_x, y - swatch_size / 2), swatch_size, swatch_size,
            facecolor=color, edgecolor="none",
            transform=legend_ax.transAxes,
        ))
        legend_ax.text(
            text_x, y, label,
            transform=legend_ax.transAxes,
            family="sans-serif", fontsize=9, color=T.COLOR_BODY,
            va="center", ha="left",
        )

    # ── Footer — sumber dihapus, sudah ada di footer poster utama
    footer_ax.axis("off")
    footer_ax.text(
        0.0, 0.6,
        f"Total {n_total} negara dengan data lengkap.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=8, color=T.COLOR_MUTED,
        va="center",
    )

    return fig


# ────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render Panel B standalone.")
    parser.add_argument("--data", default="data/world-cml-2023-cleaned.csv")
    parser.add_argument("--output", default="output/panel_b_preview.png")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()

    T.setup_matplotlib()
    T.register_local_fonts()

    df = pd.read_csv(args.data)
    fig = render_panel_b(df)

    fig.savefig(args.output, dpi=150, bbox_inches="tight",
                facecolor=T.COLOR_BG)
    print(f"[OK] PNG preview: {args.output}")

    if args.pdf:
        pdf_path = args.output.rsplit(".", 1)[0] + ".pdf"
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight",
                    facecolor=T.COLOR_BG)
        print(f"[OK] PDF vektor : {pdf_path}")
