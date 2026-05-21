"""Assemble seluruh panel ke canvas poster A2 (420x594mm portrait).

Layout mengikuti blueprint docs-system-development/spec_desain.md bagian 2.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from poster import theme as T
from poster.panels import panel_a, panel_b, panel_c, panel_d


# A3 portrait (revisi tim, sebelumnya A2)
# 1 inch = 25.4 mm. A3 = 297 x 420 mm
A2_WIDTH_INCH = 297 / 25.4    # 11.693
A2_HEIGHT_INCH = 420 / 25.4   # 16.535


# Proporsi tinggi per block (dalam mm, akan dinormalisasi ke rasio).
# Total ≈ 410 mm + ~10mm margin = 420mm A3 height.
HEIGHT_RATIOS_MM = {
    "header":    105,
    "panel_a":   150,
    "middle":    100,
    "panel_d":   65,
    "footer":    25,
}


def render_header(
    fig: plt.Figure, host_subplot_spec, df: pd.DataFrame,
) -> None:
    """Header: 2 baris. Row 1 = title + subtitle. Row 2 = 3 hook stat."""
    inner = GridSpecFromSubplotSpec(
        nrows=2, ncols=1,
        subplot_spec=host_subplot_spec,
        height_ratios=[2.3, 1.3],
        hspace=0.12,
    )
    title_ax = fig.add_subplot(inner[0])
    stats_spec = inner[1]

    # ── Row 1: Title + subtitle multi-line ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.95,
        "Tidak Semua Negara Melindungi Anak\ndari Pernikahan Dini!",
        transform=title_ax.transAxes,
        family="serif", fontsize=32, weight=900,
        color=T.COLOR_HEADLINE,
        ha="left", va="top", linespacing=0.95,
    )
    title_ax.text(
        0.0, 0.05,
        "Berdasarkan data 193 negara anggota PBB yang diperoleh dari WORLD Policy Analysis Center.\n"
        "Pernikahan yang dikategorikan sebagai pernikahan anak adalah pernikahan dengan usia salah satu pasangan di bawah usia 18 tahun.\n"
        "Kesenjangan (gap) adalah perbedaan usia minimum pernikahan antargender.",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=10, weight=400, style="italic",
        color=T.COLOR_BODY,
        ha="left", va="bottom", linespacing=1.45,
    )

    # ── Row 2: Stats bar (3 hook stat baru) ──
    # X = negara yang minage_fem_any != 5 (masih mengizinkan <18 via any path)
    n_under18 = int(((df["minage_fem_any"] != 5) & df["minage_fem_any"].notna()).sum())
    n_loop_fem = int(df["has_loophole_fem"].sum())
    n_worst = int((df["loop_summ"] == 1).sum())

    stats_gs = GridSpecFromSubplotSpec(
        nrows=1, ncols=3,
        subplot_spec=stats_spec,
        width_ratios=[1.0, 1.0, 1.0],
        wspace=0.08,
    )

    # 3 hook stat baru (revisi tim):
    # - X (under18): masih mengizinkan pernikahan anak <18 tahun
    # - 55 (loophole): ada celah hukum
    # - 26 (≤13): ada path nikah ≤13 tahun
    stats = [
        (n_under18,
         "negara masih mengizinkan\npernikahan anak di bawah\nusia 18 tahun",
         T.LOOP_SUMM_COLORS[2.0],
         "#FBE3E3"),
        (n_loop_fem,
         "negara masih memiliki celah\nhukum yang mengizinkan anak\nperempuan menikah di bawah\nusia legal",
         T.COLOR_ACCENT,
         "#FFEFE6"),
        (n_worst,
         "negara masih mengizinkan\npernikahan anak perempuan\nberusia 13 tahun atau\nlebih muda",
         T.LOOP_SUMM_COLORS[1.0],
         "#F8E1E1"),
    ]

    for col, (value, label, color, bg_tint) in enumerate(stats):
        ax = fig.add_subplot(stats_gs[0, col])
        ax.axis("off")
        # Subtle tinted background box untuk highlight number
        ax.add_patch(plt.Rectangle(
            (0.02, 0.05), 0.96, 0.90,
            transform=ax.transAxes,
            facecolor=bg_tint, edgecolor="none",
            zorder=0,
        ))
        # SIDE-BY-SIDE layout: number kiri (vertical center), label kanan
        # (vertical center, multi-line). Tidak ada lagi overlap karena
        # ada di kolom horizontal yang berbeda.
        ax.text(
            0.06, 0.55, str(value),
            transform=ax.transAxes,
            family="serif", fontsize=52, weight=900,
            color=color,
            ha="left", va="center",
            zorder=1,
        )
        ax.text(
            0.42, 0.55, label,
            transform=ax.transAxes,
            family="sans-serif", fontsize=8.5, weight=500,
            color=T.COLOR_BODY,
            ha="left", va="center", linespacing=1.35,
            zorder=1,
        )


def render_footer(
    fig: plt.Figure, host_subplot_spec, df: pd.DataFrame,
) -> None:
    """Footer: source + team credit."""
    ax = fig.add_subplot(host_subplot_spec)
    ax.axis("off")

    n = len(df)
    ax.text(
        0.0, 0.90,
        f"Dataset: WORLD Policy Analysis Center, Child Marriage Laws 2023. "
        f"DOI: 10.25828/v8s6-jz31 · Lisensi CC-BY-SA · {n} negara anggota PBB.",
        transform=ax.transAxes,
        family="sans-serif", fontsize=11, weight=600,
        color=T.COLOR_BODY,
        va="top",
    )
    ax.text(
        0.0, 0.58,
        "Analisis & visualisasi: Kelompok 11 IF4061 Visualisasi Data · "
        "Institut Teknologi Bandung, Semester 2 2025/2026.",
        transform=ax.transAxes,
        family="sans-serif", fontsize=10, weight=400,
        color=T.COLOR_MUTED,
        va="top",
    )
    ax.text(
        0.0, 0.25,
        "Tim: Eduardus Alvito Kristiadi (13522004) · "
        "Bryan Cornelius Lauwrence (13522033) · "
        "Kharris Khisunica (13522051) · "
        "Devinzen (13522064) · "
        "Julian Chandra Sutadi (13522080).",
        transform=ax.transAxes,
        family="sans-serif", fontsize=9, weight=400,
        color=T.COLOR_MUTED,
        va="top",
    )


def compose_poster(df: pd.DataFrame) -> plt.Figure:
    """Render seluruh poster ke satu Figure A2."""
    fig = plt.figure(
        figsize=(A2_WIDTH_INCH, A2_HEIGHT_INCH),
        dpi=150,
    )

    main_gs = GridSpec(
        nrows=5, ncols=1,
        figure=fig,
        height_ratios=[
            HEIGHT_RATIOS_MM["header"],
            HEIGHT_RATIOS_MM["panel_a"],
            HEIGHT_RATIOS_MM["middle"],
            HEIGHT_RATIOS_MM["panel_d"],
            HEIGHT_RATIOS_MM["footer"],
        ],
        hspace=0.08,
        left=0.036, right=0.964, top=0.975, bottom=0.025,
    )

    render_header(fig, main_gs[0], df)
    panel_a.render_panel_a(df, fig=fig, host_subplot_spec=main_gs[1])

    middle_gs = GridSpecFromSubplotSpec(
        nrows=1, ncols=2,
        subplot_spec=main_gs[2],
        width_ratios=[1.0, 1.0],
        wspace=0.12,
    )
    panel_b.render_panel_b(df, fig=fig, host_subplot_spec=middle_gs[0, 0])
    panel_c.render_panel_c(df, fig=fig, host_subplot_spec=middle_gs[0, 1])

    panel_d.render_panel_d(df, fig=fig, host_subplot_spec=main_gs[3])
    render_footer(fig, main_gs[4], df)

    return fig


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compose poster A2 final.")
    parser.add_argument("--data", default="data/world-cml-2023-cleaned.csv")
    parser.add_argument("--output", default="output/poster_a2_final.pdf")
    parser.add_argument("--png", action="store_true")
    args = parser.parse_args()

    T.setup_matplotlib()
    T.register_local_fonts()

    df = pd.read_csv(args.data)

    print(f"[INFO] Composing A2 poster ({A2_WIDTH_INCH:.2f} x {A2_HEIGHT_INCH:.2f} inch)...")
    fig = compose_poster(df)

    # NO bbox_inches="tight" — supaya output exact A3 dimensions tanpa
    # crop asimetris yang bisa shift content horizontal off-center.
    fig.savefig(args.output, format="pdf", facecolor=T.COLOR_BG)
    print(f"[OK] PDF vektor : {args.output}")

    if args.png:
        png_path = args.output.rsplit(".", 1)[0] + ".png"
        fig.savefig(png_path, format="png", dpi=120,
                    facecolor=T.COLOR_BG)
        print(f"[OK] PNG preview: {png_path}")
