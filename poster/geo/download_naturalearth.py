"""Unduh Natural Earth shapefile untuk choropleth dunia.

Natural Earth adalah dataset peta public domain — gratis, tanpa atribusi
wajib, selamanya. Kita ambil resolusi 110m (ringan, cukup untuk A2 poster).

Jalankan sekali:
    python -m poster.geo.download_naturalearth
"""
from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path


# Natural Earth 50m admin 0 countries — zipped shapefile bundle
# 50m resolusi cukup untuk capture ~242 negara termasuk microstates
# (110m hanya 177, 10m oversized untuk A2 poster context)
NE_URL = (
    "https://naciscdn.org/naturalearth/50m/cultural/"
    "ne_50m_admin_0_countries.zip"
)
# Fallback GitHub mirror kalau naciscdn tidak responsif
NE_FALLBACK_URL = (
    "https://github.com/nvkelso/natural-earth-vector/raw/master/"
    "50m_cultural/ne_50m_admin_0_countries.zip"
)

EXPECTED_FILES = {
    "ne_50m_admin_0_countries.shp",
    "ne_50m_admin_0_countries.shx",
    "ne_50m_admin_0_countries.dbf",
    "ne_50m_admin_0_countries.prj",
}


def _try_download(url: str, dest_dir: Path) -> bool:
    """Try download and extract. Return True jika sukses."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (ne-downloader)"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            zf.extractall(dest_dir)
        return True
    except Exception as e:
        print(f"[WARN] download dari {url} gagal: {type(e).__name__} {e}")
        return False


def main() -> int:
    dest = Path(__file__).parent
    dest.mkdir(parents=True, exist_ok=True)

    present = {f.name for f in dest.iterdir() if f.is_file()}
    if EXPECTED_FILES.issubset(present):
        print("[SKIP] Natural Earth 110m sudah lengkap di", dest)
        return 0

    for url in (NE_URL, NE_FALLBACK_URL):
        print(f"[INFO] mencoba: {url}")
        if _try_download(url, dest):
            print(f"[OK]   extracted ke {dest}")
            break
    else:
        print("[FAIL] semua URL gagal")
        return 1

    # Verify
    present = {f.name for f in dest.iterdir() if f.is_file()}
    missing = EXPECTED_FILES - present
    if missing:
        print(f"[FAIL] file hilang setelah extract: {missing}")
        return 1

    print("[OK]   semua file shapefile tersedia:")
    for f in sorted(EXPECTED_FILES):
        size = (dest / f).stat().st_size
        print(f"         {f}  ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
