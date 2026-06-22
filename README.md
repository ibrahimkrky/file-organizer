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

- Python 3.8+
- Ek bağımlılık yok (yalnızca standart kütüphane kullanılır)

## Kullanım

```bash
# Bir klasördeki dosyaları düzenle
python organize.py /yol/klasor

# Önce ne olacağını gör (hiçbir şey taşınmaz)
python organize.py /yol/klasor --dry-run
```

`~` kısayolu desteklenir:

```bash
python organize.py ~/İndirilenler --dry-run
```

## Özellikler

- **`--dry-run`**: Gerçekten taşımadan hangi dosyanın nereye gideceğini gösterir.
- **Türkçe çıktılar**: Her işlem için açıklayıcı mesajlar verir.
- **Güvenli taşıma**: Aynı isimde dosya varsa üzerine yazmaz; `dosya_1.txt` gibi benzersiz isim üretir.
- **Alt klasörlere dokunmaz**: Yalnızca hedef klasörün doğrudan içindeki dosyaları düzenler.

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
