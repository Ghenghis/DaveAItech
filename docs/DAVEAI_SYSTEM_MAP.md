# DaveAI.tech — System Map

**Last updated:** 2026-05-30  
**Source:** Live VPS inspection (ss, docker ps, pm2 list, nginx grep)

---

## VPS

- **Host:** 187.77.30.206 (srv1376124)
- **OS:** Ubuntu (kernel 5.x)
- **Nginx:** 1.24.0
- **Docker:** 29.4.3
- **Python:** 3.12.3
- **Node:** (hermestv, serve-api, agentic-ui)

---

## Port Map (Live)

| Port | Protocol | Process | Subdomain |
|------|----------|---------|-----------|
| 80 | TCP | nginx | redirect → 443 |
| 443 | TCP | nginx | all subdomains |
| 3001 | TCP | next-server (Next.js) | daveai.tech |
| 3011 | TCP | hermestv-vps-api (Docker) | hermestv.daveai.tech /api/ |
| 3080 | TCP | hermestv-vps-web (Docker) | hermestv.daveai.tech |
| 3103 | TCP | iptv-restream nginx (Docker) | iptv.daveai.tech |
| 3333 | TCP | openhands-app (Docker) | openhands.daveai.tech |
| 4000 | TCP | litellm (Python) | internal LLM proxy |
| 5050 | TCP | edge-tts-server (Python/PM2) | voice.daveai.tech |
| 7860 | TCP | open-webui (Docker) | hermes.daveai.tech |
| 8083 | TCP | open-webui #2 (Docker) | webui.daveai.tech |
| 8787 | TCP | hermes-webui (Docker) | hermes-webui.daveai.tech |
| 8888 | TCP | authelia (Docker) | auth.daveai.tech |
| 9091 | TCP | ? | (found in nginx config) |
| 11434 | TCP | ollama | internal |

---

## Docker Containers (Running)

| Container | Image | Ports | Subdomain |
|-----------|-------|-------|-----------|
| openhands-app | docker.openhands.dev/openhands/openhands:1.7 | 127.0.0.1:3333→3000 | openhands.daveai.tech |
| hermestv-vps-api | (custom) | 127.0.0.1:3011→? | hermestv.daveai.tech/api |
| hermestv-vps-web | (custom) | 127.0.0.1:3080→? | hermestv.daveai.tech |
| open-webui (hermes) | open-webui | localhost:7860→8080 | hermes.daveai.tech |
| open-webui (webui) | open-webui | 127.0.0.1:8083→8080 | webui.daveai.tech |
| iptv-restream-iptv_restream_nginx-1 | nginx:alpine | 127.0.0.1:3103→80 | iptv.daveai.tech |
| iptv-restream-iptv_restream_backend-1 | (custom Node.js) | 5000 (internal) | iptv.daveai.tech/api |
| iptv-restream-iptv_restream_frontend-1 | (custom) | 80 (internal) | iptv.daveai.tech UI |
| litellm | litellm | 127.0.0.1:4000 | internal |
| shiba-postgres | postgres | 127.0.0.1:5499 | internal |
| hermes1-5 | (custom) | — | Discord bots |
| hermes-webui | (custom) | localhost:8787 | hermes-webui.daveai.tech |
| pipelines | (custom) | 9099 | Open WebUI pipelines |

---

## PM2 Processes

| ID | Name | Script | Status |
|----|------|--------|--------|
| 0 | serve-api | Node.js | online |
| 3 | edge-tts | `/opt/agent-brain/venv/bin/python /opt/agent-brain/edge-tts-server.py` | online |
| 4 | agentic-ui | Node.js 1.0.0 | online |
| 5 | hermes-watchdog | bash | online |
| 8 | agent-brain | Python (brain_alice.py) | online |

---

## LLM Stack

```
OpenHands / agent-brain / hermes
         ↓
LiteLLM proxy (127.0.0.1:4000)
         ↓
┌─────────────────────────────────────────┐
│ minimax-highspeed → api.minimax.io/v1   │
│ minimax-quality   → api.minimax.io/v1   │
│ deepseek-chat     → api.deepseek.com    │
│ deepseek-reasoner → api.deepseek.com    │
│ openrouter-claude → openrouter/claude   │
│ deepseek-v3       → api.siliconflow.com │
│ (local) ollama    → 127.0.0.1:11434     │
│ (local) LM Studio → 100.117.190.97:1234 (Tailscale) │
└─────────────────────────────────────────┘
```

---

## Key File Locations (VPS)

| Path | Contents |
|------|----------|
| `/opt/agent-brain/` | brain_alice.py, edge-tts-server.py, venv, .env |
| `/opt/litellm/config.yaml` | LiteLLM proxy model config |
| `/root/.openhands/settings.json` | OpenHands LLM config |
| `/etc/nginx/sites-enabled/` | All active nginx vhosts |
| `/etc/nginx/ssl/daveai.tech/` | Cloudflare origin cert + key |
| `/var/www/agentic-website/` | Static files (voice landing page) |
| `/root/hermes-scripts/` | Hermes docker-compose + deploy scripts |
| `/root/.pm2/logs/` | PM2 process logs |

---

## SSL / TLS

- **All proxied subdomains**: Cloudflare Full SSL — origin cert at `/etc/nginx/ssl/daveai.tech/cloudflare-origin.pem`
- **webui.daveai.tech**: Let's Encrypt cert (auto-renewing)
- **Cloudflare**: Proxies all `*.daveai.tech` A records
