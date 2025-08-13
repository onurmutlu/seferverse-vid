#!/usr/bin/env python3
import os, sys, argparse, random, subprocess, shutil
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
import imageio

ROOT = Path(__file__).resolve().parents[2]
PL = ROOT / "pipeline"
STORIES = PL / "stories"
VOICES = PL / "voices"
VIDEOS = PL / "videos"
LOGS = PL / "logs"
PROMPTS = PL / "prompts"
ASSETS = PL / "assets"

LOG_FILE = LOGS / "pipeline.log"

def log(msg: str) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg, flush=True)

def load_story() -> str:
    md_files = sorted(STORIES.glob("*.md"))
    if not md_files:
        raise FileNotFoundError("pipeline/stories altında .md hikaye yok.")
    return md_files[0].read_text(encoding="utf-8")

def simple_scene_split(text: str, max_scenes: int = 5):
    lines = [l.strip("-• ").strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    scenes = [l for l in lines if len(l) > 0][:max_scenes]
    if not scenes:
        scenes = ["Opening visual", "Tech proof", "Dubai vision", "Binary choice", "Finale"]
    return scenes

def has_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def mock_tts_wav(out_path: Path, seconds: float = 3.0) -> Path:
    import wave
    sr = 16000
    t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
    freq = 440.0
    envelope = np.exp(-3 * t)
    signal = 0.2 * np.sin(2 * np.pi * freq * t) * envelope
    pcm = (signal * 32767.0).astype(np.int16)
    VOICES.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return out_path

def _resolve_elevenlabs_voice_id() -> str:
    key = os.getenv("ELEVENLABS_API_KEY", "")
    if not key:
        return ""
    vid = os.getenv("ELEVENLABS_VOICE_ID", "").strip()
    vname = os.getenv("ELEVENLABS_VOICE_NAME", "").strip()
    # Varsayılan: kullanıcı ELEVENLABS_VOICE_ID verdiyse doğrudan onu kullan
    if vid:
        return vid
    try:
        import requests
        headers = {"xi-api-key": key}
        r = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=30)
        if not r.ok:
            return vid  # en kötü eldeki değer döner
        data = r.json() or {}
        voices = data.get("voices", [])
        # Önce isimle çözümle
        if vname:
            for v in voices:
                if str(v.get("name", "")).lower() == vname.lower():
                    return v.get("voice_id", vid)
        # Sonra 'vid' adı olarak eşleştirmeyi dene
        if vid:
            for v in voices:
                if str(v.get("name", "")).lower() == vid.lower():
                    return v.get("voice_id", vid)
        # fallback: ilk uygun ses
        if voices:
            return voices[0].get("voice_id", vid)
        return vid
    except Exception:
        return vid

def elevenlabs_tts(text: str, voice_base: Path) -> Path:
    key = os.getenv("ELEVENLABS_API_KEY", "")
    if not key:
        return mock_tts_wav(voice_base.with_suffix(".wav"))

    import requests
    voice_id = _resolve_elevenlabs_voice_id()
    if not voice_id:
        log("ELEVENLABS_VOICE_ID/NAME çözümlenemedi; mock TTS.")
        return mock_tts_wav(voice_base.with_suffix(".wav"))
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": key, "accept": "audio/mpeg", "Content-Type": "application/json"}
    payload = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.4, "similarity_boost": 0.7}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.ok:
            mp3_path = voice_base.with_suffix(".mp3")
            mp3_path.write_bytes(r.content)
            # MP3 -> WAV çevir (ffmpeg varsa)
            if has_ffmpeg():
                wav_path = voice_base.with_suffix(".wav")
                try:
                    subprocess.run(["ffmpeg", "-y", "-i", str(mp3_path), str(wav_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    mp3_path.unlink(missing_ok=True)
                    return wav_path
                except Exception as e:
                    log(f"ffmpeg wav çevirme hatası: {e}. MP3 bırakıldı.")
            return mp3_path
        else:
            log(f"ElevenLabs error {r.status_code}: {r.text[:200]}")
            return mock_tts_wav(voice_base.with_suffix(".wav"))
    except Exception as e:
        log(f"ElevenLabs exception: {e}")
        return mock_tts_wav(voice_base.with_suffix(".wav"))

def mock_video_mp4(out_path: Path, duration: float = 5.0) -> Path:
    VIDEOS.mkdir(parents=True, exist_ok=True)
    fps = 24
    num_frames = max(1, int(duration * fps))
    try:
        writer = imageio.get_writer(str(out_path), fps=fps)
        for i in range(num_frames):
            r = int(127 + 127 * np.sin(2 * np.pi * i / num_frames))
            g = int(127 + 127 * np.sin(2 * np.pi * (i + num_frames / 3) / num_frames))
            b = int(127 + 127 * np.sin(2 * np.pi * (i + 2 * num_frames / 3) / num_frames))
            frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            frame[..., 0] = r
            frame[..., 1] = g
            frame[..., 2] = b
            writer.append_data(frame)
        writer.close()
    except Exception as e:
        log(f"Video yazım hatası (ffmpeg?): {e}. Boş dosya oluşturuluyor.")
        out_path.write_bytes(b"")
    return out_path

def runway_generate(prompt: str, out_video: Path, voice_path: Path | None = None) -> Path:
    key = os.getenv("RUNWAY_API_KEY", "")
    model = os.getenv("RUNWAY_MODEL", "gen3")
    if not key:
        log("Runway key yok → MOCK video.")
        return mock_video_mp4(out_video, duration=5)
    # Gerçek entegrasyon için basit placeholder: client mevcutsa kullan, yoksa mock
    try:
        # Dinamik import: çalışma zamanında sys.path'e repo kökünü ekle
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from pipeline.scripts.clients.runway_client import RunwayClient  # type: ignore
        cli = RunwayClient()
        gen_id = cli.generate(prompt=prompt, seconds=6)
        log(f"Runway gen_id={gen_id} → polling…")
        cli.wait_and_download(gen_id, out_video)
        if voice_path is not None:
            mux_audio_to_video(out_video, voice_path)
        return out_video
    except Exception as e:
        log(f"Runway REAL call error → MOCK: {e}")
        return mock_video_mp4(out_video, duration=5)

def sora_generate(prompt: str, out_video: Path) -> Path:
    key = os.getenv("SORA_API_KEY", "")
    model = os.getenv("SORA_MODEL", "text-to-video-v1")
    if not key:
        log("Sora key yok → MOCK video.")
        return mock_video_mp4(out_video, duration=5)
    log(f"Sora REAL call placeholder (model={model}). Prompt gönderildi → MOCK çıktı.")
    return mock_video_mp4(out_video, duration=5)

# --- CapCut export helpers ---
def ensure_capcut_dirs() -> Path:
    base = PL / "export" / "capcut"
    (base / "assets" / "videos").mkdir(parents=True, exist_ok=True)
    (base / "assets" / "voices").mkdir(parents=True, exist_ok=True)
    (base / "subtitles").mkdir(parents=True, exist_ok=True)
    (base / "cuts").mkdir(parents=True, exist_ok=True)
    return base

def _fmt_srt_time(t: float) -> str:
    ms = int((t - int(t)) * 1000)
    s = int(t) % 60
    m = (int(t) // 60) % 60
    h = int(t) // 3600
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def write_srt(text: str, duration_sec: float, out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        f.write("1\n")
        f.write(f"{_fmt_srt_time(0.0)} --> {_fmt_srt_time(max(0.01, duration_sec))}\n")
        f.write(text.strip() + "\n\n")

def append_manifest_row(manifest_csv: Path, row: list[str]) -> None:
    header = ("scene_id,timecode,voice,video,subtitle,vo_secs\n")
    if not manifest_csv.exists():
        manifest_csv.write_text(header, encoding="utf-8")
    with manifest_csv.open("a", encoding="utf-8") as f:
        f.write(",".join(row) + "\n")

def mux_audio_to_video(video_path: Path, audio_path: Path) -> None:
    # ffmpeg varsa sessiz videoya sesi bind eder
    if os.system("command -v ffmpeg >/dev/null 2>&1") == 0:
        tmp = str(video_path) + ".tmp.mp4"
        os.system(f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -shortest "{tmp}" >/dev/null 2>&1')
        shutil.move(tmp, video_path)

def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3, help="İlk N sahneyi üret")
    parser.add_argument("--real", action="store_true", help="(bilgi amaçlı; anahtar varsa gerçek çağrı denenir)")
    parser.add_argument("--engine", choices=["runway", "sora"], default=os.getenv("RUN_ENGINE", "runway"), help="Video motoru")
    args = parser.parse_args()

    PL.mkdir(parents=True, exist_ok=True)
    for p in [VOICES, VIDEOS, LOGS, PROMPTS, ASSETS]:
        p.mkdir(parents=True, exist_ok=True)

    story = load_story()
    scenes = simple_scene_split(story, max_scenes=args.limit)
    log(f"Scenes: {len(scenes)} -> {scenes}")
    log(f"Engine: {args.engine}")

    for idx, idea in enumerate(scenes, start=1):
        sid = f"{idx:02d}"
        prompt = f"Scene {sid}: {idea}\nStyle: cinematic, 16:9, 24fps, moody, teal/orange."
        (PROMPTS / f"scene_{sid}.txt").write_text(prompt, encoding="utf-8")

        # TTS
        voice_base = VOICES / f"scene_{sid}"
        log(f"[S{sid}] TTS")
        voice_path = elevenlabs_tts(f"{idea}. Köprü kurarız. Tren beklemez.", voice_base)

        # Video (placeholder)
        video_path = VIDEOS / f"scene_{sid}.mp4"
        log(f"[S{sid}] Video -> {video_path.name}")
        if args.engine == "runway":
            runway_generate(prompt, video_path, voice_path)
        else:
            sora_generate(prompt, video_path)

        # CapCut export
        capcut = ensure_capcut_dirs()
        cc_vid = capcut / "assets" / "videos" / video_path.name
        cc_vo = capcut / "assets" / "voices" / voice_path.name
        shutil.copy2(video_path, cc_vid)
        shutil.copy2(voice_path, cc_vo)
        # süre bul (WAV ise dalga, MP3 ise ffprobe ile tahmin edilebilir; basit yaklaşım)
        vo_dur = 3.0
        try:
            import wave
            if voice_path.suffix.lower() == ".wav":
                with wave.open(str(voice_path), "rb") as w:
                    frames = w.getnframes(); rate = w.getframerate()
                    vo_dur = frames / float(rate)
        except Exception:
            pass
        srt_path = capcut / "subtitles" / f"scene_{sid}.srt"
        write_srt(f"{idea}", vo_dur, srt_path)
        manifest_csv = capcut / "manifest_capcut.csv"
        append_manifest_row(
            manifest_csv,
            [sid, f"S{sid}", str(cc_vo), str(cc_vid), str(srt_path), f"{vo_dur:.2f}"]
        )
        m3u = capcut / "cuts" / "rough_timeline.m3u"
        with m3u.open("a", encoding="utf-8") as f:
            f.write(str(cc_vid) + "\n")

    log("✅ Pipeline tamamlandı.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
