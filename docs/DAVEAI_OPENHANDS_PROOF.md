# OpenHands Deployment Proof

**Date:** 2026-05-30  
**VPS:** 187.77.30.206

---

## What Was Deployed

- **Image:** `docker.openhands.dev/openhands/openhands:1.7`
- **Agent server:** `ghcr.io/openhands/agent-server:1.19.1-python`
- **Container name:** `openhands-app`
- **Port binding:** `127.0.0.1:3333→3000`
- **Restart policy:** `unless-stopped`
- **LLM:** `openai/deepseek-chat` via LiteLLM proxy at `http://host.docker.internal:4000`
- **Settings file:** `/root/.openhands/settings.json`

---

## Proof

### 1. Container Running
```
docker ps output:
0ceb3accbaee   docker.openhands.dev/openhands/openhands:1.7
  "/app/entrypoint.sh"   Up
  127.0.0.1:3333->3000/tcp   openhands-app
```

### 2. Port Listening
```
ss -tlnp | grep 3333:
LISTEN 0  4096  127.0.0.1:3333  0.0.0.0:*  users:(("docker-proxy",...))
```

### 3. Local HTTP 200
```
curl http://127.0.0.1:3333/ → HTTP 200
```

### 4. Via Nginx HTTP 200
```
curl --resolve openhands.daveai.tech:443:127.0.0.1 \
  https://openhands.daveai.tech/ -k → HTTP 200
```

### 5. Public URL HTTP 200
```
curl https://openhands.daveai.tech/ → HTTP 200
```

### 6. LiteLLM Reachable From Container
```
/root/.openhands/settings.json:
{
  "llm": {
    "provider": "openai",
    "model": "openai/deepseek-chat",
    "base_url": "http://host.docker.internal:4000",
    "api_key": "litellm-local"
  }
}
```
`curl http://127.0.0.1:4000/models` → HTTP 200 (confirmed before container started)

---

## Nginx Config

`/etc/nginx/sites-available/openhands.daveai.tech`:
- HTTPS on 443 with Cloudflare origin cert
- WebSocket headers: `Upgrade`, `Connection "upgrade"`
- `proxy_pass http://127.0.0.1:3333`
- 300s read/send timeouts

---

## Remaining

- Submit a test agent task in the UI and confirm agent executes (LLM call goes through LiteLLM → DeepSeek)
- Verify Docker runtime image (`ghcr.io/openhands/runtime`) gets pulled on first task run
