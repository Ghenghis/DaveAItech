# DaveAI.tech SSO (Authelia) — Operations Guide

Centralised single sign-on for `*.daveai.tech`. One login at
`https://auth.daveai.tech` grants access to every protected subdomain via a
shared session cookie scoped to `daveai.tech`. "Remember me" keeps a device
trusted for 30 days.

> **Credentials live in `.env` (`VPS_PASS`) and are never printed.** The deploy
> script reads the password from a file on the VPS and hashes it with Argon2id;
> the plaintext never appears in logs or chat.

---

## 1. Architecture

```
Browser ──► Cloudflare ──► nginx (VPS) ──► service container
                              │
                              │ auth_request (subrequest)
                              ▼
                        Authelia :9091  ◄──►  Redis (sessions)
                              ▲
                              │ 302 redirect when unauthenticated
                        auth.daveai.tech (login portal, public)
```

- **Authelia** (`authelia/authelia:4.38`) on `127.0.0.1:9091`, fronted by
  `auth.daveai.tech`.
- **Redis** (`redis:7-alpine`) stores sessions so trusted-device sessions
  survive Authelia restarts.
- **nginx** sends an `auth_request` subrequest for every hit on a protected
  `location /`. If the session is missing/expired nginx returns `302` to the
  portal with `?rd=<original-url>`; after login the user is sent back.

All files live in `/opt/authelia` on the VPS:

| Path | Purpose |
|------|---------|
| `docker-compose.yml` | Authelia + Redis services |
| `config/configuration.yml` | Authelia config (no secrets inline) |
| `config/users_database.yml` | Users + Argon2id password hashes |
| `secrets/` | `JWT_SECRET`, `SESSION_SECRET`, `STORAGE_ENCRYPTION_KEY`, `REDIS_PASSWORD`, `ADMIN_PASSWORD` (all `chmod 600`) |
| `deploy.sh` | Idempotent deploy (secrets, hash, start, health-check) |
| `apply-sso.py` | Adds/inspects forward-auth on nginx site configs |
| `verify-login.sh` | End-to-end login flow test (server-side, no leak) |
| `nginx-backups/` | Timestamped backups of every edited nginx config |

nginx snippets (in `/etc/nginx/snippets/`):

| Snippet | Where it goes |
|---------|---------------|
| `authelia-location.conf` | once inside each protected `server { }` |
| `authelia-authrequest.conf` | inside each protected `location / { }` |

---

## 2. Protection status

**Protected (interactive SSO — redirect to login):**
`bolt`, `hermes`, `hermes-webui`, `webui`, `openhands`, `game`

**Armed placeholders** (`return 503`, no backend yet — SSO guard already in the
config and activates the moment a real `proxy_pass` backend is added):
`dev`, `diy`, `fleet`, `staging`

**Intentionally NOT behind interactive login** (programmatic clients — an HTML
login page would break them):

| Subdomain | Reason |
|-----------|--------|
| `hermes3d` | MCP server — agents authenticate with tokens, not a browser form |
| `iptv`, `iptv-restream` | IPTV streams for media players; `iptv-restream` already has its own `davetv_auth_gate` |
| `voice` | Text-to-speech API called programmatically |
| `hermestv` / `tv` | Mixed web + REST API (`/api`, `/api/tts/speak`, `/health`) |
| `daveai.tech` (apex) | Already has its **own** auth (`/auth/login`, `/auth/register`, `/admin/login`) |

**Always public:** `auth.daveai.tech` (the portal itself), `www` redirect.

> To protect a mixed API service, protect `location /` (web) and add a
> `bypass` rule / unguarded `location /api/` so machine clients keep working.
> See §6.

---

## 3. Deploy / redeploy

```bash
# On the VPS
/opt/authelia/deploy.sh          # idempotent: keeps existing secrets, re-hashes
                                 # the admin password, restarts, waits for HTTP 200
```

From the workstation (uploads fresh files, normalises line endings):

```powershell
scp deployment/authelia/docker-compose.yml deployment/authelia/deploy.sh \
    deployment/authelia/apply-sso.py root@187.77.30.206:/opt/authelia/
scp deployment/authelia/config/configuration.yml root@187.77.30.206:/opt/authelia/config/
ssh root@187.77.30.206 'sed -i "s/\r$//" /opt/authelia/*.sh /opt/authelia/*.py /opt/authelia/config/*.yml'
```

---

## 4. Manage users & passwords

```bash
# Change the admin password (re-reads the plaintext, re-hashes, restarts)
printf '%s' 'NEW_PASSWORD' > /opt/authelia/secrets/ADMIN_PASSWORD
chmod 600 /opt/authelia/secrets/ADMIN_PASSWORD
/opt/authelia/deploy.sh

# Hash a password manually
docker run --rm authelia/authelia:4.38 \
  authelia crypto hash generate argon2 --password 'SECRET'

# Add another user: append to config/users_database.yml then:
docker restart authelia
```

---

## 5. Protect a new subdomain

```bash
python3 /opt/authelia/apply-sso.py protect /etc/nginx/sites-enabled/NEW.daveai.tech
nginx -t && systemctl reload nginx
python3 /opt/authelia/apply-sso.py status /etc/nginx/sites-enabled/*.daveai.tech
```

The script is safe to re-run: it skips already-protected files, files with no
HTTPS block, and configs with no `location /`. Every change is backed up to
`/opt/authelia/nginx-backups/`.

---

## 6. Protect a service but keep its API open

Inside the HTTPS `server { }` add the location include once, then guard only the
web UI and leave the API location unguarded:

```nginx
include /etc/nginx/snippets/authelia-location.conf;

location /api/ {            # machine clients — no interactive auth
    proxy_pass http://127.0.0.1:PORT/api/;
}

location / {               # humans — require SSO
    include /etc/nginx/snippets/authelia-authrequest.conf;
    proxy_pass http://127.0.0.1:PORT/;
}
```

---

## 7. Verify

```bash
/opt/authelia/verify-login.sh     # full login flow, server-side, no secrets printed
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://bolt.daveai.tech/
#   expect: 302 https://auth.daveai.tech/?rd=https://bolt.daveai.tech/
```

---

## 8. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| Authelia container restart loop | Config error — `docker logs authelia 2>&1 \| grep level=error`. Common: a secret defined **both** in `configuration.yml` and via `AUTHELIA_*_FILE`. Keep secrets **only** in env-file form. |
| `502` on every subdomain | Authelia down — `cd /opt/authelia && docker compose ps`, then `./deploy.sh`. |
| Redirect loop to portal | Session cookie `domain` must be `daveai.tech` and `auth.daveai.tech` must stay **unprotected**. |
| Login OK but subdomain still 302 | Cookie not shared — confirm `session.cookies[].domain: daveai.tech` and that you logged in on an `*.daveai.tech` host. |
| `nginx: [emerg] duplicate location` | A `.bak` file landed in `sites-enabled/`. Backups must go to `/opt/authelia/nginx-backups/` (handled by `apply-sso.py`). |
| Bash/Python script "bad interpreter" | CRLF line endings — `sed -i 's/\r$//' file`. |

---

## 9. Rollback a single subdomain

```bash
ls /opt/authelia/nginx-backups/ | grep bolt
cp /opt/authelia/nginx-backups/etc_nginx_sites-enabled_bolt.daveai.tech.bak.sso-TIMESTAMP \
   /etc/nginx/sites-enabled/bolt.daveai.tech
nginx -t && systemctl reload nginx
```
