# Blueprint 3 – ChatGPT Revizyonu

## Genel Hüküm
Claude’un “Yönetmen Kafası” güçlü bir çekirdek oluşturmuş; 3 perdeli ikna mimarisi, sahne/AI araç dağıtımı, saatlik teslim planı ve post prodüksiyon detayları çok net. Bu versiyon, teknik riskleri azaltan ve post estetiğini optimize eden revizyonları içerir.

---

## Güçlü Yanlar (Dokunma)
- **İlk 7 saniye “otorite” kotası:** Kroşe ile yağmur efekti → metin morfu → kanca.
- **Teknik kanıt üçlüsü:** Kod otoritesi → işlem onayı → ağ montajı; 0:26 / 0:44 / 1:12 vuruşları kilitli.
- **Sessizlik silahı:** 1:26-1:27 “mutlak durak”; final 2:01 kısa sessizlik.
- **48 saatlik üretim şeması:** Saat blokları, format matrisi, QR test adımı.

---

## Revizyon Maddeleri

1. **Sora bağımlılığını yedekle**  
   - Sora gerektiren 2, 9, 12. sahneler için Runway + AE 2.5D kamera rig yedekleri hazırla.
   - Alternatif timecode eşleşmesini koru.

2. **Film Grain & Chromatic Aberration Dozu**  
   - Film grain: %8–10
   - Chromatic aberration: ≤1px

3. **Peak Headroom**  
   - Master tepe: **-1 dB TRUE PEAK**
   - Hedef: **-16 LUFS**
   - Oversampled true-peak ölçümü final export sonrası yap.

4. **Renk Yönetimi**  
   - Rec.709 + Gamma 2.4 / D65
   - Tek LUT/Node zinciri, soğuk→sıcak geçiş node 2’de yapılmalı.

5. **VO İki Dil Varyantı**  
   - Adam (EN/TR aksan) + Türkçe net diksiyonlu yedek.
   - Aynı timecode, ayrı M&E export.

6. **Gerçek Ekran İçeriği**  
   - Gnosis Safe ekran kaydı, Tenderly webhook ve testnet tx kullan.
   - Cüzdan adresi / tx hash’leri kısmi maskeli.

7. **QR Kod Güvenilirliği**  
   - H=~30, M hata toleransı.
   - Redirect URL kullan, kontrast testi yap.

8. **Sayaç Tonlaması**  
   - Mekanik tik: -9 dB (2:16–2:30)
   - 2:25 kırmızı shift ile +1.5 dB yükselt.

---

## Sahne Başına Mikro Notlar
- **0:03–0:15:** Lens flare + yağmur overlay banding yapmasın, dither ekle.
- **0:26–0:35:** Parçacık yoğunluğu %15–20’de tut, UI okunurluğu korunmalı.
- **1:26–1:40:** Kalp atışı -28 LUFS, horn @1:35 -12 dB.
- **1:41–2:00:** Runway plate + AE crane-up yedeği hazır; güneş ışını 85 IRE soft knee.

---

## 48 Saatlik “Tamamla” Kontrol Listesi
1. Sora sahneleri için Runway/AE B-plan render seti.
2. VO çift paket (TR/EN) + ayrı M&E export.
3. QR kod testleri (farklı cihazlarda tarama + redirect).
4. Audio master kontrol: -1 dBTP, -16 LUFS.
5. Tek LUT ile renk tutarlılığı.

---

## Sonuç
Bu revizyon, orijinal blueprint’in dramatik gücünü koruyarak teknik riskleri minimize eder ve platform uyumluluğunu artırır. Blueprint 3, Claude’a “Revizyon Görevi” olarak verilmeye hazırdır.
