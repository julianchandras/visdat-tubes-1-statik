# CLAUDE.md

## Project Overview
Tugas Besar 1 IF4061 (Visualisasi Data) — analisis data hukum pernikahan anak (child marriage laws) dari 193 negara UN, tahun 2023. Dataset dari WORLD Policy Analysis Center (UCLA).

## Tech Stack
- Python 3.12, pandas, numpy, matplotlib
- Jupyter Notebook untuk eksplorasi data
- Virtual environment: `.venv/`

## Project Structure
```
data/
  world-cml-2023-v1.xls          # Dataset asli (193 x 85)
  world-cml-2023-dict.pdf         # Kamus data
  world-cml-2023-cleaned.csv      # Dataset hasil cleaning + transformasi (193 x 107)
notebooks/
  exploration.ipynb                # Notebook eksplorasi data (bagian 1-6)
```

## Setup
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1       # Windows
pip install -r requirements.txt
pip install xlrd matplotlib      # Tambahan yang diperlukan
```

## Dataset Notes
- Kolom ordinal menggunakan kode: 1="≤13", 2="14-15", 3="16-17", 5="≥18", 9="Unknown"
- Nilai 9 bukan missing data, melainkan "unknown minimum age set by religious/customary law"
- `iso2` Namibia: "NA" terparse sebagai NaN oleh pandas — sudah di-fix di notebook
- `wb_econ` Venezuela: NaN karena World Bank tidak mengklasifikasikan — dipertahankan
- Kolom timeseries `minage_par_18_*`: ~70-79 missing per kolom, legitimate

## Conventions
- Notebook ditulis dalam Bahasa Indonesia (markdown) + Python (code)
- Semua kolom turunan baru diberi suffix `_label` untuk versi readable
