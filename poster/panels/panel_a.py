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
from matplotlib.path import Path as MplPath
from pathlib import Path

import geopandas as gpd

from poster import theme as T


# ────────────────────────────────────────────────────────────
# Pin marker — custom teardrop path (mirip Google Maps pin)
# Tip pada koordinat (0, -1.4), kepala bulat di atas. Marker matplotlib
# di-center di geometric mean — visual tip akan sedikit di bawah
# scatter coord, masih jelas menunjuk ke negara.
# ────────────────────────────────────────────────────────────
PIN_PATH = MplPath(
    vertices=[
        (0.0, -1.4),    # tip (bottom)
        (-0.55, -0.5),  # left lower curve
        (-0.95, 0.30),  # left side
        (-0.95, 1.05),  # left upper
        (-0.55, 1.45),  # top-left
        (0.0, 1.55),    # top center
        (0.55, 1.45),   # top-right
        (0.95, 1.05),   # right upper
        (0.95, 0.30),   # right side
        (0.55, -0.5),   # right lower curve
        (0.0, -1.4),    # close to tip
    ],
    codes=[
        MplPath.MOVETO,
        MplPath.LINETO, MplPath.LINETO, MplPath.LINETO, MplPath.LINETO,
        MplPath.LINETO,
        MplPath.LINETO, MplPath.LINETO, MplPath.LINETO, MplPath.LINETO,
        MplPath.CLOSEPOLY,
    ],
)


# ────────────────────────────────────────────────────────────
# Konstanta
# ────────────────────────────────────────────────────────────

SHAPEFILE_PATH = Path("poster/geo/ne_50m_admin_0_countries.shp")

# Label untuk setiap kode loop_summ di legend.
# Order = progresi "kebaikan" dari TERBAIK (atas) → TERBURUK (bawah) → ambigu/no-data.
LOOP_SUMM_LABELS = {
    5.0: "Kesetaraan dan usia ≥ 18 tahun",
    3.0: "1 masalah: kesenjangan ATAU usia 14-17",
    2.0: "2 masalah: kesenjangan DAN usia 14-17",
    1.0: "Bisa menikah ≤ 13 tahun",
    9.0: "Mungkin < 18 tahun (diatur adat/agama)",
}
LEGEND_ORDER = [5.0, 3.0, 2.0, 1.0, 9.0]


# Equal Earth projection (EPSG:8857) — equal-area modern, tidak mendistorsi ukuran
EQUAL_EARTH_CRS = "EPSG:8857"


# Negara untuk callout — dipilih yang dramatic (loop_summ=1 + high-income).
# `xy_offset` (dx, dy dalam koordinat data Equal Earth, bukan points) →
# text di area laut/empty space agar tidak menutupi negara lain.
# Diukur empiris dari shapefile (satuan: meter di proyeksi Equal Earth).
HIGHLIGHT_COUNTRIES = {
    "GRC": {
        "label": "Yunani",
        "note":  "Satu-satunya negara Eropa\ndengan kode 1 (≤ 13 tahun)",
        # Pindah jauh ke kiri & turun (N. Atlantic antara Eropa & Amerika)
        # supaya tidak menutupi judul di atas
        "xy_offset": (-250, -80),
    },
    "SAU": {
        "label": "Arab Saudi",
        "note":  "Negara high-income\nmengizinkan ≤ 13 tahun",
        # Turun jauh ke Indian Ocean supaya tidak menutupi India/Indonesia
        "xy_offset": (50, -180),
    },
    # Singapore dihapus per keputusan tim
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

    # Figure setup — 4 rows: title (hidden) | map | LEGEND DEDICATED | footer
    # Legend di-dedicate ke row sendiri supaya tidak overlap dengan land area
    # peta (Australia, S. Africa, S. America yang meluas ke bawah).
    if fig is None:
        fig = plt.figure(figsize=(14.5, 8.5), dpi=150)
        outer = GridSpec(
            nrows=4, ncols=1,
            figure=fig,
            height_ratios=[0.6, 7.0, 1.0, 0.15],
            hspace=0.04,
            left=0.02, right=0.98, top=0.98, bottom=0.03,
        )
        title_ax = fig.add_subplot(outer[0])
        map_ax = fig.add_subplot(outer[1])
        legend_ax = fig.add_subplot(outer[2])
        footer_ax = fig.add_subplot(outer[3])
    else:
        assert host_subplot_spec is not None
        inner = GridSpecFromSubplotSpec(
            nrows=4, ncols=1,
            subplot_spec=host_subplot_spec,
            height_ratios=[0.6, 7.0, 1.0, 0.15],
            hspace=0.04,
        )
        title_ax = fig.add_subplot(inner[0])
        map_ax = fig.add_subplot(inner[1])
        legend_ax = fig.add_subplot(inner[2])
        footer_ax = fig.add_subplot(inner[3])

    # ── Title block ──
    title_ax.axis("off")
    title_ax.text(
        0.5, 0.50, "Peta Kondisi Global Pernikahan Anak",
        transform=title_ax.transAxes,
        family="serif", fontsize=18, weight=900, color=T.COLOR_HEADLINE,
        ha="center", va="center",
    )

    # ── Base layer: no-data / non-UN countries (light grey + hatched) ──
    no_data = world[world["loop_summ"].isna()]
    no_data.plot(
        ax=map_ax,
        color=T.NO_DATA_COLOR,
        edgecolor="white", linewidth=0.6,
        hatch=T.NO_DATA_HATCH,
    )

    # ── Kategori non-Unknown (ordinal 1/2/3/5) ──
    # Parity (code 5) pakai opacity < 100% supaya feel "lega/hijau" tidak
    # terlalu dominan secara visual — sesuai revisi tim.
    for code in [5.0, 3.0, 2.0, 1.0]:
        sub = world[world["loop_summ"] == code]
        if sub.empty:
            continue
        sub.plot(
            ax=map_ax,
            color=T.LOOP_SUMM_COLORS[code],
            edgecolor="white", linewidth=0.6,
            alpha=T.PARITY_ALPHA if code == 5.0 else 1.0,
        )

    # ── Kategori Unknown (kode 9): kuning + dot pattern subtle ──
    unknown = world[world["loop_summ"] == 9.0]
    if not unknown.empty:
        unknown.plot(
            ax=map_ax,
            color=T.LOOP_SUMM_COLORS[9.0],
            edgecolor="white", linewidth=0.6,
            hatch=T.UNKNOWN_HATCH,
        )

    # Highlight border dihapus per keputusan tim — pinpoint marker +
    # text annotation sudah cukup mengarahkan fokus ke negara highlight

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

    # ── Annotation callouts: ring scatter + curved arrow + text ──
    for iso3, meta in HIGHLIGHT_COUNTRIES.items():
        rows = world[world["ADM0_A3"] == iso3]
        if rows.empty:
            continue
        country_geom = rows.geometry.iloc[0]
        if country_geom is None or country_geom.is_empty:
            continue
        try:
            cx, cy = country_geom.representative_point().coords[0]
        except Exception:
            cx, cy = country_geom.centroid.coords[0]

        # Ring scatter (no fill, accent edge) di country
        map_ax.scatter(
            cx, cy, s=180, facecolors="none",
            edgecolors=T.COLOR_ACCENT, linewidths=1.8, zorder=5,
        )

        # Annotate dengan curved arrow + bbox bg
        map_ax.annotate(
            f"{meta['label']}\n{meta['note']}",
            xy=(cx, cy),
            xytext=meta["xy_offset"], textcoords="offset points",
            fontsize=8, color=T.COLOR_HEADLINE, weight=600,
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
    # Ordering: progresi "kebaikan" (terbaik → terburuk) dengan
    # Unknown & No-data sebagai 2 kategori tambahan di akhir.
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
    # No-data: hatched (sebelumnya tekstur Unknown, sekarang dipindah ke sini)
    legend_patches.append(
        mpatches.Patch(
            facecolor=T.NO_DATA_COLOR, edgecolor="white",
            linewidth=0.5, hatch=T.NO_DATA_HATCH,
            label="Tidak ada data",
        )
    )

    # Legend di axes dedicated — single row (ncol=6) supaya match arah
    # "← baik    buruk →" left-to-right, tidak misleading lagi
    legend_ax.axis("off")
    legend = legend_ax.legend(
        handles=legend_patches,
        loc="center",
        bbox_to_anchor=(0.5, 0.5),
        ncol=6,
        frameon=False,
        fontsize=8.5,
        handlelength=1.5, handleheight=1.0,
        columnspacing=0.9,
        labelcolor=T.COLOR_BODY,
    )
    legend.set_title(
        "Tingkat perlindungan anak dari pernikahan dini",
        prop={"family": "sans-serif", "size": 10, "weight": 700},
    )
    legend.get_title().set_color(T.COLOR_HEADLINE)

    # Footer dihapus per revisi tim — sumber sudah ada di footer poster utama
    footer_ax.axis("off")

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
