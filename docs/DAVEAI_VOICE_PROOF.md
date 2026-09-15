# Voice API Proof — voice.daveai.tech

**Date:** 2026-05-30  
**VPS:** 187.77.30.206

---

## Service

- **Script:** `/opt/agent-brain/edge-tts-server.py`
- **Runtime:** Python venv at `/opt/agent-brain/venv`
- **Port:** `127.0.0.1:5050`
- **PM2 process:** id=3 `edge-tts` — status: online
- **Nginx:** `/etc/nginx/sites-enabled/voice.daveai.tech` → upstream `voice_edge_tts_backend`

---

## Bug Fixed (BUG-002)

Nginx config had `rewrite ^/api/(.*) /$1 break` which stripped the `/api/` prefix before forwarding to edge-tts. The backend only has `/api/*` routes — stripping the prefix caused all requests to 404.

**Fix:** Removed both rewrite lines. Backend now receives full path.

---

## Routes Available (from source)

| Method | Path                   | Description                     |
| ------ | ---------------------- | ------------------------------- |
| GET    | `/api/voices`          | List all voices (30 voices)     |
| GET    | `/api/voices/british`  | British voices only             |
| GET    | `/api/voices/all-edge` | All Azure edge voices           |
| GET    | `/api/agents/voices`   | Agent voice defaults            |
| GET    | `/api/tts/health`      | Health check                    |
| GET    | `/api/edge-tts/health` | Health check (alias)            |
| GET    | `/health`              | Direct health                   |
| POST   | `/api/tts`             | TTS synthesis (kokoro compat)   |
| POST   | `/api/edge-tts`        | TTS synthesis (edge-tts direct) |

---

## Proof

### 1. Backend Direct (port 5050)
```
curl http://127.0.0.1:5050/api/voices → HTTP 200
curl http://127.0.0.1:5050/api/tts/health → HTTP 200
curl http://127.0.0.1:5050/health → HTTP 200
```

### 2. Via Nginx (post-fix)
```
curl https://voice.daveai.tech/api/voices → HTTP 200
curl https://voice.daveai.tech/api/tts/health → HTTP 200
curl https://voice.daveai.tech/api/edge-tts/health → HTTP 200
```

### 3. Voices Response Sample
30 voices returned including:
- `bf_alice` → `en-GB-MaisieNeural` (DaveAI's voice persona)
- `af_heart` → `en-US-JennyNeural`
- `am_fenrir` → `en-US-GuyNeural`
- British female (11), British male (5), American female/male (14)

---

## TTS Audio Proven (2026-05-30)

### POST /api/edge-tts — WORKS ✅
```
curl -X POST https://voice.daveai.tech/api/edge-tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from DaveAI","voice":"en-GB-MaisieNeural"}'
→ HTTP 200 | 14,400 bytes audio
```

### POST /api/tts — 400 (wrong payload format)
The `/api/tts` kokoro-compat route requires different fields than `voice_id` + `text`. Use `/api/edge-tts` with `voice` field instead.

```bash
# Correct working TTS call:
curl -X POST https://voice.daveai.tech/api/edge-tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from DaveAI","voice":"en-GB-MaisieNeural"}' \
  --output maisie.mp3
# Returns: 14400+ bytes MP3 audio
```

## Status: ✅ Voice TTS proven working
