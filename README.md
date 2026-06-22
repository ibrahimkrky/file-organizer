# File Organizer (organize.py)

Bir klasördeki dosyaları **uzantılarına göre** alt klasörlere taşıyan basit bir Python CLI aracı.

## Kategoriler

| Klasör | Örnek uzantılar |
|------------|------------------------------------------------|
| `Images` | jpg, png, gif, webp, svg, heic … |
| `Documents`| pdf, docx, txt, xlsx, pptx, csv, md … |
| `Videos` | mp4, mkv, mov, avi, webm … |
| `Audio` | mp3, wav, flac, aac, m4a … |
| `Archives` | zip, rar, 7z, tar, gz … |
| `Code` | py, js, ts, java, html, css, json, yaml … |
| `Others` | Yukarıdakilere uymayan tüm dosyalar |

## Gereksinimler

- Python 3.9+
- Aracın kendisi ek bağımlılık gerektirmez (yalnızca standart kütüphane kullanılır).
- Testleri çalıştırmak için `pytest` gerekir (bkz. `requirements.txt`).

## Kullanım

```bash
# Bir klasördeki dosyaları düzenle
python organize.py /yol/klasor

# Önce ne olacağını gör (hiçbir şey taşınmaz)
python organize.py /yol/klasor --dry-run

# Son düzenlemeyi geri al
python organize.py /yol/klasor --undo
```

`~` kısayolu desteklenir:

```bash
python organize.py ~/İndirilenler --dry-run
```

## Özellikler

- **`--dry-run`**: Gerçekten taşımadan hangi dosyanın nereye gideceğini gösterir.
- **`--undo`**: Son düzenlemeyi geri alır. Her düzenlemede yapılan taşımalar hedef
  klasördeki `.organize_log.json` dosyasına kaydedilir; `--undo` bu kaydı okuyarak
  dosyaları eski yerlerine taşır ve boşalan kategori klasörlerini temizler.
- **Türkçe çıktılar**: Her işlem için açıklayıcı mesajlar verir.
- **Güvenli taşıma**: Aynı isimde dosya varsa üzerine yazmaz; `dosya_1.txt` gibi benzersiz isim üretir.
- **Alt klasörlere dokunmaz**: Yalnızca hedef klasörün doğrudan içindeki dosyaları düzenler.

## Geri alma (undo) nasıl çalışır?

Düzenleme yapıldığında, taşınan her dosyanın eski ve yeni konumu hedef klasördeki
`.organize_log.json` dosyasına yazılır. `--undo` çalıştırıldığında:

1. Log dosyası okunur ve taşımalar **ters sırada** geri alınır.
2. Orijinal konumda artık başka bir dosya varsa üzerine yazılmaz; benzersiz isim üretilir.
3. Boşalan kategori klasörleri silinir.
4. İşlem sonunda log dosyası silinir.

> Not: Yalnızca **en son** düzenleme geri alınabilir; her düzenleme önceki logun üzerine yazar.

## Testler

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Testleri çalıştır
pytest
```

Testler geçici klasör (`tmp_path`) kullanır; gerçek dosyalarınıza dokunmaz.

## Örnek çıktı

```
TASLAK modu: '/home/ibrahim/İndirilenler' klasörü için planlanan işlemler:

  [TASLAK] 'tatil.jpg' -> Images/
  [TASLAK] 'rapor.pdf' -> Documents/
  [TASLAK] 'organize.py' -> Code/

Özet (taslak): 3 dosya taşınacaktı. Hiçbir değişiklik yapılmadı.
```

## Lisans

MIT
