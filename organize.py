#!/usr/bin/env python3
"""organize.py — Bir klasördeki dosyaları uzantılarına göre alt klasörlere taşır."""

import argparse
import shutil
import sys
from pathlib import Path

# Kategori -> o kategoriye ait uzantılar
KATEGORILER = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".heic", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".ppt", ".pptx", ".csv", ".md", ".epub"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".rb",
             ".go", ".rs", ".php", ".html", ".css", ".json", ".xml", ".yml", ".yaml", ".sh"},
}

# Hiçbir kategoriye uymayan dosyaların gideceği klasör
DIGER = "Others"


def kategori_bul(uzanti: str) -> str:
    """Verilen uzantıya karşılık gelen kategori adını döndürür."""
    uzanti = uzanti.lower()
    for kategori, uzantilar in KATEGORILER.items():
        if uzanti in uzantilar:
            return kategori
    return DIGER


def klasor_organize_et(hedef: Path, dry_run: bool) -> None:
    """Hedef klasördeki dosyaları kategorilere göre taşır."""
    # Bu betiğin oluşturduğu kategori klasörlerinin adları (tekrar taşımayı önlemek için)
    kategori_isimleri = set(KATEGORILER.keys()) | {DIGER}

    tasinan = 0
    atlanan = 0

    for oge in sorted(hedef.iterdir()):
        # Yalnızca dosyalarla ilgileniyoruz; alt klasörlere dokunmuyoruz
        if not oge.is_file():
            continue

        kategori = kategori_bul(oge.suffix)
        hedef_klasor = hedef / kategori
        varis = hedef_klasor / oge.name

        if dry_run:
            print(f"  [TASLAK] '{oge.name}' -> {kategori}/")
            tasinan += 1
            continue

        # Klasörü oluştur
        hedef_klasor.mkdir(exist_ok=True)

        # Aynı isimde dosya varsa üzerine yazmamak için yeni isim üret
        if varis.exists():
            varis = benzersiz_isim(hedef_klasor, oge.name)
            print(f"  [DIKKAT] '{oge.name}' zaten mevcut, '{varis.name}' olarak taşınıyor.")

        try:
            shutil.move(str(oge), str(varis))
            print(f"  [TASINDI] '{oge.name}' -> {kategori}/")
            tasinan += 1
        except OSError as hata:
            print(f"  [HATA] '{oge.name}' taşınamadı: {hata}")
            atlanan += 1

    print()
    if dry_run:
        print(f"Özet (taslak): {tasinan} dosya taşınacaktı. Hiçbir değişiklik yapılmadı.")
    else:
        print(f"Özet: {tasinan} dosya taşındı, {atlanan} dosya atlandı.")


def benzersiz_isim(klasor: Path, isim: str) -> Path:
    """Klasörde çakışmayan bir dosya yolu üretir (ör. dosya_1.txt)."""
    taban = Path(isim).stem
    uzanti = Path(isim).suffix
    sayac = 1
    while True:
        aday = klasor / f"{taban}_{sayac}{uzanti}"
        if not aday.exists():
            return aday
        sayac += 1


def main() -> int:
    ayrıştırıcı = argparse.ArgumentParser(
        description="Bir klasördeki dosyaları uzantılarına göre alt klasörlere düzenler.",
        epilog="Örnek: python organize.py ~/İndirilenler --dry-run",
    )
    ayrıştırıcı.add_argument(
        "klasor",
        help="Düzenlenecek klasörün yolu.",
    )
    ayrıştırıcı.add_argument(
        "--dry-run",
        action="store_true",
        help="Gerçekten taşımadan, hangi dosyanın nereye gideceğini gösterir.",
    )
    argümanlar = ayrıştırıcı.parse_args()

    hedef = Path(argümanlar.klasor).expanduser().resolve()

    if not hedef.exists():
        print(f"Hata: '{hedef}' bulunamadı.", file=sys.stderr)
        return 1
    if not hedef.is_dir():
        print(f"Hata: '{hedef}' bir klasör değil.", file=sys.stderr)
        return 1

    if argümanlar.dry_run:
        print(f"TASLAK modu: '{hedef}' klasörü için planlanan işlemler:\n")
    else:
        print(f"'{hedef}' klasörü düzenleniyor...\n")

    klasor_organize_et(hedef, argümanlar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
