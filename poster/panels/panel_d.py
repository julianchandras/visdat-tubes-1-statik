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

    # Title block diperbesar (1.4) supaya ada margin vertikal yang
    # cukup antara title dan subtitle. hspace antar tile diperbesar
    # supaya region title tidak overlap chart di atasnya.
    if fig is None:
        fig = plt.figure(figsize=(15.35, 4.5), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[1.4, 3.3, 0.4],
            hspace=0.55,
            left=0.04, right=0.98, top=0.95, bottom=0.06,
        )
        title_ax = fig.add_subplot(outer[0])
        grid_spec = GridSpecFromSubplotSpec(
            nrows=2, ncols=3,
            subplot_spec=outer[1],
            wspace=0.22, hspace=1.10,
        )
        footer_ax = fig.add_subplot(outer[2])
    else:
        assert host_subplot_spec is not None, \
            "host_subplot_spec wajib saat render ke canvas utama"
        inner = GridSpecFromSubplotSpec(
            nrows=3, ncols=1,
            subplot_spec=host_subplot_spec,
            height_ratios=[1.4, 3.3, 0.4],
            hspace=0.55,
        )
        title_ax = fig.add_subplot(inner[0])
        grid_spec = GridSpecFromSubplotSpec(
            nrows=2, ncols=3,
            subplot_spec=inner[1],
            wspace=0.22, hspace=1.10,
        )
        footer_ax = fig.add_subplot(inner[2])

    # ── Title & subtitle block — dengan margin vertikal jelas ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.92,
        "Perkembangan Perlindungan Hukum Selama Periode 1995 - 2023",
        transform=title_ax.transAxes,
        family="serif", fontsize=15, weight=900, color=T.COLOR_HEADLINE,
        va="top",
    )
    title_ax.text(
        0.0, 0.18,
        "Persentase negara dengan usia minimum pernikahan ≥ 18 (dengan izin orang tua), 1995 - 2023.",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=10, color=T.COLOR_MUTED,
        va="top",
    )

    # ── Grid 2×3 sparkline — STYLING UNIFORM untuk semua tile ──
    LINE_WIDTH = 1.0       # tipis supaya chart lebih jelas terbaca
    LINE_ALPHA = 0.95
    FILL_ALPHA = 0.18
    line_handles_for_legend = None
    for idx, region in enumerate(T.REGION_ORDER):
        row, col = divmod(idx, 3)
        ax = fig.add_subplot(grid_spec[row, col])
        data = series_by_region[region]

        # Filled gap area — uniform color & alpha
        ax.fill_between(
            data["year"], data["f_pct"], data["m_pct"],
            color=T.COLOR_FEMALE, alpha=FILL_ALPHA, linewidth=0,
        )

        # Lines — uniform width & alpha (label di line pertama untuk legend)
        m_line, = ax.plot(
            data["year"], data["m_pct"],
            color=T.COLOR_MALE, lw=LINE_WIDTH, alpha=LINE_ALPHA,
            solid_capstyle="round", label="Laki-laki",
        )
        f_line, = ax.plot(
            data["year"], data["f_pct"],
            color=T.COLOR_FEMALE, lw=LINE_WIDTH, alpha=LINE_ALPHA,
            solid_capstyle="round", label="Perempuan",
        )
        if line_handles_for_legend is None:
            line_handles_for_legend = (f_line, m_line)

        # Endpoint markers
        ax.plot([2023], [data["f_pct"].iloc[-1]],
                marker="o", ms=3.5, color=T.COLOR_FEMALE)
        ax.plot([2023], [data["m_pct"].iloc[-1]],
                marker="o", ms=3.5, color=T.COLOR_MALE)

        # Y-axis 0-100 konsisten
        ax.set_ylim(0, 105)
        ax.set_xlim(1995, 2023)

        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["0", "50", "100%"], fontsize=7, color=T.COLOR_MUTED)
        ax.set_xticks([1995, 2023])
        ax.set_xticklabels(["'95", "'23"], fontsize=7, color=T.COLOR_MUTED)

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(T.COLOR_GRIDLINE)
        ax.spines["bottom"].set_color(T.COLOR_GRIDLINE)
        ax.tick_params(length=2, width=0.5)

        # Region title — DI ATAS tile (loc top, pad besar), uniform color
        ax.set_title(
            region, loc="left", pad=6,
            family="serif", fontsize=11, weight=700,
            color=T.COLOR_HEADLINE,
        )

        # Gap annotation di ATAS chart (di luar y=100% area) — tidak
        # collide dengan endpoint line di mana pun. Pakai simbol ▲ (stock
        # up triangle) untuk gap positif, "parity" untuk gap = 0.
        f_2023 = data["f_pct"].iloc[-1]
        m_2023 = data["m_pct"].iloc[-1]
        gap = m_2023 - f_2023
        # Pakai family="sans-serif" (Source Sans 3) supaya glyph ▲ ter-render —
        # IBM Plex Mono tidak include U+25B2.
        gap_label = f"▲ {gap:.0f}pp" if gap > 0 else "kesetaraan"
        ax.text(
            1.0, 1.04, gap_label,
            transform=ax.transAxes,
            ha="right", va="bottom",
            family="sans-serif", fontsize=9, weight=600,
            color=T.COLOR_BODY,
        )

    # ── Footer: line chart legend (proper) + minor caption ──
    footer_ax.axis("off")
    if line_handles_for_legend is not None:
        f_line, m_line = line_handles_for_legend
        footer_ax.legend(
            handles=[f_line, m_line],
            loc="center left",
            bbox_to_anchor=(0.0, 0.5),
            ncol=2,
            frameon=False,
            fontsize=9,
            handlelength=2.0, handleheight=0.8,
            columnspacing=1.5,
            labelcolor=T.COLOR_BODY,
        )
    footer_ax.text(
        1.0, 0.5,
        f"Berdasarkan data dari {n_complete} negara pada periode 1995 - 2023.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=8, color=T.COLOR_MUTED,
        va="center", ha="right",
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
