# IPTV Proof — iptv.daveai.tech

**Date:** 2026-05-30  
**VPS:** 187.77.30.206

---

## Service Stack

```
iptv.daveai.tech (nginx :443)
    ↓
VPS nginx → 127.0.0.1:3103
    ↓
iptv-restream-iptv_restream_nginx-1 (nginx:alpine, Docker)
    ├── / → iptv-restream-iptv_restream_frontend-1 :80
    ├── /api/ → iptv-restream-iptv_restream_backend-1 :5000
    ├── /socket.io/ → backend :5000
    └── /proxy/ → backend :5000
```

---

## Containers

| Container | Image | Status |
|-----------|-------|--------|
| iptv-restream-iptv_restream_nginx-1 | nginx:alpine | Up 6 days |
| iptv-restream-iptv_restream_backend-1 | custom Node.js | Up 6 days |
| iptv-restream-iptv_restream_frontend-1 | custom | Up 40 hours |

---

## Proven Endpoints

```
curl https://iptv.daveai.tech/ → HTTP 200 ✅
curl http://172.21.0.4:5000/api/channels → HTTP 200 ✅
```

---

## The /playlist 404 — Explanation (Not a Bug)

The audit initially flagged `https://iptv.daveai.tech/playlist` as 404. After inspecting the backend source:

- `PlaylistService.js` manages playlists as internal data objects stored in `/channels/<name>.txt`
- Playlists are added/managed through the UI via `/api/channels` CRUD operations
- There is **no `/playlist.m3u` HTTP download route** in the backend source
- The app is designed as an **IPTV restreamer UI**, not a plain M3U server
- `/playlist` returning 404 is correct behavior — it's not a defined route

**Not a bug. Architecture is by design.**

---

## Remaining

1. Access `https://iptv.daveai.tech/` in browser — verify UI loads
2. Add a test M3U playlist URL via the UI
3. Verify channel list populates at `/api/channels`
4. Test stream/playback of at least one channel
5. Capture screenshot as proof
