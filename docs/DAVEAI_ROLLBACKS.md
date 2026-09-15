# DaveAI.tech — Rollback Index

All changes made during the 2026-05-30 session are documented here with exact rollback steps.

---

## ROL-001 — OpenHands: Switched from CLI binary to Docker

**Change:** Stopped PM2 `openhands-web` venv process, started Docker container `openhands-app`  
**Files changed:**
- New: `/root/.openhands/settings.json` (created with LiteLLM base_url)
- New: `/etc/nginx/sites-available/openhands.daveai.tech` (new nginx config)
- New: `/etc/nginx/sites-enabled/openhands.daveai.tech` (symlink)
- New: Docker container `openhands-app`
- Created (unused): `/opt/openhands-venv/`, `/usr/local/bin/start-openhands-web.sh`

**Rollback:**
```bash
docker rm -f openhands-app
rm /etc/nginx/sites-enabled/openhands.daveai.tech
nginx -s reload
# The broken CLI binary at /usr/local/bin/openhands remains unchanged
```

---

## ROL-002 — Voice nginx: Removed bad rewrite rule

**Change:** Removed `rewrite ^/api/(.*) /$1 break;` from `/etc/nginx/sites-enabled/voice.daveai.tech`  
**Backup:** `/etc/nginx/sites-available/voice.daveai.tech.bak.20260530-213134`

**Rollback:**
```bash
# WARNING: This will re-break voice /api/* endpoints
cp /etc/nginx/sites-available/voice.daveai.tech.bak.20260530-213134 \
   /etc/nginx/sites-enabled/voice.daveai.tech
nginx -t && nginx -s reload
```

---

## ROL-003 — Removed .bak files from sites-enabled

**Change:** `find /etc/nginx/sites-enabled/ -name "*.bak*" -exec rm -f {} \;`  
**Impact:** .bak files no longer confuse nginx -t  
**Rollback:** N/A — backups remain in `sites-available/` with timestamps

---

## ROL-004 — Updated /root/.openhands/settings.json

**Change:** Updated `base_url` from `http://127.0.0.1:4000` to `http://host.docker.internal:4000` so the Docker container can reach LiteLLM on the host.

**Rollback:**
```bash
python3 -c "
import json
with open('/root/.openhands/settings.json') as f:
    s = json.load(f)
s['llm']['base_url'] = 'http://127.0.0.1:4000'
with open('/root/.openhands/settings.json', 'w') as f:
    json.dump(s, f, indent=2)
"
docker restart openhands-app
```
Note: `127.0.0.1` will not work from inside Docker — only use this if switching away from Docker back to a host process.
