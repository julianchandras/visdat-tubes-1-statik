"""Panel A — Hero choropleth dunia: `loop_summ`.

Peta dunia menunjukkan kualitas perlindungan hukum per negara, di mana
`loop_summ` sudah composite (mencakup gender parity + minage_loop). 5 kategori
diskrit sequential red (makin merah makin buruk) + abu-abu hatched untuk
Unknown (hukum adat/agama).

Selaras dengan docs-system-development/spec_desain.md bagian 4.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from pathlib import Path

import geopandas as gpd

from poster import theme as T


# ────────────────────────────────────────────────────────────
# Konstanta
# ────────────────────────────────────────────────────────────

SHAPEFILE_PATH = Path("poster/geo/ne_50m_admin_0_countries.shp")

# Label untuk setiap kode loop_summ di legend
LOOP_SUMM_LABELS = {
    5.0: "Parity + usia ≥ 18",
    3.0: "1 masalah: inequality atau usia 14-17",
    2.0: "2 masalah: inequality DAN usia 14-17",
    1.0: "Bisa nikah ≤ 13 tahun",
    9.0: "Unknown (hukum adat/agama)",
}
LEGEND_ORDER = [5.0, 3.0, 2.0, 1.0, 9.0]


# Equal Earth projection (EPSG:8857) — equal-area modern, tidak mendistorsi ukuran
EQUAL_EARTH_CRS = "EPSG:8857"


# Negara untuk callout — dipilih yang dramatic (loop_summ=1 + high-income)
HIGHLIGHT_COUNTRIES = {
    "GRC": {
        "label": "Yunani",
        "note":  "Satu-satunya negara\nEropa dengan kode 1",
        "xy_offset": (40, 80),
    },
    "SAU": {
        "label": "Arab Saudi",
        "note":  "Negara high-income\nmengizinkan ≤ 13",
        "xy_offset": (70, -60),
    },
    "SGP": {
        "label": "Singapura",
        "note":  "High-income dengan\ngender gap ekstrem",
        "xy_offset": (85, -20),
    },
}


# ────────────────────────────────────────────────────────────
# Data loading & join
# ────────────────────────────────────────────────────────────

def _load_world_with_data(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Load Natural Earth 50m + join dengan dataset child marriage.

    Primary join: ADM0_A3. Patch untuk South Sudan (NE pakai SDS, UN pakai SSD).
    """
    if not SHAPEFILE_PATH.exists():
        raise FileNotFoundError(
            f"Shapefile tidak ditemukan di {SHAPEFILE_PATH}. "
            "Jalankan: python -m poster.geo.download_naturalearth"
        )

    world = gpd.read_file(SHAPEFILE_PATH)

    # Manual patch South Sudan (NE: SDS → UN: SSD)
    world.loc[world["NAME"] == "S. Sudan", "ADM0_A3"] = "SSD"

    # Drop Antarctica dari tampilan
    world = world[world["ADM0_A3"] != "ATA"].copy()

    # Merge data via ADM0_A3 ↔ iso3
    merged = world.merge(
        df[["iso3", "country", "loop_summ", "wb_econ_label", "region"]],
        left_on="ADM0_A3", right_on="iso3",
        how="left",  # keep semua negara NE, data NaN untuk yang tidak ada
    )
    return merged


# ────────────────────────────────────────────────────────────
# Render
# ────────────────────────────────────────────────────────────

def render_panel_a(
    df: pd.DataFrame,
    fig: plt.Figure | None = None,
    host_subplot_spec=None,
) -> plt.Figure:
    world = _load_world_with_data(df)

    # Reproject ke Equal Earth
    world = world.to_crs(EQUAL_EARTH_CRS)

    # Figure setup
    if fig is None:
        fig = plt.figure(figsize=(14.5, 8.5), dpi=150)
        outer = GridSpec(
            nrows=3, ncols=1,
            figure=fig,
            height_ratios=[1.0, 7.0, 0.8],
            hspace=0.02,
            left=0.02, right=0.98, top=0.98, bottom=0.03,
        )
        title_ax = fig.add_subplot(outer[0])
        map_ax = fig.add_subplot(outer[1])
        footer_ax = fig.add_subplot(outer[2])
    else:
        assert host_subplot_spec is not None
        inner = GridSpecFromSubplotSpec(
            nrows=3, ncols=1,
            subplot_spec=host_subplot_spec,
            height_ratios=[1.0, 7.0, 0.8],
            hspace=0.02,
        )
        title_ax = fig.add_subplot(inner[0])
        map_ax = fig.add_subplot(inner[1])
        footer_ax = fig.add_subplot(inner[2])

    # ── Title block ──
    title_ax.axis("off")
    title_ax.text(
        0.5, 0.65, "PETA KETIDAKADILAN HUKUM",
        transform=title_ax.transAxes,
        family="serif", fontsize=34, weight=900,
        color=T.COLOR_HEADLINE,
        ha="center", va="center",
    )
    title_ax.text(
        0.5, 0.15,
        "Apakah hukum negara melindungi anak perempuan dari pernikahan dini? "
        "Kode gabungan usia minimum dan kesetaraan gender — 193 negara anggota PBB.",
        transform=title_ax.transAxes,
        family="sans-serif", fontsize=13, color=T.COLOR_MUTED,
        ha="center", va="center",
    )

    # ── Base layer: no-data / non-UN countries ──
    no_data = world[world["loop_summ"].isna()]
    no_data.plot(
        ax=map_ax,
        color=T.NO_DATA_COLOR,
        edgecolor="white", linewidth=0.6,
    )

    # ── Kategori non-Unknown (ordinal 1/2/3/5) ──
    for code in [5.0, 3.0, 2.0, 1.0]:
        sub = world[world["loop_summ"] == code]
        if sub.empty:
            continue
        sub.plot(
            ax=map_ax,
            color=T.LOOP_SUMM_COLORS[code],
            edgecolor="white", linewidth=0.6,
        )

    # ── Kategori Unknown (kode 9) dengan hatched pattern ──
    unknown = world[world["loop_summ"] == 9.0]
    if not unknown.empty:
        unknown.plot(
            ax=map_ax,
            color=T.LOOP_SUMM_COLORS[9.0],
            edgecolor="white", linewidth=0.6,
            hatch=T.UNKNOWN_HATCH,
        )

    # ── Map axes styling ──
    map_ax.set_aspect("equal")
    map_ax.set_axis_off()
    map_ax.set_facecolor(T.COLOR_BG)

    # Trim whitespace di atas/bawah kutub
    minx, miny, maxx, maxy = world.total_bounds
    map_ax.set_xlim(minx, maxx)
    # Trim 8% dari atas (Antartika sudah di-drop, tapi sisa padding polar)
    height = maxy - miny
    map_ax.set_ylim(miny + height * 0.02, maxy - height * 0.05)

    # ── Annotation callouts ──
    for iso3, meta in HIGHLIGHT_COUNTRIES.items():
        rows = world[world["ADM0_A3"] == iso3]
        if rows.empty:
            continue
        # Gunakan representative_point (label-safe) atau centroid
        country_geom = rows.geometry.iloc[0]
        if country_geom is None or country_geom.is_empty:
            continue
        try:
            cx, cy = country_geom.representative_point().coords[0]
        except Exception:
            cx, cy = country_geom.centroid.coords[0]

        # Lingkaran highlight
        map_ax.scatter(
            cx, cy, s=180, facecolors="none",
            edgecolors=T.COLOR_ACCENT, linewidths=1.8, zorder=5,
        )

        # Annotation
        map_ax.annotate(
            f"{meta['label']}\n{meta['note']}",
            xy=(cx, cy),
            xytext=meta["xy_offset"], textcoords="offset points",
            fontsize=10, color=T.COLOR_HEADLINE, weight=600,
            ha="center", family="sans-serif",
            arrowprops=dict(
                arrowstyle="-",
                color=T.COLOR_ACCENT,
                lw=0.9, shrinkA=6, shrinkB=8,
                connectionstyle="arc3,rad=0.15",
            ),
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=T.COLOR_BG, edgecolor="none",
                alpha=0.9,
            ),
            zorder=6,
        )

    # ── Legend ──
    legend_patches = []
    for code in LEGEND_ORDER:
        color = T.LOOP_SUMM_COLORS[code]
        label = LOOP_SUMM_LABELS[code]
        hatch = T.UNKNOWN_HATCH if code == 9.0 else None
        patch = mpatches.Patch(
            facecolor=color, edgecolor="white", linewidth=0.5,
            hatch=hatch, label=label,
        )
        legend_patches.append(patch)
    # Tambah no-data patch
    legend_patches.append(
        mpatches.Patch(
            facecolor=T.NO_DATA_COLOR, edgecolor="white",
            linewidth=0.5, label="Tidak ada data",
        )
    )

    legend = map_ax.legend(
        handles=legend_patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.01),
        ncol=3,
        frameon=False,
        fontsize=10,
        handlelength=1.8, handleheight=1.1,
        columnspacing=1.5,
        labelcolor=T.COLOR_BODY,
    )
    legend.set_title(
        "Kualitas perlindungan hukum terhadap pernikahan dini:",
        prop={"family": "sans-serif", "size": 10, "weight": 700},
    )
    legend.get_title().set_color(T.COLOR_HEADLINE)

    # ── Footer caption ──
    footer_ax.axis("off")
    counts = df["loop_summ"].value_counts().to_dict()
    n_parity = int(counts.get(5.0, 0))
    n_worst = int(counts.get(1.0, 0))
    footer_ax.text(
        0.5, 0.75,
        f"Dari 193 negara UN: {n_parity} sudah mencapai parity + usia ≥ 18, "
        f"namun {n_worst} masih mengizinkan pernikahan anak perempuan ≤ 13 tahun.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=10, color=T.COLOR_ACCENT,
        weight=600, ha="center", va="top",
    )
    footer_ax.text(
        0.5, 0.25,
        "Proyeksi: Equal Earth (equal-area). "
        "Sumber: WORLD Policy Analysis Center, Child Marriage Laws 2023. "
        "Batas negara: Natural Earth 50m.",
        transform=footer_ax.transAxes,
        family="sans-serif", fontsize=8, color=T.COLOR_MUTED,
        ha="center", va="top",
    )

    return fig


# ────────────────────────────────────────────────────────────
# CLI untuk render standalone preview
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render Panel A standalone.")
    parser.add_argument("--data", default="data/world-cml-2023-cleaned.csv")
    parser.add_argument("--output", default="output/panel_a_preview.png")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()

    T.setup_matplotlib()
    T.register_local_fonts()

    df = pd.read_csv(args.data)
    fig = render_panel_a(df)

    fig.savefig(args.output, dpi=150, bbox_inches="tight",
                facecolor=T.COLOR_BG)
    print(f"[OK] PNG preview: {args.output}")

    if args.pdf:
        pdf_path = args.output.rsplit(".", 1)[0] + ".pdf"
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight",
                    facecolor=T.COLOR_BG)
        print(f"[OK] PDF vektor : {pdf_path}")
