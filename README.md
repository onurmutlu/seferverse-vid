# SeferVerse VID

SeferVerse için yapay zekâ destekli, sinematik pitch/video üretim deposu. Tamamen Markdown odaklı içerik + otomasyon scriptleri ile çalışır. CapCut’a hazır sahne export’ları üretir; Runway/Sora ve ElevenLabs entegrasyonlarıyla gerçek üretime geçebilir.

- **Durum**: Aktif
- **Sahipler**: Onur (Tech), Taylan (Biz/Strategy)
- **Tarih**: 2025-08-11

## Hızlı Başlangıç
```bash
git clone <YOUR_REPO_URL> seferverse-vid
cd seferverse-vid
chmod +x setup_pipeline.sh && ./setup_pipeline.sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### DRY-RUN (mock üretim)
```bash
python pipeline/scripts/story_to_video.py --limit 3
```

### Gerçek çağrılar (anahtarlarla)
```bash
# .env içine anahtarları doldurun
python pipeline/scripts/story_to_video.py --limit 3 --real --engine runway  # veya --engine sora
```

## Proje Yapısı (öz)
- `pipeline/` — otomasyon akışı
  - `scripts/` — Python/Bash scriptleri (ana giriş: `story_to_video.py`)
  - `stories/` — senaryo/hikâye .md dosyaları (girdi)
  - `voices/` — sahne WAV/MP3 (çıktı)
  - `videos/` — sahne MP4 (çıktı)
  - `prompts/` — sahne prompt şablonları
  - `logs/` — `pipeline.log`
  - `export/capcut/` — CapCut’a hazır paket (assets + subtitles + manifest)
- `canon/`, `visual/`, `audio/`, `tech/`, `pitch/`, `prompts/` — bilgi tabanı

## .env Anahtarları
```dotenv
# === API KEYS ===
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
RUNWAY_API_KEY=
SORA_API_KEY=

# === OPTIONS ===
OPENAI_MODEL=gpt-4o-mini
ELEVENLABS_VOICE_ID=           # (veya) ELEVENLABS_VOICE_NAME=Adam
RUNWAY_BASE=https://api.dev.runwayml.com/v1
RUNWAY_AUTH_HEADER=Authorization
RUNWAY_AUTH_PREFIX=Bearer
RUNWAY_VERSION=2024-11-06
RUN_ENGINE=runway              # runway | sora
```

## Kullanım Akışı
1) `pipeline/stories/` altındaki `.md` hikâyeyi düzenle (her madde bir sahne)
2) `python pipeline/scripts/story_to_video.py --limit N` çalıştır
3) Çıktılar:
   - `pipeline/voices/scene_XX.(wav|mp3)`
   - `pipeline/videos/scene_XX.mp4`
   - CapCut export: `pipeline/export/capcut/` (assets, subtitles, manifest, m3u)

## CapCut’a Hazır Export
- Videolar: `export/capcut/assets/videos/scene_XX.mp4`
- Sesler: `export/capcut/assets/voices/scene_XX.(wav|mp3)`
- Altyazı: `export/capcut/subtitles/scene_XX.srt`
- Manifest: `export/capcut/manifest_capcut.csv`
- Hızlı sıralı izleme: `export/capcut/cuts/rough_timeline.m3u`

## Gerçek Entegrasyonlar
- ElevenLabs (TTS): `.env`’de `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID` (panelden voice_id) veya `ELEVENLABS_VOICE_NAME`
- Runway (Video): `.env`’de `RUNWAY_BASE`, `RUNWAY_VERSION`, `Authorization: Bearer <API_KEY>` — dev/stable versiyona göre
- Sora: placeholder; aynı arayüzle devreye alınır

## Örnek Hikâye (Smolensk — 5 Sahne)
`pipeline/stories/sample.md` içeriği örnektir:

```
# Smolensk Sprint — Teaser (5 Sahne, Genişletilmiş)

- **Sahne 1 — Yağmur Altında Bekleyiş:**  
  Gri bulutların altında ince ama inatçı bir yağmur… yaklaşan bir değişimin habercisi.

- **Sahne 2 — Kodun Nabzı:**  
  Monitörde Gnosis Safe multi-sig… her tıklama kaderin bir halkası.

- **Sahne 3 — Köprü Üzerindeki Yarış:**  
  Trenin ön camından hızlanan raylar… yeni bir başlangıca giden sisli ufuk.

- **Sahne 4 — Dubai’nin İki Yüzü:**  
  Çölden neon geceye; kamera toplantı odasına yaklaşır, karar anı.

- **Sahne 5 — Eşik:**  
  Kapı aralanır; tek adım, perde siyaha… kalp atışı ve sessizlik.
```

## Sık Sorunlar
- ffmpeg yok: `brew install ffmpeg`
- ElevenLabs 404: `ELEVENLABS_VOICE_ID` geçerli değil → panelden gerçek voice_id (UUID benzeri) kopyala veya `ELEVENLABS_VOICE_NAME` kullan
- Runway 401: `Authorization: Bearer <API_KEY>` ve doğru `RUNWAY_BASE`/`RUNWAY_VERSION` ayarlarını kontrol et
- Dev API 400 “version invalid”: `.env`’de `RUNWAY_VERSION`’ı dokümandaki güncel tarihle güncelle (örn. `2024-11-06`)

## Lisans
MIT — bkz. [LICENSE](LICENSE)
