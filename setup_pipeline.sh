#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$ROOT/pipeline"/{stories,voices,videos,prompts,logs,scripts,tracker,assets}
touch "$ROOT/pipeline"/{stories,voices,videos,prompts,logs,scripts,tracker,assets}/.gitkeep

# .env.example
cat > "$ROOT/.env.example" <<'ENV'
# === API KEYS ===
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
RUNWAY_API_KEY=

# === OPTIONS ===
OPENAI_MODEL=gpt-4o-mini
ELEVENLABS_VOICE_ID=Adam
RUNWAY_MODEL=gen3
PROJECT_NAME=SeferVerse VID
ENV

# requirements
cat > "$ROOT/requirements.txt" <<'REQ'
python-dotenv==1.0.1
requests==2.32.3
pydub==0.25.1
moviepy==1.0.3
REQ

# README
mkdir -p "$ROOT/pipeline"
cat > "$ROOT/pipeline/README.md" <<'MD'
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

MD

# örnek hikaye

cat > "$ROOT/pipeline/stories/sample.md" <<'STORY'

# Smolensk Sprint — Teaser

* Köprü metaforu, yağmurlu sınır kapısı
* Kod yazımı, Gnosis Safe multi-sig proof
* Dubai timelapse → tren metaforu
STORY

echo "✅ Klasörler ve başlangıç dosyaları oluşturuldu."
