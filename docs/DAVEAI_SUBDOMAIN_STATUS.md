# DaveAI.tech — Subdomain Status

**Last checked:** 2026-05-30 21:32 UTC (live curl from VPS)

---

## daveai.tech
- **HTTP:** 200
- **Backend:** Next.js on :3001 (PM2 agentic-ui)
- **Status:** Working — needs proof
- **Checked:**
  - Root `/` → 200 ✅
  - `/api/health` → 200 ✅
  - `/api/chat` → 405 (GET on a POST-only route — not broken, just test was wrong method)
- **Remaining:** Manual browser check of full UI layout, action window, transcript, composer

---

## apps.daveai.tech
- **HTTP:** 302
- **Status:** Working — redirects. Target and content unverified.
- **Remaining:** Browser check of landing page and app links

---

## auth.daveai.tech
- **HTTP:** 200
- **Backend:** Authelia :8888
- **Status:** ✅ Working
- **Checked:** SSO login page loads at 200

---

## bolt.daveai.tech
- **HTTP:** 302
- **Backend:** Redirect (Bolt.DIY UI)
- **Status:** ✅ Working
- **Checked:** Redirects correctly

---

## webui.daveai.tech
- **HTTP:** 302
- **Backend:** Open WebUI :8083
- **Status:** ✅ Working
- **Checked:** Auth redirect (expected for Open WebUI)

---

## hermes.daveai.tech
- **HTTP:** 302
- **Backend:** Open WebUI :7860
- **Status:** ✅ Working
- **Checked:** Auth redirect (expected)

---

## hermes-webui.daveai.tech
- **HTTP:** 302
- **Backend:** Hermes WebUI :8787
- **Status:** ✅ Working
- **Checked:** Redirects (auth flow)

---

## voice.daveai.tech
- **HTTP:** 200
- **Backend:** edge-tts-server.py on :5050 (PM2)
- **Status:** ✅ Working — **FIXED 2026-05-30** (BUG-002)
- **Checked:**
  - Root `/` → 200 (voice landing page) ✅
  - `/api/voices` → 200 ✅ (30 voices returned)
  - `/api/tts/health` → 200 ✅
  - `/api/edge-tts/health` → 200 ✅
  - POST `/api/tts` → 400 (bad test payload — needs `voice_id` + `text`)
- **Remaining:** Test POST `/api/tts` with valid payload, verify audio binary response

---

## openhands.daveai.tech
- **HTTP:** 200
- **Backend:** Docker `openhands-app` :3333→3000
- **Status:** ✅ Working — **DEPLOYED 2026-05-30** (BUG-001 fixed)
- **Checked:**
  - Root `/` → 200 ✅
  - Local `http://127.0.0.1:3333/` → 200 ✅
  - Via nginx `--resolve` → 200 ✅
  - `docker ps` → Up ✅
  - LLM: LiteLLM proxy → `openai/deepseek-chat` ✅
- **Remaining:** Submit a test agent task to confirm LLM executes (not just UI loads)

---

## hermestv.daveai.tech
- **HTTP:** 200
- **Backend:** hermestv-vps-web :3080 + hermestv-vps-api :3011
- **Status:** ✅ Working
- **Checked:**
  - Root `/` → 200 ✅
  - `/api/health` → 200 ✅
  - Local `http://127.0.0.1:3011/api/health` → 200 ✅
  - Local `http://127.0.0.1:3080/` → 200 ✅

---

## iptv.daveai.tech
- **HTTP:** 200
- **Backend:** iptv-restream stack (nginx → frontend + backend :5000)
- **Status:** Working — needs proof
- **Checked:**
  - Root `/` → 200 ✅
  - `/api/channels` → 200 ✅ (via backend at 172.21.0.4:5000)
  - `/playlist` → 404 (not a route — playlists are managed via UI /api/channels)
- **Architecture note:** `/playlist` is not an HTTP endpoint. The iptv-restream app manages M3U playlists via `/api/channels` CRUD. There is no standalone `/playlist.m3u` HTTP download route.
- **Remaining:** Add a test channel via UI, verify stream playback

---

## iptv-restream.daveai.tech
- **HTTP:** 302
- **Status:** ✅ Working (redirects to iptv.daveai.tech)

---

## hermes3d.daveai.tech
- **HTTP:** 503
- **Status:** 🚧 Intentional placeholder — not built
- **Action:** Document and leave

---

## dev.daveai.tech
- **HTTP:** 503
- **Status:** 🚧 Intentional placeholder
- **Action:** Document and leave

---

## diy.daveai.tech
- **HTTP:** 503
- **Status:** 🚧 Intentional placeholder
- **Action:** Document and leave

---

## fleet.daveai.tech
- **HTTP:** 503
- **Status:** 🚧 Intentional placeholder
- **Action:** Document and leave

---

## staging.daveai.tech
- **HTTP:** 503
- **Status:** 🚧 Intentional placeholder
- **Action:** Document and leave

---

## game.daveai.tech
- **HTTP:** 302
- **Status:** Working — redirect target unverified
- **Remaining:** Check redirect destination
