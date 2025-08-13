# lightweight Runway client – placeholder
import os, time, requests


class RunwayClient:
    def __init__(self):
        self.base = os.getenv("RUNWAY_BASE", "https://api.runwayml.com/v1")
        self.key = os.getenv("RUNWAY_API_KEY", "")
        self.poll = int(os.getenv("RUNWAY_POLL_SEC", "6"))
        self.auth_style = os.getenv("RUNWAY_AUTH_STYLE", "bearer").lower()  # bearer | api-key
        # Dev API: text_to_video | text_to_image; durum: /tasks/{id}
        self.generate_path = os.getenv("RUNWAY_GENERATE_PATH", "/text_to_video")
        self.status_path = os.getenv("RUNWAY_STATUS_PATH", "/tasks/{id}")
        self.debug = os.getenv("RUNWAY_DEBUG", "0").lower() in {"1","true","yes","on"}
        # Tam esnek başlık: RUNWAY_AUTH_HEADER=Authorization, RUNWAY_AUTH_PREFIX=Bearer
        self.custom_header = os.getenv("RUNWAY_AUTH_HEADER", "").strip()
        self.custom_prefix = os.getenv("RUNWAY_AUTH_PREFIX", "").strip()
        # API versiyonu ve aday listesi
        self.version = os.getenv("RUNWAY_VERSION", "").strip()
        candidates = os.getenv("RUNWAY_VERSION_CANDIDATES", "").strip()
        self.version_candidates = [v.strip() for v in candidates.split(",") if v.strip()] or [
            "2024-11-01",
            "2024-10-01",
            "2024-09-01",
            "2024-06-01",
        ]

    def _hdr(self):
        base = {"Accept": "application/json", "Content-Type": "application/json"}
        # Versiyon header'ı (dev API gerektiriyor)
        version = self.version or self.version_candidates[0]
        base.update({"X-Runway-Version": version})
        if self.custom_header:
            value = f"{self.custom_prefix} {self.key}".strip()
            base.update({self.custom_header: value})
            return base
        if self.auth_style == "api-key":
            base.update({"Runway-API-Key": self.key})
        elif self.auth_style == "x-api-key":
            base.update({"X-API-Key": self.key})
        elif self.auth_style == "api-key-generic":
            base.update({"Api-Key": self.key})
        elif self.auth_style == "token":
            base.update({"Authorization": f"Token {self.key}"})
        elif self.auth_style == "x-runway-api-key":
            base.update({"X-Runway-API-Key": self.key})
        else:
            base.update({"Authorization": f"Bearer {self.key}"})
        return base

    def generate(self, prompt, seconds=6, seed=None, webhook=None):
        if not self.key:
            raise RuntimeError("RUNWAY_API_KEY yok")
        # Payload şeması path'e göre değişir
        model = os.getenv("RUNWAY_MODEL", "gen3")
        ratio = os.getenv("RUNWAY_RATIO", "1920:1080")
        if "text_to_image" in self.generate_path:
            payload = {
                "model": model,
                "ratio": ratio,
                "promptText": prompt,
            }
        else:  # text_to_video (varsayılan)
            payload = {
                "model": model,
                "ratio": ratio,
                "promptText": prompt,
                "duration": seconds,
            }
        if seed is not None:
            payload["seed"] = seed
        webhook_url = webhook or os.getenv("RUNWAY_WEBHOOK_URL") or None
        if webhook_url:
            payload["webhook_url"] = webhook_url
        # NOTE: gerçek endpoint/properties hesap türüne göre değişebilir
        url = f"{self.base.rstrip('/')}{self.generate_path}"
        tried = []
        # Eğer özel header verildiyse, sadece versiyon adayları üzerinden dene
        if self.custom_header:
            tried_vers = []
            versions_to_try = [self.version] if self.version else []
            versions_to_try += [v for v in self.version_candidates if v not in versions_to_try]
            r = None
            for ver in versions_to_try:
                self.version = ver
                tried_vers.append(ver)
                if self.debug:
                    print(f"[runway] POST {url} header={self.custom_header} prefix={self.custom_prefix} ver={ver}")
                r = requests.post(url, headers=self._hdr(), json=payload, timeout=60)
                if r.status_code == 400 and ("Version" in (r.text or "") or "version" in (r.text or "")):
                    continue
                break
            if r is None:
                raise RuntimeError("Runway generate failed: no response")
        else:
            for style in [self.auth_style, "bearer", "token", "api-key", "x-api-key", "api-key-generic", "x-runway-api-key"]:
                self.auth_style = style
                tried.append(style)
                for ver in self.version_candidates:
                    self.version = ver
                    if self.debug:
                        key_len = len(self.key or "")
                        print(f"[runway] POST {url} auth={style} key_len={key_len} ver={ver}")
                    r = requests.post(url, headers=self._hdr(), json=payload, timeout=60)
                    # 401 -> auth stili değiştir, 400 versiyon hatası -> sonraki versiyon
                    if r.status_code == 401:
                        break
                    if r.status_code == 400 and ("Version" in (r.text or "") or "version" in (r.text or "")):
                        continue
                    break
                if r.status_code != 401:
                    break
        if not r.ok:
            snippet = r.text[:400] if r.text else ""
            raise RuntimeError(f"Runway generate failed: status={r.status_code} body={snippet} tried={tried} ver={self.version}")
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return (data.get("id") or data.get("generation_id") or data.get("task_id"))

    def wait_and_download(self, gen_id, out_path):
        while True:
            url = f"{self.base.rstrip('/')}{self.status_path.format(id=gen_id)}"
            if self.debug:
                print(f"[runway] GET {url}")
            r = requests.get(url, headers=self._hdr(), timeout=30)
            if not r.ok:
                snippet = r.text[:400] if r.text else ""
                raise RuntimeError(f"Runway status failed: status={r.status_code} body={snippet}")
            st = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            status = st.get("status") or st.get("state")
            out_url = st.get("output_url") or st.get("asset_url") or st.get("result", {}).get("url")
            if status in ("succeeded", "completed", "done") and out_url:
                vid = requests.get(out_url, timeout=300)
                with open(out_path, "wb") as f:
                    f.write(vid.content)
                return out_path
            if status in ("failed", "canceled", "error"):
                raise RuntimeError(f"Runway failed: {st}")
            time.sleep(self.poll)

