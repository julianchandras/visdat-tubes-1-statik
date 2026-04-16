"""Panel B — Beeswarm: Economic × Gender × Minimum Age.

Dot plot per negara × gender pada grid (wb_econ × minage_loop). Menunjukkan
sebaran negara dan menyoroti gender gap via connector line antara dot F (merah)
dan M (biru) yang berbeda posisi Y.

Selaras dengan docs-system-development/spec_desain.md bagian 5.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

from poster import theme as T


# ────────────────────────────────────────────────────────────
# Konstanta mapping
# ────────────────────────────────────────────────────────────

# Kode minage_loop → posisi y di chart
# Gap visual 1 unit antara kode 3 (16-17) dan kode 5 (>=18) untuk mencerminkan
# non-linearitas skala. Kode 9 (Unknown) di track terpisah, di atas separator.
CODE_TO_Y = {
    1.0: 0.0,   # <=13 (terburuk)
    2.0: 1.0,   # 14-15
    3.0: 2.0,   # 16-17
    5.0: 3.5,   # >=18 (gap sengaja, mencerminkan lompatan 2 tahun)
    9.0: 5.5,   # Unknown (track terpisah)
}
Y_SEPARATOR = 4.5   # garis horizontal pemisah antara main track & Unknown track

Y_LABELS = {
    0.0: "≤ 13 tahun",
    1.0: "14–15",
    2.0: "16–17",
    3.5: "≥ 18 tahun",
    5.5: "Unknown\n(adat/agama)",
}

# Income group → posisi x (pusat kolom)
INCOME_X = {
    "Low-income":    0.0,
    "Middle-income": 1.0,
    "High-income":   2.0,
}

# Offset dalam kolom: F di kiri, M di kanan
SUB_OFFSET_F = -0.18
SUB_OFFSET_M = +0.18
JITTER_RANGE = 0.12   # range horizontal per dot dalam sub-column

DOT_SIZE = 42


def _apply_jitter(n: int, rng: np.random.Generator) -> np.ndarray:
    """Return n nilai jitter uniform dalam [-JITTER_RANGE, +JITTER_RANGE]."""
    return rng.uniform(-JITTER_RANGE, JITTER_RANGE, size=n)


def _prepare_data(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Filter & tambah kolom x_f, x_m, y_f, y_m untuk plotting."""
    sub = df.dropna(subset=[
        "wb_econ_label", "minage_fem_loop", "minage_mal_loop",
    ]).copy()
    sub = sub[sub["wb_econ_label"].isin(INCOME_X)]

    sub["x_base"] = sub["wb_econ_label"].map(INCOME_X)

    # Jitter independent per-row per-gender
    sub["jit_f"] = _apply_jitter(len(sub), rng)
    sub["jit_m"] = _apply_jitter(len(sub), rng)

    sub["x_f"] = sub["x_base"] + SUB_OFFSET_F + sub["jit_f"]
    sub["x_m"] = sub["x_base"] + SUB_OFFSET_M + sub["jit_m"]
    sub["y_f"] = sub["minage_fem_loop"].map(CODE_TO_Y)
    sub["y_m"] = sub["minage_mal_loop"].map(CODE_TO_Y)

    sub["has_gap"] = sub["minage_fem_loop"] != sub["minage_mal_loop"]
    return sub


# Negara highlight untuk annotation (dipilih dari kasus dramatic)
HIGHLIGHT_COUNTRIES = {
    "Singapore": {
        "label": "Singapore",
        "note":  "Negara high-income,\nperempuan bisa nikah ≤ 13",
        "xy_offset_f": (50, 40),
        "xy_offset_m": (0, 0),
    },
    "Equatorial Guinea": {
        "label": "Equatorial Guinea",
        "note":  "Laki-laki dikodekan\nUnknown (adat/agama)",
        "xy_offset_f": (-10, 55),
        "xy_offset_m": (0, 0),
    },
}


def render_panel_b(
    df: pd.DataFrame,
    fig: plt.Figure | None = None,
    host_subplot_spec=None,
    random_seed: int = 42,
) -> plt.Figure:
    rng = np.random.default_rng(random_seed)
    plot_df = _prepare_data(df, rng)
    n_gap = int(plot_df["has_gap"].sum())
    n_total = len(plot_df)

    if fig is None:
        fig = plt.figure(figsize=(8.2, 5.8), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[1.0, 3.5, 0.55],
            hspace=0.30,
            left=0.09, right=0.98, top=0.95, bottom=0.06,
        )
        title_ax = fig.add_subplot(outer[0])
        ax = fig.add_subplot(outer[1])
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
        ax = fig.add_subplot(inner[1])
        footer_ax = fig.add_subplot(inner[2])

    # ── Title block ──
    title_ax.axis("off")
    title_ax.text(
        0.0, 0.75, "DI BALIK PETA — GENDER GAP PER KELAS EKONOMI",
        transform=title_ax.transAxes,
        family="serif", fontsize=20, weight=900, color=T.COLOR_HEADLINE,
    )
    title_ax.text(
        0.0, 0.18,
        f"Setiap dot = 1 negara. Garis abu-abu menghubungkan posisi perempuan vs laki-laki "
        f"di {n_gap} negara dengan gender gap.",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=11, color=T.COLOR_MUTED,
    )

    # ── Connector lines (gender gap countries) ──
    gap_df = plot_df[plot_df["has_gap"]]
    for _, row in gap_df.iterrows():
        ax.plot(
            [row["x_f"], row["x_m"]],
            [row["y_f"], row["y_m"]],
            color=T.COLOR_MUTED, alpha=0.45, lw=0.8,
            zorder=1,
        )

    # ── Dots female ──
    ax.scatter(
        plot_df["x_f"], plot_df["y_f"],
        s=DOT_SIZE, c=T.COLOR_FEMALE,
        edgecolors="white", linewidths=0.6,
        alpha=0.85, zorder=3,
        label="Perempuan",
    )
    # ── Dots male ──
    ax.scatter(
        plot_df["x_m"], plot_df["y_m"],
        s=DOT_SIZE, c=T.COLOR_MALE,
        edgecolors="white", linewidths=0.6,
        alpha=0.85, zorder=3,
        label="Laki-laki",
    )

    # ── Separator line (main track ↔ Unknown track) ──
    ax.axhline(
        Y_SEPARATOR, color=T.COLOR_GRIDLINE, lw=0.8,
        linestyle="--", zorder=0,
    )

    # ── Axis ticks & labels ──
    ax.set_yticks(list(Y_LABELS.keys()))
    ax.set_yticklabels(list(Y_LABELS.values()), fontsize=10,
                        color=T.COLOR_BODY, family="sans-serif")
    ax.set_xticks(list(INCOME_X.values()))
    ax.set_xticklabels(list(INCOME_X.keys()), fontsize=11,
                        color=T.COLOR_HEADLINE, family="sans-serif",
                        weight=600)

    # Y-axis header — rotated vertical di sisi luar kiri
    ax.text(
        -0.02, 0.98, "Usia minimum pernikahan (dengan celah)  ↓",
        transform=ax.transAxes,
        family="sans-serif", fontsize=9, color=T.COLOR_MUTED,
        ha="left", va="bottom", weight=600,
    )

    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(-0.7, 6.2)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(T.COLOR_GRIDLINE)
    ax.spines["bottom"].set_color(T.COLOR_GRIDLINE)
    ax.tick_params(length=2, width=0.5)

    # Subtle horizontal gridlines di main track
    for y in [0.0, 1.0, 2.0, 3.5]:
        ax.axhline(y, color=T.COLOR_GRIDLINE, lw=0.3, alpha=0.5, zorder=0)

    # ── Annotation negara highlight ──
    for country, meta in HIGHLIGHT_COUNTRIES.items():
        rows = plot_df[plot_df["country"] == country]
        if rows.empty:
            continue
        row = rows.iloc[0]
        # Lingkaran pembeda di sekitar dot F
        ax.scatter(
            row["x_f"], row["y_f"],
            s=DOT_SIZE * 3, facecolors="none",
            edgecolors=T.COLOR_ACCENT, linewidths=1.5,
            zorder=4,
        )
        # Label callout
        ax.annotate(
            f"{meta['label']}\n{meta['note']}",
            xy=(row["x_f"], row["y_f"]),
            xytext=meta["xy_offset_f"], textcoords="offset points",
            fontsize=8, color=T.COLOR_HEADLINE, weight=600,
            ha="center", family="sans-serif",
            arrowprops=dict(
                arrowstyle="-", color=T.COLOR_ACCENT,
                lw=0.7, shrinkA=2, shrinkB=4,
            ),
        )

    # ── Legend — di luar chart area supaya tidak overlap data ──
    legend = ax.legend(
        loc="upper right", bbox_to_anchor=(1.0, 1.08),
        frameon=False, fontsize=10, handletextpad=0.3,
        ncol=2, columnspacing=1.2,
        labelcolor=T.COLOR_BODY,
    )
    for handle in legend.legend_handles:
        handle.set_alpha(1.0)

    # ── Footer caption ──
    footer_ax.axis("off")
    footer_ax.text(
        0.0, 0.75,
        f"Total {n_total} negara dengan data lengkap. Jitter horizontal ditambahkan "
        f"untuk mengurangi tumpang-tindih dot.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=9, color=T.COLOR_MUTED,
        va="top",
    )
    footer_ax.text(
        0.0, 0.25,
        "Sumber: WORLD Policy Analysis Center, Child Marriage Laws 2023.",
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
