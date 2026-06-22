#!/usr/bin/env python3
"""organize.py — Bir klasördeki dosyaları uzantılarına göre alt klasörlere taşır."""

import argparse
import json
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

# Yapılan taşımaların kaydedildiği log dosyasının adı (hedef klasör içine yazılır)
LOG_DOSYASI = ".organize_log.json"


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
    # Geri alma için yapılan taşımaları (kaynak, varış) olarak biriktiriyoruz
    kayitlar: list[dict[str, str]] = []

    for oge in sorted(hedef.iterdir()):
        # Yalnızca dosyalarla ilgileniyoruz; alt klasörlere dokunmuyoruz
        if not oge.is_file():
            continue

        # Kendi log dosyamızı taşımıyoruz
        if oge.name == LOG_DOSYASI:
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
            kayitlar.append({"kaynak": str(oge), "varis": str(varis)})
            tasinan += 1
        except OSError as hata:
            print(f"  [HATA] '{oge.name}' taşınamadı: {hata}")
            atlanan += 1

    # Başarılı taşımaları log dosyasına yaz (undo için)
    if not dry_run and kayitlar:
        log_yaz(hedef, kayitlar)

    print()
    if dry_run:
        print(f"Özet (taslak): {tasinan} dosya taşınacaktı. Hiçbir değişiklik yapılmadı.")
    else:
        print(f"Özet: {tasinan} dosya taşındı, {atlanan} dosya atlandı.")


def log_yaz(hedef: Path, kayitlar: list[dict[str, str]]) -> None:
    """Yapılan taşımaları hedef klasördeki log dosyasına kaydeder."""
    log_yolu = hedef / LOG_DOSYASI
    log_yolu.write_text(
        json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def geri_al(hedef: Path) -> int:
    """Son düzenlemeyi log dosyasına bakarak geri alır."""
    log_yolu = hedef / LOG_DOSYASI
    if not log_yolu.exists():
        print(f"Geri alınacak bir kayıt bulunamadı ('{LOG_DOSYASI}' yok).", file=sys.stderr)
        return 1

    try:
        kayitlar = json.loads(log_yolu.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as hata:
        print(f"Hata: log dosyası okunamadı: {hata}", file=sys.stderr)
        return 1

    geri_alinan = 0
    atlanan = 0
    olusan_klasorler: set[Path] = set()

    # Taşımaları ters sırada geri al
    for kayit in reversed(kayitlar):
        varis = Path(kayit["varis"])
        kaynak = Path(kayit["kaynak"])
        olusan_klasorler.add(varis.parent)

        if not varis.exists():
            print(f"  [ATLANDI] '{varis.name}' bulunamadı, geri alınamıyor.")
            atlanan += 1
            continue

        # Orijinal konumda artık başka bir dosya varsa üzerine yazma
        if kaynak.exists():
            kaynak = benzersiz_isim(kaynak.parent, kaynak.name)
            print(f"  [DIKKAT] '{varis.name}' için orijinal isim dolu, '{kaynak.name}' olarak geri alınıyor.")

        try:
            shutil.move(str(varis), str(kaynak))
            print(f"  [GERI ALINDI] '{varis.name}' -> {kaynak.parent.name}/")
            geri_alinan += 1
        except OSError as hata:
            print(f"  [HATA] '{varis.name}' geri alınamadı: {hata}")
            atlanan += 1

    # Geri almadan sonra boş kalan kategori klasörlerini temizle
    for klasor in olusan_klasorler:
        if klasor.is_dir() and not any(klasor.iterdir()):
            klasor.rmdir()

    # İşlem tamamlandı, log dosyasını sil
    log_yolu.unlink()

    print()
    print(f"Özet: {geri_alinan} dosya geri alındı, {atlanan} dosya atlandı.")
    return 0


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
    ayrıştırıcı.add_argument(
        "--undo",
        action="store_true",
        help="Son düzenlemeyi geri alır (kayıt log dosyasından okunur).",
    )
    argümanlar = ayrıştırıcı.parse_args()

    if argümanlar.dry_run and argümanlar.undo:
        print("Hata: --dry-run ve --undo birlikte kullanılamaz.", file=sys.stderr)
        return 1

    hedef = Path(argümanlar.klasor).expanduser().resolve()

    if not hedef.exists():
        print(f"Hata: '{hedef}' bulunamadı.", file=sys.stderr)
        return 1
    if not hedef.is_dir():
        print(f"Hata: '{hedef}' bir klasör değil.", file=sys.stderr)
        return 1

    if argümanlar.undo:
        print(f"'{hedef}' klasörü için son düzenleme geri alınıyor...\n")
        return geri_al(hedef)

    if argümanlar.dry_run:
        print(f"TASLAK modu: '{hedef}' klasörü için planlanan işlemler:\n")
    else:
        print(f"'{hedef}' klasörü düzenleniyor...\n")

    klasor_organize_et(hedef, argümanlar.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
