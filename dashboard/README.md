# Dashboard Interaktif — Hukum Pernikahan Anak

Tugas Besar 2 IF4061 (Visualisasi Data Interaktif). Dashboard **analitis** atas
data hukum pernikahan anak 193 negara anggota PBB (WORLD Policy Analysis Center,
2023). Lanjutan topik Tugas Besar 1.

## Stack
- **Streamlit** (framework dashboard) + **Plotly** (chart interaktif)
- **pandas / numpy** (data)
- Hosting: **Streamlit Community Cloud** (gratis, publik)

## Menjalankan lokal
```bash
# dari root repo, dengan venv aktif
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

## Menyiapkan data (build-step, sekali jalan)
Data dashboard di-generate dari `.xls` asli (butuh `xlrd`, hanya saat build):
```bash
.venv/Scripts/python.exe dashboard/prepare_data.py
# → dashboard/data/dashboard_data.csv
```
App runtime hanya membaca CSV ini, jadi `xlrd` tidak masuk requirements deploy.

## Struktur
```
dashboard/
  app.py              # entry: layout, sidebar filter, orkestrasi
  data.py             # load (cached) + filter + agregasi
  theme.py            # token warna/label (port dari poster Tubes 1)
  prepare_data.py     # build-step: .xls → dashboard_data.csv
  charts/             # modul chart Plotly (peta, gender×income, loophole, dst)
  data/               # dashboard_data.csv (generated)
  requirements.txt
.streamlit/config.toml  # tema — di ROOT repo (dibaca relatif ke working dir
                        # 'streamlit run', bukan lokasi app.py)
```

## Fitur interaktif (syarat tugas)
- **Filtering**: region, pendapatan, tingkat perlindungan (sidebar) + range tahun (timeseries)
- **Zooming**: native Plotly (peta & chart)
- **Tooltip/hover**: hovertemplate kustom di setiap chart

Dokumen desain lengkap: `docs-system-development/tubes2/spec_dashboard.md`
