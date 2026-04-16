"""Unduh Google Fonts (OFL) ke direktori ini untuk render poster.

Fonts di-download dari repo github.com/google/fonts (SIL Open Font License).
Tidak butuh akun/subscription — seluruh fonts di-distribute gratis.

Jalankan sekali:
    python -m poster.fonts.download_fonts
"""
from __future__ import annotations

import urllib.request
import urllib.error
from pathlib import Path


# Font files yang dibutuhkan poster — sesuai spec_desain.md bagian 11.2
# URL pattern: raw GitHub mirror dari google/fonts (OFL license, free forever)
#
# Google Fonts repo distribusikan Playfair Display & Source Sans 3 sebagai
# VARIABLE FONTS — satu file TTF covers semua weight (axis `wght`).
# Matplotlib >=3.8 support variable font via font_manager. IBM Plex Mono
# masih distribusikan sebagai static TTF per weight.
FONT_FILES = {
    # Playfair Display — variable font, wght axis 400-900
    "PlayfairDisplay[wght].ttf":
        "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",

    # Source Sans 3 — variable font, wght axis 200-900
    "SourceSans3[wght].ttf":
        "https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf",

    # IBM Plex Mono — static per-weight TTF
    "IBMPlexMono-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf",
    "IBMPlexMono-Medium.ttf":
        "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf",
}


def _download(url: str, dest: Path) -> tuple[bool, str]:
    """Download single file. Return (success, message)."""
    if dest.exists() and dest.stat().st_size > 0:
        return True, f"[SKIP] already exists: {dest.name}"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (font-downloader)"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return True, f"[OK]   downloaded {dest.name} ({len(data):,} bytes)"
    except urllib.error.HTTPError as e:
        return False, f"[FAIL] {dest.name}: HTTP {e.code} — {url}"
    except Exception as e:
        return False, f"[FAIL] {dest.name}: {type(e).__name__} — {e}"


def main() -> int:
    fonts_dir = Path(__file__).parent
    fonts_dir.mkdir(parents=True, exist_ok=True)

    success = 0
    fail = 0
    for filename, url in FONT_FILES.items():
        ok, msg = _download(url, fonts_dir / filename)
        print(msg)
        if ok:
            success += 1
        else:
            fail += 1

    print(f"\nSummary: {success} ok, {fail} failed, total {len(FONT_FILES)}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
