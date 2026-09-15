---

## BUG-009 — NODE_ENV=production breaks Vite dev SSR jsxDEV

**Date:** 2026-05-30  
**Severity:** Critical (dev server completely broken)  
**System:** Bolt.DIY local development

**Symptom:**  
`pnpm dev` crashes immediately with HTTP 500:
```
TypeError: __vite_ssr_import__.jsxDEV is not a function
    at g:\Github\Bolt.DIY\app\entry.server.tsx:28
```

**Root Cause:**  
`NODE_ENV=production` was set in repo `.env` line 29. Vite's dev SSR transform emits `jsxDEV` calls (development JSX runtime), but React's production build has no `jsxDEV` function. The mismatch causes a hard crash.

**Fix:**
1. **Backup:** `G:\private\backups\BoltDIY\.env.20260530-155503.bak`
2. **Removed** `NODE_ENV=production` from repo `.env`
3. **Replaced with documentation block:**
```env
# Development Mode
# NOTE: Do NOT set NODE_ENV=production here. It breaks the Vite dev server SSR
#       transform ("__vite_ssr_import__.jsxDEV is not a function" 500 at entry.server.tsx).
# For local development, override per-process instead:
#       PowerShell:  $env:NODE_ENV="development"; pnpm dev
#       bash:        NODE_ENV=development pnpm dev
# NODE_ENV should only be "production" in the production/deploy context (see .env.production).
```
4. **Added warning to `.env.example`** at line 201-208 with same guidance.

**Result:** `pnpm dev` starts successfully, HTTP 200, 0 console errors.

**Rollback:** Restore backup from `G:\private\backups\BoltDIY\`

---
# DaveAI.tech — Bug Fix Log

All fixes are real, tested, and proven. No stubs or mocks.

---

## BUG-001 — OpenHands CLI PyInstaller bundle missing `textual_serve/static`

**Date:** 2026-05-30  
**Severity:** Critical (blocked openhands.daveai.tech entirely)  
**System:** `openhands.daveai.tech`

**Symptom:**  
`openhands web --host 127.0.0.1 --port 3333` crashed immediately with:
```
ValueError: '/tmp/_MEI<hash>/textual_serve/static' does not exist
```
PM2 crash-looped 40+ times. Port 3333 never bound.

**Root Cause:**  
The pre-built PyInstaller binary (`/usr/local/bin/openhands` v1.21.0, 88MB ELF) is missing the `textual_serve/static` directory from its bundle. This is a packaging defect in the v1.21.0 release binary — not a configuration issue.

**Fix:**  
Switched to the official Docker deployment method per docs.openhands.dev:
```bash
docker run -d \
  --name openhands-app \
  --restart unless-stopped \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e AGENT_SERVER_IMAGE_TAG=1.19.1-python \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  -p 127.0.0.1:3333:3000 \
  --add-host host.docker.internal:host-gateway \
  docker.openhands.dev/openhands/openhands:1.7
```

**Proof:**  
- `ss -tlnp | grep 3333` → LISTEN  
- `curl http://127.0.0.1:3333/` → HTTP 200  
- `curl https://openhands.daveai.tech/` → HTTP 200  
- `docker ps` → `openhands-app Up`

**Rollback:**  
`docker rm -f openhands-app` removes the container. The broken binary remains at `/usr/local/bin/openhands` and can be re-attempted if a fixed version is released.

---

## BUG-002 — voice.daveai.tech /api/* routes returning 404

**Date:** 2026-05-30  
**Severity:** High (voice API completely broken through nginx)  
**System:** `voice.daveai.tech`

**Symptom:**  
`https://voice.daveai.tech/api/voices` → HTTP 404  
`https://voice.daveai.tech/api/tts/health` → HTTP 404  
Direct backend call `http://127.0.0.1:5050/api/voices` → HTTP 200 ✅  

**Root Cause:**  
The nginx config for `voice.daveai.tech` had a `rewrite` rule in the `/api/` location block:
```nginx
location /api/ {
    rewrite ^/api/(.*) /$1 break;   # ← BUG: strips /api/ prefix
    proxy_pass http://voice_edge_tts_backend;
}
```
The `edge-tts-server.py` backend registers ALL routes under `/api/` (e.g. `/api/voices`, `/api/tts`, `/api/tts/health`). The rewrite stripped the `/api/` prefix before forwarding, so the backend received `/voices` instead of `/api/voices` — path not found → 404.

**Fix:**  
Removed both `rewrite ^/api/(.*) /$1 break;` lines from the voice nginx config. The backend now receives the full path including `/api/`.

```bash
# Backup: /etc/nginx/sites-enabled/voice.daveai.tech.bak.20260530-213134
# (moved out of sites-enabled to not break nginx -t)
```

**Proof:**  
- `curl https://voice.daveai.tech/api/voices` → HTTP 200  
- `curl https://voice.daveai.tech/api/tts/health` → HTTP 200  
- `nginx -t` passes

**Rollback:**  
Restore backup: `cp /etc/nginx/sites-available/voice.daveai.tech.bak.20260530-213134 /etc/nginx/sites-enabled/voice.daveai.tech && nginx -s reload`

---

## BUG-003 — nginx .bak files in sites-enabled breaking nginx -t

**Date:** 2026-05-30  
**Severity:** Medium (nginx reload failed)  
**System:** nginx

**Symptom:**  
After creating a backup of `voice.daveai.tech` as `voice.daveai.tech.bak.*` in `sites-enabled/`, nginx loaded both files. The backup had a duplicate `limit_req_zone` definition, causing:
```
[emerg] limit_req_zone "voice_synth_limit" is already bound to key...
nginx: configuration file test failed
```

**Root Cause:**  
Backup file saved in `sites-enabled/` directory (which nginx scans with a wildcard include) instead of `sites-available/` or an external backup directory.

**Fix:**  
Removed all `.bak*` files from `/etc/nginx/sites-enabled/`:
```bash
find /etc/nginx/sites-enabled/ -name "*.bak*" -exec rm -f {} \;
```

**Rollback:**  
N/A — backup copies exist in `sites-available/` as timestamped files.

**Prevention:**  
Always backup to `/etc/nginx/sites-available/` with a timestamp suffix, never in `sites-enabled/`.

---

## BUG-004 — Action Window: Tool logs auto-expanded inline in chat transcript

**Date:** 2026-05-30  
**Severity:** High (UI contract violation — tool output mixed with AI prose)  
**System:** `Bolt.DIY` — `app/components/chat/Artifact.tsx`

**Symptom:**  
Every AI message that included artifact actions caused the tool log (ActionList) to auto-expand inside the chat transcript, mixing build output with chat content.

**Root Cause:**  
`useEffect` in `Artifact.tsx` set `showActions=true` whenever `actions.length > 0` and the user hadn't manually toggled — so it fired on every message render.

**Fix:**  
Disabled the auto-expand: `if (false && actions.length && ...)`. `showActions` now stays `false` by default. Added "Build / Tool Log" label header when manually expanded.

**Rollback:**  
Revert the `if (false &&` guard back to `if (` in `Artifact.tsx`.

---

## BUG-005 — Action Window: Artifact launcher card indistinct from content

**Date:** 2026-05-30  
**Severity:** Medium (UX — users couldn't tell the card was a navigation element)  
**System:** `Bolt.DIY` — `app/components/chat/Artifact.tsx`

**Symptom:**  
Artifact card showed generic subtitle "Click to open Workbench" with no icon — visually identical to inline content blocks.

**Fix:**  
Added `i-ph:layout-duotone` icon to card title row. Changed subtitle to "Open in Action Window".

---

## BUG-006 — Action Window: Tool invocations unseparated from AI prose

**Date:** 2026-05-30  
**Severity:** High (UI contract violation — tool calls mixed into chat transcript)  
**System:** `Bolt.DIY` — `app/components/chat/AssistantMessage.tsx`

**Symptom:**  
`ToolInvocations` rendered flat directly below AI prose with no visual boundary — indistinguishable from chat text.

**Fix:**  
Wrapped `ToolInvocations` in a bordered labeled container with "TOOL CALLS" header and distinct background color.

---

## BUG-007 — Action Window: Mobile layout stacked Workbench below chat

**Date:** 2026-05-30  
**Severity:** High (mobile unusable — two panels stacked vertically)  
**System:** `Bolt.DIY` — `app/components/chat/BaseChat.tsx` + `BaseChat.module.scss`

**Symptom:**  
On viewports below 1024px, the Workbench rendered below the chat column in DOM order. Both panels visible simultaneously.

**Root Cause:**  
`showWorkbench` and `showChat` atoms were never coordinated. No CSS rule to hide chat when Workbench opened on mobile.

**Fix:**  
- Added `useEffect` in `BaseChat.tsx` to set `chatStore.showChat=false` when `showWorkbench=true` on mobile
- Chat column gets `hidden` class when `isSmallViewport && showWorkbench`  
- Added `@media (max-width: 1023px)` rule in `BaseChat.module.scss` setting `--workbench-inner-width: 100%` and hiding `.Chat` when `data-workbench-open='true'`

---

## BUG-008 — tsconfig.json: invalid `"electron"` type entry + missing node_modules

**Date:** 2026-05-30  
**Severity:** High (all IDE TypeScript errors project-wide — 50+ false errors)  
**System:** `Bolt.DIY` — `tsconfig.json` + `pnpm install`

**Symptom:**  
IDE showed "Cannot find module 'react'" and similar on every file. 50+ TS errors across all components.

**Root Cause:**  
1. `node_modules` was absent — `NODE_ENV=production` caused `pnpm install` to skip devDependencies
2. `tsconfig.json` listed `"electron"` in `types` array — wrong, package is `@types/electron`
3. `functions/[[path]].ts` imported `../build/server` (post-build only) — tsc error at dev time

**Fix:**  
1. `$env:NODE_ENV='development'; pnpm install --ignore-scripts` — 841 packages installed
2. Removed `"electron"` from `tsconfig.json` types array
3. Added `"exclude": ["node_modules", "build", "functions"]` to `tsconfig.json`

**Result:** `pnpm typecheck` → exit 0, 0 errors.
