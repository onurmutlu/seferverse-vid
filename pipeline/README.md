# SeferVerse VID Pipeline

## Yapı
```

pipeline/
assets/    # logo, qr, sabit görseller
logs/      # pipeline.log
prompts/   # runway/sora/gpt prompt şablonları
scripts/   # python/bash scriptleri
stories/   # .md hikayeler (girdi)
tracker/   # üretim takip dosyaları
videos/    # sahne mp4 çıktıları
voices/    # sahne wav çıktıları

````

## Kurulum
```bash
cp .env.example .env   # anahtarları doldur
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
````

## Çalıştırma

```bash
python pipeline/scripts/story_to_video.py --limit 1          # DRY-RUN (mock)
python pipeline/scripts/story_to_video.py --limit 3 --real   # gerçek çağrılar (anahtarlar dolu olmalı)
```

## CapCut Export
- Export kökü: `pipeline/export/capcut/`
- Videolar: `assets/videos/scene_XX.mp4`
- Sesler: `assets/voices/scene_XX.(wav|mp3)`
- Altyazılar: `subtitles/scene_XX.srt`
- Manifest: `manifest_capcut.csv`
- Hızlı izleme listesi: `cuts/rough_timeline.m3u`

## .env Notları (özet)
```dotenv
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=           # (veya ELEVENLABS_VOICE_NAME=)
RUNWAY_API_KEY=
RUNWAY_BASE=https://api.dev.runwayml.com/v1
RUNWAY_AUTH_HEADER=Authorization
RUNWAY_AUTH_PREFIX=Bearer
RUNWAY_VERSION=2024-11-06
RUN_ENGINE=runway
```

