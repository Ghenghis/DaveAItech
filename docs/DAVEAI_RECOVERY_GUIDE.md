# DaveAI.tech — Recovery Guide

**VPS:** 187.77.30.206  
**SSH:** `ssh root@187.77.30.206`

---

## Quick Restart Commands

### Nginx
```bash
nginx -t && nginx -s reload      # test + reload (safe)
systemctl restart nginx          # full restart (use if reload fails)
```

### OpenHands
```bash
docker restart openhands-app
# Or full re-deploy:
docker rm -f openhands-app
bash /tmp/run-openhands-docker.sh   # re-upload from deployment/ first
```

### edge-tts (voice API)
```bash
pm2 restart edge-tts
pm2 logs edge-tts --lines 50
```

### agent-brain
```bash
pm2 restart agent-brain
pm2 logs agent-brain --lines 50
```

### LiteLLM proxy
```bash
pm2 restart litellm 2>/dev/null || docker restart litellm
curl http://127.0.0.1:4000/models   # verify
```

### IPTV stack
```bash
cd /root/iptv-restream   # or wherever docker-compose.yml is
docker compose restart
# Or individual:
docker restart iptv-restream-iptv_restream_backend-1
docker restart iptv-restream-iptv_restream_frontend-1
```

### HermesTv
```bash
docker restart hermestv-vps-api hermestv-vps-web
```

### All PM2 processes
```bash
pm2 restart all
pm2 save
```

---

## Nginx Config Locations

| Subdomain | Config file |
|-----------|-------------|
| daveai.tech | `/etc/nginx/sites-enabled/daveai.tech` |
| openhands.daveai.tech | `/etc/nginx/sites-available/openhands.daveai.tech` (symlinked) |
| voice.daveai.tech | `/etc/nginx/sites-enabled/voice.daveai.tech` |
| iptv.daveai.tech | `/etc/nginx/sites-enabled/iptv.daveai.tech` |
| auth.daveai.tech | `/etc/nginx/sites-enabled/auth.daveai.tech` (symlinked) |
| bolt.daveai.tech | `/etc/nginx/sites-enabled/bolt.daveai.tech` (symlinked) |

**Rule: NEVER save .bak files inside `sites-enabled/` — nginx loads everything in that dir.**  
Save backups to `sites-available/` with a timestamp.

---

## Rollback: voice nginx rewrite fix (BUG-002)

```bash
# If voice /api/* breaks again, restore original (with broken rewrite):
# Note: original had rewrite lines — this BREAKS the API. Use only if needed.
# The fixed version is the correct one. Do not revert unless there's a new reason.
```

---

## Rollback: OpenHands Docker (BUG-001)

```bash
docker rm -f openhands-app
# Broken CLI binary still at /usr/local/bin/openhands (do not use for 'web' cmd)
# To re-deploy Docker version:
docker run -d \
  --name openhands-app \
  --restart unless-stopped \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e AGENT_SERVER_IMAGE_TAG=1.19.1-python \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  -p 127.0.0.1:3333:3000 \
  --add-host host.docker.internal:host-gateway \
  docker.openhands.dev/openhands/openhands:1.7
```

---

## If LiteLLM Goes Down

All of these will fail: agent-brain, OpenHands, Hermes agents (if using LiteLLM models).

```bash
# Check:
ss -tlnp | grep 4000
curl http://127.0.0.1:4000/models

# Restart (check actual process manager):
pm2 list | grep litellm
docker ps | grep litellm
# restart whichever manages it
```

---

## Emergency Nginx Reset

```bash
# Full nginx stop/start:
systemctl stop nginx
systemctl start nginx
systemctl status nginx

# Check for config errors:
nginx -T 2>&1 | grep -E "emerg|error"
```
