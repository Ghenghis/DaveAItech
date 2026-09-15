# DaveAI.tech — Final Proof Index

> Every fix made during the sprint is recorded here.  
> Format: date | subdomain | what was fixed | proof method | result.

---

## Format

```
### <YYYY-MM-DD> — <subdomain/system> — <fix description>
- **Root cause:** what was actually broken
- **Fix:** exact change made (file + line or command)
- **Proof:** curl output / screenshot path / nginx -t output
- **Rollback:** how to undo
```

---

## Sprint Fixes

### Authelia — File-based secrets, no restart loop

- **Root cause:** Secrets defined both inline in `configuration.yml` AND as `AUTHELIA_*_FILE` env vars → Authelia refused to start ("defined in multiple sources").
- **Fix:** Removed all secret values from `configuration.yml`; kept only `AUTHELIA_*_FILE` env vars in `docker-compose.yml`.
- **Files:** `deployment/authelia/config/configuration.yml`, `deployment/authelia/docker-compose.yml`
- **Proof:** `docker logs authelia | grep level=error` → 0 errors after fix
- **Rollback:** Restore `configuration.yml` from `/opt/authelia/nginx-backups/`

---

### Authelia — Redis password via file

- **Root cause:** Redis was started with a hardcoded empty password; Authelia couldn't auth to it.
- **Fix:** Redis command uses `cat /secrets/REDIS_PASSWORD`; Authelia env var `AUTHELIA_SESSION_REDIS_PASSWORD_FILE` points to same file.
- **Files:** `deployment/authelia/docker-compose.yml`
- **Proof:** `docker exec authelia-redis redis-cli -a "$(cat /opt/authelia/secrets/REDIS_PASSWORD)" ping` → `PONG`
- **Rollback:** Remove `--requirepass` from Redis command

---

### hermes.daveai.tech — Backend repointed to :8083

- **Root cause:** nginx was proxying hermes to port 7860 where no container existed → raw 502.
- **Fix:** `proxy_pass` changed to `http://127.0.0.1:8083` (Open WebUI).
- **Files:** `/etc/nginx/sites-enabled/hermes.daveai.tech` (on VPS)
- **Proof:** `curl -s -o /dev/null -w '%{http_code}' https://hermes.daveai.tech/` → `302`
- **Rollback:** Restore from `/opt/authelia/nginx-backups/`

---

### openhands.daveai.tech — Raw 502 → clean 503

- **Root cause:** `proxy_intercept_errors` was missing; nginx returned raw 502 with no HTML.
- **Fix:** Added `proxy_intercept_errors on` + `error_page 502 503 504 = @backend_down`.
- **Files:** `/etc/nginx/sites-enabled/openhands.daveai.tech` (on VPS)
- **Proof:** `curl -s https://openhands.daveai.tech/` → returns HTML "not deployed yet" with HTTP 503
- **Rollback:** Remove the two directives

---

### webui.daveai.tech — Mangled nginx config rewritten

- **Root cause:** Config had duplicate `server {}` blocks and a missing SSL block → nginx syntax error.
- **Fix:** Rewrote clean config with correct SSL, forward-auth, and single `location /` block.
- **Files:** `/etc/nginx/sites-enabled/webui.daveai.tech` (on VPS)
- **Proof:** `nginx -t` → `syntax is ok`
- **Rollback:** Restore from `/opt/authelia/nginx-backups/`

---

### apply-sso.py — Backups outside sites-enabled

- **Root cause:** Script was placing `.bak` files inside `sites-enabled/` → nginx loaded them as server blocks → duplicate `location /` errors.
- **Fix:** Set `BACKUP_DIR = "/opt/authelia/nginx-backups"` (outside nginx include path).
- **Files:** `deployment/authelia/apply-sso.py`
- **Proof:** `nginx -t` passes after running apply-sso.py protect; no `.bak` files in sites-enabled.
- **Rollback:** N/A (backups are non-destructive)

---

### deploy.sh / apply-sso.py — CRLF line endings

- **Root cause:** Files transferred from Windows had `\r\n` line endings → bash "bad interpreter" error, Python syntax error.
- **Fix:** `sed -i 's/\r$//' /opt/authelia/*.sh /opt/authelia/*.py` after every SCP upload.
- **Proof:** `file deploy.sh` → `Bourne-Again shell script, ASCII text` (not "with CRLF")
- **Rollback:** N/A

---

### bolt.daveai.tech — SSO verified

- **Root cause:** nginx config was missing Authelia forward-auth includes.
- **Fix:** Applied `authelia-location.conf` and `authelia-authrequest.conf` snippets.
- **Files:** `/etc/nginx/sites-enabled/bolt.daveai.tech` (on VPS)
- **Proof:** `curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://bolt.daveai.tech/` → `302 https://auth.daveai.tech/?rd=https://bolt.daveai.tech/`
- **Rollback:** `cp /opt/authelia/nginx-backups/..bolt..bak /etc/nginx/sites-enabled/bolt.daveai.tech && nginx -t && systemctl reload nginx`

---

### Placeholder subdomains — clean 503

- **Root cause:** dev/diy/fleet/staging/hermes3d either had raw 502 (broken proxy) or no config at all.
- **Fix:** Created clean 503 placeholder configs with SSO guard armed.
- **Files:** `deployment/nginx-configs/placeholders.nginx.conf`, `hermes3d.daveai.tech.nginx.conf`
- **Proof:** `curl -s -o /dev/null -w '%{http_code}' https://dev.daveai.tech/` → `503` (not 502/000)
- **Rollback:** Remove the nginx symlinks

---

## Verification Commands (run on VPS)

```bash
# All subdomains — quick HTTP status check
for sub in daveai.tech auth bolt webui hermes hermes-webui voice openhands hermestv iptv iptv-restream hermes3d dev diy fleet staging; do
  host="${sub}.daveai.tech"
  [[ "$sub" == "daveai.tech" ]] && host="daveai.tech"
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "https://$host/" 2>/dev/null || echo "ERR")
  printf "%-35s %s\n" "$host" "$code"
done

# Authelia health
curl -s http://127.0.0.1:9091/api/health

# nginx syntax
nginx -t

# Containers
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# PM2
pm2 list
```

---

## Pending Verifications (PENDING = not yet run on VPS)

| Item | Command | Expected |
|------|---------|---------|
| voice /voices | `curl https://voice.daveai.tech/voices` | JSON array |
| voice /api/tts | POST with text | mp3 audio response |
| hermestv UI | `curl -o /dev/null -w '%{http_code}' https://hermestv.daveai.tech/` | 200 |
| iptv /playlist | `curl -o /dev/null -w '%{http_code}' https://iptv.daveai.tech/playlist` | 200 |
| openhands backend | `curl http://127.0.0.1:3333/` | 200 (after restore) |
| apex console errors | Browser DevTools | 0 errors |
