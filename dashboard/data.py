"""Data layer dashboard — load (cached) + helper filter & agregasi.

Membaca CSV hasil `prepare_data.py`. Semua transformasi berat sudah dilakukan
di build-step; di sini hanya load + filter ringan supaya rerun Streamlit cepat.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data" / "dashboard_data.csv"

YEARS = list(range(1995, 2024))
F_COLS = [f"minage_par_18_f_{y}" for y in YEARS]
M_COLS = [f"minage_par_18_m_{y}" for y in YEARS]


@st.cache_data(show_spinner=False)
def _load_csv(_path: Path, _mtime: float) -> pd.DataFrame:
    """Internal: cached read keyed by mtime supaya cache invalidate otomatis
    saat CSV di-regenerate atau ter-update (mis. setelah git pull di Streamlit
    Cloud). Tanpa ini, signature load_data() tetap sama walau CSV berubah,
    sehingga cache lama yang punya skema lebih sempit bisa bertahan & memicu
    KeyError di chart yang butuh kolom baru.
    """
    return pd.read_csv(_path)


def load_data() -> pd.DataFrame:
    """Load dataset dashboard. Cache invalidate otomatis bila file CSV berubah."""
    return _load_csv(DATA_PATH, DATA_PATH.stat().st_mtime)


def filter_data(
    df: pd.DataFrame,
    regions: list[str] | None = None,
    incomes: list[str] | None = None,
    severities: list[float] | None = None,
) -> pd.DataFrame:
    """Terapkan filter global. None / list kosong = tidak memfilter dimensi itu."""
    out = df
    if regions:
        out = out[out["region"].isin(regions)]
    if incomes:
        out = out[out["wb_econ_label"].isin(incomes)]
    if severities:
        out = out[out["loop_summ"].isin(severities)]
    return out


def kpi_metrics(df: pd.DataFrame) -> dict[str, int]:
    """Hitung 4 angka KPI untuk subset terfilter."""
    n_under18 = int(((df["minage_fem_any"] != 5) & df["minage_fem_any"].notna()).sum())
    n_loophole = int(df["has_loophole_fem"].sum())
    n_worst = int((df["loop_summ"] == 1).sum())
    n_parity = int((df["loop_summ"] == 5).sum())
    return {
        "under18": n_under18,
        "loophole": n_loophole,
        "worst": n_worst,
        "parity": n_parity,
    }


def country_detail(df: pd.DataFrame, iso3: str) -> dict | None:
    """Ambil ringkasan satu negara untuk panel detail (klik di peta)."""
    row = df[df["iso3"] == iso3]
    if row.empty:
        return None
    r = row.iloc[0]
    return {
        "country": r["country"],
        "iso3": r["iso3"],
        "region": r["region"],
        "income": r.get("wb_econ_label"),
        "perlindungan": r.get("loop_summ_label"),
        "minage_fem": r.get("minage_fem_loop_label"),
        "minage_mal": r.get("minage_mal_loop_label"),
        "has_loophole_fem": bool(r.get("has_loophole_fem", False)),
        "has_loophole_mal": bool(r.get("has_loophole_mal", False)),
        "has_gender_gap": bool(r.get("has_gender_gap", False)),
    }


def region_timeseries(df: pd.DataFrame, region: str | None = None) -> pd.DataFrame:
    """% negara dengan usia min ≥18 (izin ortu) per tahun, F & M.

    region=None → agregat seluruh subset.
    """
    sub = df if region is None else df[df["region"] == region]
    rows = []
    for year, fc, mc in zip(YEARS, F_COLS, M_COLS):
        n_f = sub[fc].notna().sum()
        n_m = sub[mc].notna().sum()
        f_pct = (sub[fc] == 1).sum() / n_f * 100 if n_f else None
        m_pct = (sub[mc] == 1).sum() / n_m * 100 if n_m else None
        rows.append({"year": year, "Perempuan": f_pct, "Laki-laki": m_pct})
    return pd.DataFrame(rows)
