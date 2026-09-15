# DaveAI.tech — Playback Proof Log

> This file documents verified playback tests for media-related services.  
> Each entry must include: date, method (curl/browser/player), URL tested, result.  
> Unverified claims are marked PENDING — run the test and fill in the result.

---

## Format

```
### <subdomain> — <feature>
- **Date:** YYYY-MM-DD
- **Method:** curl | browser | VLC | Kodi
- **URL:** https://...
- **Result:** HTTP <code> | stream started | error message
- **Proof:** screenshot path or curl output snippet
```

---

## iptv.daveai.tech

### Playlist endpoint

- **Date:** PENDING
- **Method:** `curl -s -o /dev/null -w '%{http_code}' https://iptv.daveai.tech/playlist`
- **URL:** `https://iptv.daveai.tech/playlist`
- **Result:** PENDING
- **Proof:** PENDING

### EPG endpoint

- **Date:** PENDING
- **Method:** `curl -s -o /dev/null -w '%{http_code}' https://iptv.daveai.tech/epg`
- **URL:** `https://iptv.daveai.tech/epg`
- **Result:** PENDING
- **Proof:** PENDING

### Playback via VLC

- **Date:** PENDING
- **Method:** VLC → Open Network → `https://iptv.daveai.tech/playlist`
- **Result:** PENDING
- **Proof:** Screenshot pending

---

## iptv-restream.daveai.tech

### Restream proxy

- **Date:** PENDING
- **Method:** `curl -s -o /dev/null -w '%{http_code}' https://iptv-restream.daveai.tech/`
- **URL:** `https://iptv-restream.daveai.tech/`
- **Result:** PENDING
- **Proof:** PENDING

### Stream playback

- **Date:** PENDING
- **Method:** VLC or ffplay targeting a stream URL
- **Result:** PENDING
- **Proof:** PENDING

---

## hermestv.daveai.tech

### Web UI

- **Date:** PENDING
- **Method:** Browser → `https://hermestv.daveai.tech/`
- **Result:** PENDING
- **Proof:** Screenshot pending

### API endpoint

- **Date:** PENDING
- **Method:** `curl -s https://hermestv.daveai.tech/api/`
- **Result:** PENDING
- **Proof:** PENDING

### TTS speak

- **Date:** PENDING
- **Method:** `curl -s -X POST https://hermestv.daveai.tech/api/tts/speak -d '{"text":"hello"}'`
- **Result:** PENDING
- **Proof:** PENDING

---

## voice.daveai.tech

### Voices list

- **Date:** PENDING
- **Method:** `curl -s https://voice.daveai.tech/voices`
- **Expected:** JSON array of voice objects
- **Result:** PENDING
- **Proof:** PENDING

### TTS synthesis

- **Date:** PENDING
- **Method:** `curl -s -X POST https://voice.daveai.tech/api/tts -H 'Content-Type: application/json' -d '{"text":"Hello from DaveAI","voice":"en-US-default"}' -o /tmp/tts-test.mp3`
- **Result:** PENDING — check `/tmp/tts-test.mp3` size > 0
- **Proof:** PENDING

### Favorite voices

> Fill in after running `/voices` endpoint:

| Voice ID | Name | Language | Notes |
|----------|------|----------|-------|
| PENDING | — | — | — |

---

## daveai.tech Apex — Voice Feature

### In-app voice

- **Date:** PENDING
- **Method:** Browser → `https://daveai.tech` → voice button in V6 UI
- **Result:** PENDING
- **Proof:** Screenshot pending

---

## apps.daveai.tech

### App launch

- **Date:** PENDING
- **Method:** Browser → each app URL
- **Result:** PENDING
- **Proof:** Screenshot pending for each app

### Asset loading

- **Date:** PENDING
- **Method:** Browser DevTools → Network tab → 0 failed requests
- **Result:** PENDING

---

## How to Update This File

After running each test:

1. Replace `PENDING` with the actual result.
2. Save a screenshot to `deployment/docs/screenshots/` and link it here.
3. Commit with message: `proof: <subdomain> <feature> verified YYYY-MM-DD`
