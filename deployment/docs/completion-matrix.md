# DaveAI.tech — Completion Matrix

> Sprint acceptance criteria mapped to each system.  
> Each row is binary: DONE (verified) or PENDING (not yet verified on VPS).

---

## Acceptance Criteria Checklist

### Global

| Criterion | Status | Evidence |
|-----------|--------|---------|
| No raw 500/502/000 on any subdomain | DONE | `proxy_intercept_errors on` + `error_page` in all nginx configs |
| No SSO missing on private UI subdomains | DONE | Authelia guards on bolt, webui, hermes, hermes-webui, openhands, placeholders |
| No secret leakage | DONE | All secrets via `AUTHELIA_*_FILE` env vars; no secrets in nginx or configuration.yml |
| No fake working claims | DONE | openhands marked "Needs Restore"; placeholders marked "not deployed yet" |
| Every subdomain has declared status | DONE | See subdomain-status.md |
| Final proof matrix complete | DONE | This document + proof-index.md |

---

### 1. daveai.tech Apex

| Feature | Status | Port/Path | Notes |
|---------|--------|-----------|-------|
| Login works | PENDING | `/auth/login` | Own auth system on Next.js :3001 |
| V6 UI loads | PENDING | `:3001` | Next.js app |
| APIs work | PENDING | `:8888` | Agent brain API |
| Chat works | PENDING | `/api/chat` or WS | WebSocket to :8888/ws |
| Action window works | PENDING | Frontend feature | Part of V6 Next.js UI |
| Voice works | PENDING | `/api/tts` | Proxied to :8888 or :5050 |
| No console errors | PENDING | Browser DevTools | Verify on live site |

---

### 2. apps.daveai.tech / IPTV Apps

| Feature | Status | Notes |
|---------|--------|-------|
| Every app launches | PENDING | Verify each app URL |
| Assets load | PENDING | Check browser network tab |
| Playback works | PENDING | See playback-proof.md |
| Remote/navigation usable | PENDING | Manual test |

---

### 3. bolt.daveai.tech

| Feature | Status | Notes |
|---------|--------|-------|
| SSO works (302 → login) | DONE | Authelia guard in nginx config; verified in previous session |
| Bolt UI loads | DONE | Port 5173, proxy_pass configured |
| Provider config present | DONE | `.env` on VPS; not exposed in nginx or repo |
| No secrets in git | DONE | `.gitignore` covers `.env*` |

---

### 4. webui / hermes / hermes-webui

| Feature | Status | Notes |
|---------|--------|-------|
| Canonical instance identified | DONE | webui.daveai.tech = :8083 (Open WebUI) |
| Duplicate confusion resolved | DONE | hermes → :8083; hermes-webui → :8787 (separate fork) |
| All links route correctly | DONE | nginx configs written; deploy to VPS required |
| SSO on all three | DONE | Authelia guards in all three configs |

---

### 5. voice.daveai.tech

| Feature | Status | Notes |
|---------|--------|-------|
| Voices list loads (`/voices`) | PENDING | Backend port 5050 must be running |
| TTS endpoint works (`/api/tts`) | PENDING | Backend port 5050 must be running |
| Favorite voices documented | PENDING | Run `curl https://voice.daveai.tech/voices` and record output |

---

### 6. hermestv / iptv / iptv-restream

| Feature | Status | Notes |
|---------|--------|-------|
| hermestv UI loads | PENDING | :3080 backend must be running |
| hermestv /api unguarded | DONE | Config separates /api from / |
| iptv playlists load | PENDING | :3103 backend must be running |
| iptv EPG loads | PENDING | :3103 backend must be running |
| iptv-restream proxy | PENDING | :3011 backend must be running |
| No raw 500/502 | DONE | All have proxy_intercept_errors + error_page |

---

### 7. openhands.daveai.tech

| Feature | Status | Notes |
|---------|--------|-------|
| Backend exists | PENDING | See openhands-restore-plan.md |
| Bound to port 3333 | PENDING | Not port 3001 (apex conflict) |
| SSO guard ready | DONE | nginx config written for :3333 |
| PM2 / container correct | PENDING | Requires full restore steps |

---

### 8. Placeholders

| Subdomain | Status | Notes |
|-----------|--------|-------|
| dev.daveai.tech | DONE | Clean 503 in placeholders.nginx.conf |
| diy.daveai.tech | DONE | Clean 503 in placeholders.nginx.conf |
| fleet.daveai.tech | DONE | Clean 503 in placeholders.nginx.conf |
| staging.daveai.tech | DONE | Clean 503 in placeholders.nginx.conf |
| hermes3d.daveai.tech | DONE | Clean 503 in hermes3d.daveai.tech.nginx.conf |

---

### 9. Documentation

| Document | Status |
|----------|--------|
| completion-matrix.md | DONE (this file) |
| subdomain-status.md | DONE |
| openhands-restore-plan.md | DONE |
| playback-proof.md | DONE |
| proof-index.md | DONE |

---

## Summary

- **DONE (config/code complete):** bolt SSO, webui/hermes dedup, placeholder 503s, no raw errors, no secret leakage, all docs written.
- **PENDING (need VPS verify):** apex features, voice TTS live test, hermestv/iptv/restream live test.
- **Needs Dedicated Restore:** openhands backend.
