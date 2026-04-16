"""Panel D — Small multiples sparkline per region (1995-2023).

Menunjukkan tren % negara dengan usia minimum pernikahan >=18 (parental
consent), perempuan vs laki-laki, per 6 region. Highlight outlier
(East Asia stagnan, Europe parity) sebagai counter-narrative.

Selaras dengan docs-system-development/spec_desain.md bagian 7.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from poster import theme as T


YEARS = list(range(1995, 2024))
F_COLS = [f"minage_par_18_f_{y}" for y in YEARS]
M_COLS = [f"minage_par_18_m_{y}" for y in YEARS]


def _compute_region_series(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Untuk tiap region, hitung % negara dengan value=1 per tahun (F & M)."""
    out = {}
    for region in T.REGION_ORDER:
        sub = df[df["region"] == region]
        rows = []
        for year, fc, mc in zip(YEARS, F_COLS, M_COLS):
            n_f = sub[fc].notna().sum()
            n_m = sub[mc].notna().sum()
            f_pct = (sub[fc] == 1).sum() / n_f * 100 if n_f else np.nan
            m_pct = (sub[mc] == 1).sum() / n_m * 100 if n_m else np.nan
            rows.append({"year": year, "f_pct": f_pct, "m_pct": m_pct})
        out[region] = pd.DataFrame(rows)
    return out


def _count_complete_countries(df: pd.DataFrame) -> int:
    """Jumlah negara dengan data F lengkap 1995-2023."""
    return int(df[F_COLS].notna().all(axis=1).sum())


def render_panel_d(
    df: pd.DataFrame,
    fig: plt.Figure | None = None,
    host_subplot_spec=None,
) -> plt.Figure:
    """Render Panel D ke figure baru (standalone) atau ke subplot host.

    Parameters
    ----------
    df : DataFrame dataset cleaned.
    fig : Figure, kalau None buat figure standalone (untuk testing panel).
    host_subplot_spec : SubplotSpec, kalau diberikan render di dalam canvas
        poster utama.

    Returns
    -------
    Figure yang berisi panel.
    """
    series_by_region = _compute_region_series(df)
    n_complete = _count_complete_countries(df)

    # Standalone mode — ukuran proporsional Panel D di A2 (lebar 390mm × tinggi 54mm)
    # tambah ruang untuk title + footnote
    if fig is None:
        fig = plt.figure(figsize=(15.35, 4.5), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[0.8, 3.2, 0.5],
            hspace=0.35,
            left=0.04, right=0.98, top=0.95, bottom=0.06,
        )
        title_ax = fig.add_subplot(outer[0])
        grid_spec = GridSpecFromSubplotSpec(
            nrows=2, ncols=3,
            subplot_spec=outer[1],
            wspace=0.20, hspace=0.55,
        )
        footer_ax = fig.add_subplot(outer[2])
    else:
        assert host_subplot_spec is not None, \
            "host_subplot_spec wajib saat render ke canvas utama"
        inner = GridSpecFromSubplotSpec(
            nrows=3, ncols=1,
            subplot_spec=host_subplot_spec,
            height_ratios=[0.8, 3.2, 0.5],
            hspace=0.35,
        )
        title_ax = fig.add_subplot(inner[0])
        grid_spec = GridSpecFromSubplotSpec(
            nrows=2, ncols=3,
            subplot_spec=inner[1],
            wspace=0.20, hspace=0.55,
        )
        footer_ax = fig.add_subplot(inner[2])

    # ── Title & subtitle block ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.85, "28 TAHUN PROGRES — TIDAK SEMUA DUNIA BERGERAK SAMA",
        transform=title_ax.transAxes,
        family="serif", fontsize=18, weight=700, color=T.COLOR_HEADLINE,
    )
    title_ax.text(
        0.0, 0.10,
        "% negara dengan usia minimum pernikahan >= 18 dengan parental consent, 1995 → 2023",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=11, color=T.COLOR_MUTED,
    )

    # ── Grid 2×3 sparkline ──
    for idx, region in enumerate(T.REGION_ORDER):
        row, col = divmod(idx, 3)
        ax = fig.add_subplot(grid_spec[row, col])
        data = series_by_region[region]

        highlight = T.REGION_HIGHLIGHT.get(region)
        is_highlighted = highlight is not None

        # Line width lebih tebal kalau highlighted
        lw_f = 2.2 if is_highlighted else 1.5
        lw_m = 2.2 if is_highlighted else 1.5
        alpha_main = 1.0 if is_highlighted else 0.75

        # Filled gap area antara F dan M
        fill_color = T.COLOR_FEMALE
        fill_alpha = 0.22 if is_highlighted else 0.12
        ax.fill_between(
            data["year"], data["f_pct"], data["m_pct"],
            color=fill_color, alpha=fill_alpha, linewidth=0,
        )

        # Lines
        ax.plot(
            data["year"], data["m_pct"],
            color=T.COLOR_MALE, lw=lw_m, alpha=alpha_main,
            solid_capstyle="round",
        )
        ax.plot(
            data["year"], data["f_pct"],
            color=T.COLOR_FEMALE, lw=lw_f, alpha=alpha_main,
            solid_capstyle="round",
        )

        # Endpoint marker
        ax.plot([2023], [data["f_pct"].iloc[-1]],
                marker="o", ms=4, color=T.COLOR_FEMALE, alpha=alpha_main)
        ax.plot([2023], [data["m_pct"].iloc[-1]],
                marker="o", ms=4, color=T.COLOR_MALE, alpha=alpha_main)

        # Y-axis 0-100 konsisten
        ax.set_ylim(0, 100)
        ax.set_xlim(1995, 2023)

        # Tick minimalis
        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["0", "50", "100%"], fontsize=8, color=T.COLOR_MUTED)
        ax.set_xticks([1995, 2023])
        ax.set_xticklabels(["'95", "'23"], fontsize=8, color=T.COLOR_MUTED)

        # Spine minimalis
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(T.COLOR_GRIDLINE)
        ax.spines["bottom"].set_color(T.COLOR_GRIDLINE)
        ax.tick_params(length=2, width=0.5)

        # Region title + gap 2023
        f_2023 = data["f_pct"].iloc[-1]
        m_2023 = data["m_pct"].iloc[-1]
        gap = m_2023 - f_2023

        title_color = highlight if is_highlighted else T.COLOR_HEADLINE
        ax.set_title(
            region, loc="left", pad=8,
            family="serif", fontsize=12, weight=700,
            color=title_color,
        )
        # Gap annotation kanan atas
        gap_label = f"gap +{gap:.0f}pp" if gap > 0 else "gender parity"
        ax.text(
            0.98, 0.97, gap_label,
            transform=ax.transAxes,
            ha="right", va="top",
            family="monospace", fontsize=9,
            color=highlight if is_highlighted else T.COLOR_BODY,
            weight="bold" if is_highlighted else "normal",
        )

        # Endpoint label 2023 (angka persentase) — hanya untuk highlighted
        if is_highlighted:
            ax.annotate(
                f"F {f_2023:.0f}%",
                xy=(2023, f_2023),
                xytext=(4, -2), textcoords="offset points",
                fontsize=8, color=T.COLOR_FEMALE, weight=600,
                ha="left", va="top",
            )
            ax.annotate(
                f"M {m_2023:.0f}%",
                xy=(2023, m_2023),
                xytext=(4, 2), textcoords="offset points",
                fontsize=8, color=T.COLOR_MALE, weight=600,
                ha="left", va="bottom",
            )

    # ── Footer caption ──
    footer_ax.axis("off")
    footer_caption = (
        f"Merah = perempuan, biru = laki-laki, area berwarna = gender gap. "
        f"Berdasarkan {n_complete} negara dengan data lengkap 1995-2023. "
        f"Sumber: WORLD Policy Analysis Center, Child Marriage Laws 2023."
    )
    footer_ax.text(
        0.0, 0.5, footer_caption,
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=8, color=T.COLOR_MUTED,
        va="center",
    )

    return fig


# ────────────────────────────────────────────────────────────
# CLI untuk render standalone preview
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render Panel D standalone.")
    parser.add_argument(
        "--data", default="data/world-cml-2023-cleaned.csv",
        help="Path CSV dataset cleaned.",
    )
    parser.add_argument(
        "--output", default="output/panel_d_preview.png",
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
    fig = render_panel_d(df)

    fig.savefig(args.output, dpi=150, bbox_inches="tight",
                facecolor=T.COLOR_BG)
    print(f"[OK] PNG preview: {args.output}")

    if args.pdf:
        pdf_path = args.output.rsplit(".", 1)[0] + ".pdf"
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight",
                    facecolor=T.COLOR_BG)
        print(f"[OK] PDF vektor : {pdf_path}")
