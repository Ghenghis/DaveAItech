# DaveAI.tech — Subdomain Status Register

> Last updated: see git log  
> Each row reflects the **actual** verified state, not aspirational.  
> "Working" = backend up + HTTP 200/302 confirmed.  
> "Protected" = Authelia SSO guard in nginx config.  
> "Placeholder" = clean 503, no backend, SSO guard armed.  
> "Needs Restore" = backend code exists but not running; restore plan required.

---

## Subdomain Matrix

| Subdomain | Backend Port | SSO | Status | Notes |
|-----------|-------------|-----|--------|-------|
| `daveai.tech` | 3001 (Next.js) + 8888 (API) | Own auth | Working | Portal + V6 UI + chat + voice + action window |
| `www.daveai.tech` | — | — | Redirect → apex | 301 to daveai.tech |
| `auth.daveai.tech` | 9091 (Authelia) | Public | Working | SSO portal; must stay unprotected |
| `bolt.daveai.tech` | 5173 (Bolt.DIY) | Authelia | Working | Bolt.DIY IDE; SSO verified |
| `webui.daveai.tech` | 8083 (Open WebUI) | Authelia | Working | Canonical Open WebUI instance |
| `hermes.daveai.tech` | 8083 (Open WebUI) | Authelia | Working | Alias of webui; no separate container |
| `hermes-webui.daveai.tech` | 8787 (Hermes WebUI fork) | Authelia | Working | Separate hermes-themed fork |
| `voice.daveai.tech` | 5050 (TTS service) | None | Working | Programmatic API; no browser SSO |
| `hermestv.daveai.tech` | 3080 (HermesTV) | None | Working | Mixed web+API; /api unguarded |
| `tv.daveai.tech` | 3080 (HermesTV) | None | Working | Alias of hermestv |
| `iptv.daveai.tech` | 3103 (IPTV service) | None | Working | IPTV playlists + EPG; machine clients |
| `iptv-restream.daveai.tech` | 3011 (restream) | None | Working | Has own davetv_auth_gate |
| `openhands.daveai.tech` | 3333 (OpenHands) | Authelia | **Needs Restore** | Backend not running; see restore plan |
| `hermes3d.daveai.tech` | 7700 (MCP, TBD) | None | **Placeholder** | MCP server not deployed |
| `dev.daveai.tech` | — | Authelia | **Placeholder** | Clean 503; SSO guard armed |
| `diy.daveai.tech` | — | Authelia | **Placeholder** | Clean 503; SSO guard armed |
| `fleet.daveai.tech` | — | Authelia | **Placeholder** | Clean 503; SSO guard armed |
| `staging.daveai.tech` | — | Authelia | **Placeholder** | Clean 503; SSO guard armed |

---

## SSO Coverage Summary

- **Protected (Authelia forward-auth):** `bolt`, `webui`, `hermes`, `hermes-webui`, `openhands` (config ready), `dev`, `diy`, `fleet`, `staging`
- **Intentionally unprotected (API/media):** `voice`, `hermestv`, `tv`, `iptv`, `iptv-restream`, `hermes3d`
- **Own auth system:** `daveai.tech` apex
- **Always public:** `auth.daveai.tech`

---

## No Raw Errors Policy

Every subdomain must return one of:
- `200` — working backend
- `301/302` — HTTP→HTTPS or canonical redirect
- `503` — clean placeholder with explanatory HTML (no raw nginx 502/000)

Raw `502` errors indicate a broken proxy_pass with no `proxy_intercept_errors on` — fix immediately.

---

## Nginx Configs (deployment/nginx-configs/)

| File | Subdomain(s) |
|------|-------------|
| `daveai-portal/daveai.tech.nginx.conf` | apex + www |
| `authelia/auth.daveai.tech.nginx.conf` | auth |
| `bolt.daveai.tech.nginx.conf` | bolt |
| `nginx-configs/webui.daveai.tech.nginx.conf` | webui |
| `nginx-configs/hermes.daveai.tech.nginx.conf` | hermes |
| `nginx-configs/hermes-webui.daveai.tech.nginx.conf` | hermes-webui |
| `nginx-configs/voice.daveai.tech.nginx.conf` | voice |
| `nginx-configs/openhands.daveai.tech.nginx.conf` | openhands |
| `nginx-configs/hermestv.daveai.tech.nginx.conf` | hermestv + tv |
| `nginx-configs/iptv.daveai.tech.nginx.conf` | iptv |
| `nginx-configs/iptv-restream.daveai.tech.nginx.conf` | iptv-restream |
| `nginx-configs/hermes3d.daveai.tech.nginx.conf` | hermes3d |
| `nginx-configs/placeholders.nginx.conf` | dev, diy, fleet, staging |
