"""Persiapan data dashboard (Tugas Besar 2) — reproducible & self-contained.

Membaca dataset ASLI `data/world-cml-2023-v1.xls`, menerapkan ulang langkah
cleaning + transformasi yang disepakati di Tubes 1, dan MEMPERTAHANKAN kolom
composite `loop_summ`, `minage_fem_any`, `minage_mal_any` (yang sempat ter-drop
di CSV cleaned versi merge). Output: `dashboard/data/dashboard_data.csv`.

Jalankan sekali sebagai build-step:
    .venv/Scripts/python.exe dashboard/prepare_data.py

App Streamlit hanya membaca CSV hasil generate ini — tidak butuh xlrd saat runtime
(deploy lebih ringan). Lihat docs-system-development/tubes2/spec_dashboard.md §7.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# Path relatif terhadap root repo (file ini ada di dashboard/)
ROOT = Path(__file__).resolve().parent.parent
SOURCE_XLS = ROOT / "data" / "world-cml-2023-v1.xls"
OUTPUT_CSV = Path(__file__).resolve().parent / "data" / "dashboard_data.csv"

# Mapping ground-truth diekstrak dari CSV cleaned tim (hanya 1/2/4 yang muncul).
# 3 (upper-middle versi WB) tidak ada di data ini; NaN (Venezuela) dipertahankan.
WB_ECON_LABELS = {
    1.0: "Low-income",
    2.0: "Middle-income",
    4.0: "High-income",
}

# Skala ordinal usia minimum (kamus data WORLD Policy Center).
MINAGE_LABELS = {
    1.0: "≤ 13 tahun",
    2.0: "14-15 tahun",
    3.0: "16-17 tahun",
    5.0: "≥ 18 tahun",
    9.0: "Tidak diketahui (adat/agama)",
}

# Ringkasan loophole composite (lihat poster/panels/panel_a.py).
LOOP_SUMM_LABELS = {
    5.0: "Kesetaraan & usia ≥ 18 tahun",
    3.0: "1 masalah: kesenjangan ATAU usia 14-17",
    2.0: "2 masalah: kesenjangan DAN usia 14-17",
    1.0: "Bisa menikah ≤ 13 tahun",
    9.0: "Mungkin < 18 (diatur adat/agama)",
}

# protect_girl_*/protect_boy_*: keadaan saat anak umur X bisa dinikahkan.
PROTECT_LABELS = {
    1.0: "Tanpa pembatasan",
    2.0: "Boleh dengan izin orang tua / hukum adat",
    3.0: "Hanya dengan persetujuan pengadilan / kehamilan",
    5.0: "Dilarang secara hukum",
}

# legal_diff_leg / legal_diff_pc: granular gender disparity.
LEGAL_DIFF_LABELS = {
    1.0: "Tanpa usia min. khusus perempuan",
    2.0: "Perempuan 3 tahun lebih muda",
    3.0: "Perempuan 1-2 tahun lebih muda",
    5.0: "Tanpa perbedaan",
}

# Kolom yang dipertahankan untuk dashboard (lean tapi lengkap).
# Diperluas untuk mendukung viz Tangga Umur, Heatmap Erosi, dan Dumbbell Gender.
KEEP_COLUMNS = [
    "country", "iso2", "iso3", "region", "wb_econ",
    # Usia min — 5 layer per gender (leg / pc / crlaw / loop / any)
    "minage_fem_leg",   "minage_mal_leg",
    "minage_fem_pc",    "minage_mal_pc",
    "minage_fem_crlaw", "minage_mal_crlaw",
    "minage_fem_loop",  "minage_mal_loop",
    "minage_fem_any",   "minage_mal_any",
    # Ringkasan composite
    "loop_summ",
    # Loophole exceptions
    "except_pc", "except_preg", "except_crlaw",
    # protect_girl_* / protect_boy_* — keadaan per usia (untuk Tangga Umur)
    "protect_girl_13", "protect_girl_15", "protect_girl_17",
    "protect_boy_13",  "protect_boy_15",  "protect_boy_17",
    # Gender disparity granular
    "legal_diff_leg", "legal_diff_pc",
]


def build() -> pd.DataFrame:
    df = pd.read_excel(SOURCE_XLS)

    # ── Cleaning fix #1: iso2 Namibia "NA" terparse jadi NaN oleh pandas.
    # (Di .xls sudah NaN; di sini dipulihkan ke "NA" yang benar.)
    mask_namibia = df["country"].str.contains("Namibia", na=False) & df["iso2"].isna()
    df.loc[mask_namibia, "iso2"] = "NA"

    # ── Subset kolom timeseries (1995-2023) untuk Panel D / Section timeseries.
    ts_cols = [c for c in df.columns if c.startswith("minage_par_18_")]

    df = df[KEEP_COLUMNS + ts_cols].copy()

    # ── Transformasi: label readable (suffix _label sesuai konvensi Tubes 1).
    df["wb_econ_label"] = df["wb_econ"].map(WB_ECON_LABELS)
    df["loop_summ_label"] = df["loop_summ"].map(LOOP_SUMM_LABELS)
    df["minage_fem_loop_label"] = df["minage_fem_loop"].map(MINAGE_LABELS)
    df["minage_mal_loop_label"] = df["minage_mal_loop"].map(MINAGE_LABELS)
    # Label readable untuk kolom baru
    for age in (13, 15, 17):
        df[f"protect_girl_{age}_label"] = df[f"protect_girl_{age}"].map(PROTECT_LABELS)
        df[f"protect_boy_{age}_label"]  = df[f"protect_boy_{age}"].map(PROTECT_LABELS)
    df["legal_diff_leg_label"] = df["legal_diff_leg"].map(LEGAL_DIFF_LABELS)
    df["legal_diff_pc_label"]  = df["legal_diff_pc"].map(LEGAL_DIFF_LABELS)

    # ── Derivasi: ada celah hukum (loop < legal). Verified vs CSV tim (55/50).
    df["has_loophole_fem"] = df["minage_fem_loop"] < df["minage_fem_leg"]
    df["has_loophole_mal"] = df["minage_mal_loop"] < df["minage_mal_leg"]

    # ── Derivasi: gender gap (selisih kode usia loop M - F), kode 9 di-mask.
    fem = df["minage_fem_loop"].where(df["minage_fem_loop"] != 9)
    mal = df["minage_mal_loop"].where(df["minage_mal_loop"] != 9)
    df["gender_gap_loop"] = mal - fem
    df["has_gender_gap"] = df["minage_fem_loop"] != df["minage_mal_loop"]

    # ── Join centroid lon/lat dari Natural Earth 50m shapefile.
    # Build-time saja (butuh geopandas, sama seperti xlrd). Runtime app hanya
    # membaca kolom lon/lat dari CSV → tidak perlu geopandas di prod.
    import geopandas as gpd
    ne_path = ROOT / "poster" / "geo" / "ne_50m_admin_0_countries.shp"
    gdf = gpd.read_file(ne_path)[["ADM0_A3", "geometry"]]
    # Patch South Sudan ISO mismatch (sama seperti poster Tubes 1)
    gdf.loc[gdf["ADM0_A3"] == "SDS", "ADM0_A3"] = "SSD"
    # Centroid pakai representative_point() (selalu di dalam poligon, beda
    # dengan .centroid yang bisa di laut untuk negara cekung mis. Norwegia).
    cent = gdf.copy()
    cent["lon"] = cent["geometry"].representative_point().x
    cent["lat"] = cent["geometry"].representative_point().y
    df = df.merge(
        cent[["ADM0_A3", "lon", "lat"]].rename(columns={"ADM0_A3": "iso3"}),
        on="iso3", how="left",
    )

    return df


def main() -> None:
    df = build()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"[OK] {OUTPUT_CSV}  shape={df.shape}")
    print(f"     loop_summ      : {df['loop_summ'].notna().sum()} non-null")
    print(f"     has_loophole_f : {int(df['has_loophole_fem'].sum())}")
    print(f"     has_loophole_m : {int(df['has_loophole_mal'].sum())}")


if __name__ == "__main__":
    main()
