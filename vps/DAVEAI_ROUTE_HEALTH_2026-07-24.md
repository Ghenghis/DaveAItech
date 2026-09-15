# DaveAI Route Health Proof

Date: 2026-07-24
Scope: Track C HTTPS routing and service ownership
Truth level: live external checks plus VPS listener/process inspection

## Accepted Repair

The VPS already had healthy localhost services for DaveAI Brain and LiteLLM,
but nginx had no matching HTTPS virtual hosts for their public subdomains.
Cloudflare therefore returned HTTP 526.

The following routes are now explicit and live:

| Public route | Origin | Proof |
| --- | --- | --- |
| `api.daveai.tech` | DaveAI Brain on `127.0.0.1:8888` | `/health` returns HTTP 200 |
| `ai.daveai.tech` | LiteLLM on `127.0.0.1:4000` | `/health/liveliness` returns HTTP 200 |
| `llm.daveai.tech` | LiteLLM on `127.0.0.1:4000` | `/health/liveliness` returns HTTP 200 |
| `docs.daveai.tech` | Canonical DaveAI docs | HTTP 302 to `https://daveai.tech/docs/ROADMAP.md`; target returns HTTP 200 |

The primary site regression check remains green:

```text
https://daveai.tech/api/health -> HTTP 200
status: ok
version: 4.0.0
tools: 116
agents: supervisor, coder, asset, qa
```

## Safe Fallback

An explicit wildcard HTTPS fallback now returns HTTP 503 with a small JSON
response for undefined `*.daveai.tech` hosts. This prevents an undefined
subdomain from falling through to the DaveAI Brain/API virtual host after TLS
negotiation.

Proof:

```text
https://not-a-real-service.daveai.tech/ -> HTTP 503
https://git.daveai.tech/               -> HTTP 503
https://db.daveai.tech/                -> HTTP 503
https://monitor.daveai.tech/           -> HTTP 503
https://ws.daveai.tech/                -> HTTP 503
```

## Current External Route Truth

| Route | HTTP | Current truth |
| --- | ---: | --- |
| `daveai.tech` | 200 | Live |
| `auth.daveai.tech` | 200 | Live |
| `api.daveai.tech/health` | 200 | Live |
| `voice.daveai.tech` | 200 | Live |
| `ai.daveai.tech/health/liveliness` | 200 | Live |
| `llm.daveai.tech/health/liveliness` | 200 | Live |
| `openhands.daveai.tech` | 200 | Live |
| `docs.daveai.tech` | 302 -> 200 | Live canonical redirect |
| `hermestv.daveai.tech` | 200 | Live |
| `iptv.daveai.tech` | 200 | Live |
| `hermes-webui.daveai.tech` | 302 | Live, auth-gated |
| `apps.daveai.tech` | 302 | Live, auth-gated |
| `game.daveai.tech` | 302 | Auth-gated placeholder |
| `diy.daveai.tech` | 503 | Not deployed |
| `dev.daveai.tech` | 503 | Not deployed |
| `staging.daveai.tech` | 503 | Not deployed |
| `git.daveai.tech` | 503 | Not deployed |
| `db.daveai.tech` | 503 | Not deployed |
| `monitor.daveai.tech` | 503 | Not deployed |
| `fleet.daveai.tech` | 503 | Not deployed |
| `ws.daveai.tech` | 503 | Not deployed |
| `hermes3d.daveai.tech` | 503 | Placeholder |

## Service Ownership Findings

- Port `3000` is an OpenHands agent container, not Grafana. It must not be
  routed as `monitor.daveai.tech`.
- Port `3100` is the DaveTV authentication gate, not the documentation site.
- No current listener owns the advertised Git/Gitea, database-admin, fleet, or
  WebSocket service ports.
- The live UI still labels several unavailable routes as `live`. Correcting
  those labels requires a separately reviewed V6 HTML change under the current
  coordination contract.

## Deployment and Rollback

Deployed nginx source:

```text
/etc/nginx/conf.d/daveai-core-services.conf
```

Validated with `nginx -t` before every reload.

Rollback snapshots:

```text
/opt/daveai/backups/20260724T094817Z-core-service-routes
/opt/daveai/backups/20260724T094853Z-docs-route
/opt/daveai/backups/20260724T094936Z-subdomain-fallback
```

## Next Recommended Slice

Correct the DaveAI Sites panel status labels so only proven routes are shown as
live. After cross-review, update the V6 HTML without changing layout or app
behavior, run the existing Core regression harness, and publish a rollback.

Then deploy absent services one at a time. Monitoring should be first only
after a real Grafana service has its own non-conflicting listener.

