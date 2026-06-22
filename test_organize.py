"""organize.py için pytest testleri.

Testler gerçek dosya sistemini kirletmemek için pytest'in `tmp_path`
geçici klasörünü kullanır.
"""

import json

import pytest

import organize
from organize import (
    DIGER,
    LOG_DOSYASI,
    geri_al,
    kategori_bul,
    klasor_organize_et,
)


# --- kategori_bul --------------------------------------------------------

@pytest.mark.parametrize(
    "uzanti, beklenen",
    [
        (".jpg", "Images"),
        (".PNG", "Images"),      # büyük/küçük harf duyarsız olmalı
        (".pdf", "Documents"),
        (".md", "Documents"),
        (".mp4", "Videos"),
        (".mp3", "Audio"),
        (".zip", "Archives"),
        (".py", "Code"),
        (".json", "Code"),
        (".xyz", DIGER),         # bilinmeyen uzantı
        ("", DIGER),             # uzantısız dosya
    ],
)
def test_kategori_bul(uzanti, beklenen):
    assert kategori_bul(uzanti) == beklenen


# --- yardımcılar ---------------------------------------------------------

def _dosya_olustur(klasor, isim, icerik="veri"):
    """Geçici klasörde bir dosya oluşturup yolunu döndürür."""
    yol = klasor / isim
    yol.write_text(icerik, encoding="utf-8")
    return yol


# --- klasor_organize_et --------------------------------------------------

def test_dosyalar_dogru_kategorilere_tasinir(tmp_path):
    _dosya_olustur(tmp_path, "tatil.jpg")
    _dosya_olustur(tmp_path, "rapor.pdf")
    _dosya_olustur(tmp_path, "betik.py")
    _dosya_olustur(tmp_path, "bilinmeyen.xyz")

    klasor_organize_et(tmp_path, dry_run=False)

    assert (tmp_path / "Images" / "tatil.jpg").is_file()
    assert (tmp_path / "Documents" / "rapor.pdf").is_file()
    assert (tmp_path / "Code" / "betik.py").is_file()
    assert (tmp_path / DIGER / "bilinmeyen.xyz").is_file()
    # Orijinal konumda artık dosya kalmamalı
    assert not (tmp_path / "tatil.jpg").exists()


def test_dry_run_hicbir_sey_tasimaz(tmp_path):
    _dosya_olustur(tmp_path, "tatil.jpg")

    klasor_organize_et(tmp_path, dry_run=True)

    # Dosya yerinde kalmalı, kategori klasörü ve log oluşmamalı
    assert (tmp_path / "tatil.jpg").is_file()
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / LOG_DOSYASI).exists()


def test_alt_klasorlere_dokunulmaz(tmp_path):
    alt = tmp_path / "mevcut_klasor"
    alt.mkdir()
    _dosya_olustur(alt, "icerik.txt")

    klasor_organize_et(tmp_path, dry_run=False)

    # Alt klasör ve içindeki dosya olduğu gibi kalmalı
    assert (alt / "icerik.txt").is_file()


def test_isim_cakismasi_benzersiz_isim_uretir(tmp_path):
    # Images klasörü ve içinde aynı isimde bir dosya önceden var
    (tmp_path / "Images").mkdir()
    _dosya_olustur(tmp_path / "Images", "foto.jpg", icerik="eski")
    _dosya_olustur(tmp_path, "foto.jpg", icerik="yeni")

    klasor_organize_et(tmp_path, dry_run=False)

    assert (tmp_path / "Images" / "foto.jpg").read_text(encoding="utf-8") == "eski"
    assert (tmp_path / "Images" / "foto_1.jpg").read_text(encoding="utf-8") == "yeni"


def test_log_dosyasi_olusturulur(tmp_path):
    _dosya_olustur(tmp_path, "tatil.jpg")
    _dosya_olustur(tmp_path, "rapor.pdf")

    klasor_organize_et(tmp_path, dry_run=False)

    log_yolu = tmp_path / LOG_DOSYASI
    assert log_yolu.is_file()
    kayitlar = json.loads(log_yolu.read_text(encoding="utf-8"))
    assert len(kayitlar) == 2
    assert all("kaynak" in k and "varis" in k for k in kayitlar)


def test_log_dosyasi_tasinmaz(tmp_path):
    # Önceden var olan bir log dosyası organize sırasında taşınmamalı
    _dosya_olustur(tmp_path, LOG_DOSYASI, icerik="[]")
    _dosya_olustur(tmp_path, "tatil.jpg")

    klasor_organize_et(tmp_path, dry_run=False)

    assert (tmp_path / LOG_DOSYASI).is_file()
    assert not (tmp_path / DIGER / LOG_DOSYASI).exists()


# --- geri_al (undo) ------------------------------------------------------

def test_geri_al_dosyalari_eski_yerine_koyar(tmp_path):
    _dosya_olustur(tmp_path, "tatil.jpg")
    _dosya_olustur(tmp_path, "rapor.pdf")
    klasor_organize_et(tmp_path, dry_run=False)

    sonuc = geri_al(tmp_path)

    assert sonuc == 0
    assert (tmp_path / "tatil.jpg").is_file()
    assert (tmp_path / "rapor.pdf").is_file()
    # Boş kalan kategori klasörleri temizlenmeli
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / "Documents").exists()
    # Log dosyası silinmeli
    assert not (tmp_path / LOG_DOSYASI).exists()


def test_geri_al_log_yoksa_hata_doner(tmp_path):
    sonuc = geri_al(tmp_path)
    assert sonuc == 1


def test_organize_ve_geri_al_dongusu(tmp_path):
    # Tam bir döngü: düzenle -> geri al -> orijinal durum
    isimler = ["a.jpg", "b.pdf", "c.py", "d.xyz"]
    for isim in isimler:
        _dosya_olustur(tmp_path, isim, icerik=isim)

    klasor_organize_et(tmp_path, dry_run=False)
    geri_al(tmp_path)

    for isim in isimler:
        assert (tmp_path / isim).read_text(encoding="utf-8") == isim
