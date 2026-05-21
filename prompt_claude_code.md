# Prompt untuk Claude Code — Tugas Besar 1 IF4061 (Poin 4, 5, 6)

## Konteks

Aku sedang mengerjakan Tugas Besar 1 mata kuliah IF4061 (Visualisasi Data). Ini tugas kelompok. Repo sudah ada di direktori ini. Struktur repo:

```
data/
  world-cml-2023-v1.xls    <- dataset utama
  world-cml-2023-dict.pdf   <- kamus data
notebooks/
  exploration.ipynb          <- notebook eksplorasi (sudah ada bagian 1-3, bagian 4-6 masih kosong)
```

Dataset ini berisi data hukum pernikahan anak (child marriage laws) dari 193 negara UN, diproduksi oleh WORLD Policy Analysis Center (UCLA), tahun 2023. Format: file Excel (.xls), 193 baris × 85 kolom.

## Tugasku

Aku perlu mengisi **bagian 4, 5, dan 6** di notebook `exploration.ipynb` yang saat ini masih kosong:

- **4. Data Cleaning & Quality Improvement**
- **5. Data Transformation for Analysis**
- **6. Data Consolidation**

Untuk setiap bagian, buatkan **sel Markdown** penjelasan (dalam Bahasa Indonesia) dan **sel Code** Python yang menjalankan prosesnya. Di akhir, export dataset final ke CSV sebagai `data/world-cml-2023-cleaned.csv`.

## Detail yang harus dikerjakan

### 4. Data Cleaning & Quality Improvement

Temuan dari eksplorasi data:

**Missing Values (kolom inti, bukan timeseries):**
- `iso2`: 1 missing (Namibia) — kode ISO-2 Namibia seharusnya "NA", kemungkinan terparse sebagai NaN. Fix: isi manual dengan "NA".
- `wb_econ`: 1 missing (Venezuela) — World Bank tidak mengklasifikasikan Venezuela. Keputusan: pertahankan sebagai NaN, dokumentasikan.
- `minage_fem_leg`, `minage_fem_pc`: 1 missing (Afghanistan) — tidak ada data legislasi. Pertahankan sebagai NaN.
- `minage_fem_crlaw`, `minage_fem_loop`, `loop_summ`, dan kolom terkait: 6 missing (Afghanistan, Comoros, Ethiopia, Iraq, Myanmar, Tanzania) — negara dengan sistem hukum kompleks yang sulit dikodekan. Pertahankan sebagai NaN.
- `except_crlaw`: 4 missing (Afghanistan, Comoros, Ethiopia, Myanmar). Pertahankan sebagai NaN.
- Kolom timeseries `minage_par_18_f_*` dan `minage_par_18_m_*`: rata-rata 72.5 missing per kolom (dari 193). Ini karena data historis tidak tersedia untuk semua negara. Pertahankan apa adanya.

**Nilai Khusus (Value 9 = "Unknown minimum age set by religious or customary law"):**
- Muncul di: `minage_fem_crlaw` (15 negara), `minage_fem_any` (15), `minage_mal_crlaw` (15), `minage_mal_any` (15), `minage_fem_loop` (13), `minage_mal_loop` (14), `loop_summ` (13).
- Keputusan: Nilai 9 BUKAN missing data, melainkan kategori bermakna ("unknown/unregulated"). Pertahankan sebagai kode tersendiri.

**Duplikasi:** Tidak ada baris duplikat maupun duplikasi nama negara.

**Yang perlu di-fix:**
1. Isi `iso2` Namibia dengan "NA"
2. Dokumentasikan bahwa missing values lainnya adalah legitimate (bukan error) dan dipertahankan

Kode Python harus:
- Tampilkan ringkasan missing values per kolom inti
- Fix iso2 Namibia
- Tampilkan daftar negara dengan value 9
- Print konfirmasi tidak ada duplikat

### 5. Data Transformation for Analysis

Buat kolom-kolom turunan baru yang berguna untuk analisis dan visualisasi nantinya:

1. **`wb_econ_label`**: Mapping kode numerik ke label readable:
   - 1.0 → "Low-income"
   - 2.0 → "Middle-income"  
   - 4.0 → "High-income"

2. **`has_loophole_fem`** (boolean): True jika `minage_fem_loop` < `minage_fem_leg` (usia efektif dengan loophole lebih rendah dari usia legal untuk perempuan)

3. **`has_loophole_mal`** (boolean): Sama untuk laki-laki

4. **`loophole_severity_fem`**: Kategori severity loophole untuk perempuan:
   - "Tidak ada loophole" jika `minage_fem_loop` >= `minage_fem_leg`
   - "Ringan" jika legal=18 tapi loophole turun ke 16-17
   - "Sedang" jika legal=18 tapi loophole turun ke 14-15
   - "Berat" jika legal=18 tapi loophole turun ke ≤13
   - "Unknown" jika `minage_fem_loop` == 9

5. **`gender_loophole_gap`**: Selisih antara `minage_fem_loop` dan `minage_mal_loop` (negatif = perempuan kurang terlindungi)

6. **Label mapping untuk kolom ordinal utama** — buat versi readable:
   - Untuk kolom `minage_*` (1→"≤13", 2→"14-15", 3→"16-17", 5→"≥18", 9→"Unknown")
   - Untuk kolom `protect_*` (1→"Tanpa batasan", 2→"Consent ortu/hukum adat", 3→"Persetujuan pengadilan/kehamilan", 5→"Dilarang")
   - Untuk `except_pc` (1→"Bisa menikah <18 tanpa syarat", 2→"Ada pengecualian consent ortu", 3→"Ada pengecualian + syarat tambahan", 5→"Tidak ada pengecualian")

7. **Tentukan resolusi data**: Untuk visualisasi statis, kita menggunakan data cross-sectional (snapshot 2023) pada level negara. Kolom timeseries (`minage_par_18_f_*` dan `minage_par_18_m_*`) bisa digunakan nanti jika ingin menunjukkan tren temporal, tapi untuk fase ini fokus ke data terkini.

Kode Python harus:
- Buat semua kolom turunan di atas
- Tampilkan sample hasilnya
- Print ringkasan statistik (berapa negara punya loophole, distribusi severity, dll)

### 6. Data Consolidation

Bagian ini menjelaskan bahwa **tidak diperlukan konsolidasi data eksternal tambahan**. Alasan:
- Dataset sudah mengandung variabel `wb_econ` (World Bank Income Group) sebagai proksi kondisi ekonomi negara
- Dataset sudah mengandung variabel `region` (klasifikasi geografis World Bank)
- Kedua variabel ini cukup untuk analisis perbandingan berdasarkan kelompok pendapatan dan wilayah
- Menambahkan data GDP per capita secara eksplisit tidak diperlukan karena `wb_econ` sudah merepresentasikan klasifikasi ekonomi yang relevan

Kode Python:
- Tampilkan distribusi `wb_econ` dan `region` untuk konfirmasi kelengkapan
- Print statement bahwa konsolidasi tidak diperlukan

### Export Dataset Final

Di akhir notebook:
- Export dataframe yang sudah di-transform ke `data/world-cml-2023-cleaned.csv`
- Print shape dan konfirmasi

## Instruksi Teknis

- Gunakan `pandas` untuk semua operasi
- Tambahkan Markdown cell (dalam Bahasa Indonesia) sebelum setiap code cell untuk menjelaskan apa yang dilakukan
- Pastikan kode bisa dijalankan dari atas ke bawah tanpa error
- Jangan mengubah bagian 1-3 yang sudah ada di notebook
- Jika notebook sudah punya cell untuk bagian 4-6 (walau kosong), isi cell tersebut. Jika belum ada, tambahkan cell baru di bawah bagian 3.
