# OpenHands — Restore Plan

> **Status: Backend Missing — Needs Dedicated Restore**  
> The nginx config at `deployment/nginx-configs/openhands.daveai.tech.nginx.conf`
> is written and correct. The Authelia SSO guard is armed. The only missing piece
> is the OpenHands backend running on **port 3333**.

---

## Why It's Broken

- PM2 process `openhands-multiagent` was previously crash-looping on port `3001`.
- Port `3001` is **already owned by the daveai.tech apex Next.js app** — this was
  the root conflict.
- The nginx proxy_pass for openhands.daveai.tech was pointing at 3001 (wrong port),
  causing raw 502 errors.
- The backend process itself is not running cleanly.

---

## Required Correct Port

OpenHands **must** bind to `127.0.0.1:3333`. The nginx config already reflects this.
Do not use 3001 (apex), 5173 (bolt), 8083 (webui), or 8888 (api brain).

---

## Restore Steps

### Step 1 — Stop the broken PM2 process

```bash
pm2 stop openhands-multiagent 2>/dev/null || true
pm2 delete openhands-multiagent 2>/dev/null || true
pm2 save
```

### Step 2 — Verify OpenHands is installed

```bash
# Option A: Docker image (recommended)
docker pull ghcr.io/all-hands-ai/openhands:main

# Option B: Python package
pip show openhands-ai 2>/dev/null || pip install openhands-ai
```

### Step 3 — Start OpenHands on port 3333

**Docker (recommended):**

```bash
docker run -d \
  --name openhands \
  --restart unless-stopped \
  -p 127.0.0.1:3333:3000 \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=ghcr.io/all-hands-ai/runtime:main \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/openhands/workspace:/opt/workspace_base \
  ghcr.io/all-hands-ai/openhands:main
```

> The container's internal port is 3000; nginx sees it at 127.0.0.1:3333 via `-p 127.0.0.1:3333:3000`.

**PM2 (if Python install preferred):**

```bash
pm2 start "python -m openhands.server --port 3333 --host 127.0.0.1" \
  --name openhands \
  --interpreter none
pm2 save
```

### Step 4 — Verify backend is up

```bash
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3333/
# Expected: 200 or 302
```

### Step 5 — Deploy nginx config

```bash
cp /path/to/deployment/nginx-configs/openhands.daveai.tech.nginx.conf \
   /etc/nginx/sites-available/openhands.daveai.tech
ln -sf /etc/nginx/sites-available/openhands.daveai.tech \
        /etc/nginx/sites-enabled/openhands.daveai.tech
nginx -t && systemctl reload nginx
```

### Step 6 — Verify SSO flow

```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://openhands.daveai.tech/
# Expected: 302 https://auth.daveai.tech/?rd=https://openhands.daveai.tech/
```

---

## Rollback

If the restore breaks something:

```bash
# Stop backend
docker stop openhands && docker rm openhands
# or: pm2 stop openhands && pm2 delete openhands

# Remove nginx symlink
rm /etc/nginx/sites-enabled/openhands.daveai.tech
nginx -t && systemctl reload nginx
```

---

## Environment Variables Needed

OpenHands requires at minimum an LLM API key. Set in `/opt/openhands/.env`:

```
LLM_API_KEY=<your-key>
LLM_MODEL=<model-name>
```

Pass to Docker: `--env-file /opt/openhands/.env`

Do **not** commit secrets to git.

---

## Acceptance

- `curl http://127.0.0.1:3333/` returns 200
- `curl https://openhands.daveai.tech/` returns 302 → auth portal
- After login, OpenHands UI loads in browser
- Port 3001 is unaffected (apex still works)
