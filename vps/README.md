# DaveAI VPS - Complete Deployment System

**Server:** 187.77.30.206 (Hostinger VPS)  
**Purpose:** Centralized management of the verified DaveAI production services

> Production status and deployment inputs are defined in
> `DAVEAI_SOURCE_OF_TRUTH.md`, `daveai-sites-config.json`, and
> `daveai-project-catalog.json`. Older status notes below describe the original
> infrastructure plan and must not be used to infer that a route is live.

## 📋 Production Verification

```powershell
python vps/verify-source-of-truth.py
node vps/verify-daveai-ui-contracts.cjs vps/daveai-ui-v6.html
node vps/verify-feature-completion-state-actions.cjs vps/daveai-ui-v6.html
```

The legacy `deploy-all-services.sh` file describes the original infrastructure
plan and must not be used for the current VPS. The production services have
focused activation scripts under `services/`.

## 🌐 Subdomain Inventory

### Core Services (3000-3099)
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| daveai.tech | 3001 + 8888 | Next.js + Agent Brain | ✅ Active |
| api.daveai.tech | 8888 | API Gateway | ✅ Active |
| auth.daveai.tech | 8888 | Authelia SSO | ✅ Active |
| monitor.daveai.tech | 3030 | Grafana | 🔐 Active |

### AI/LLM Services (4000-4099)
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| ai.daveai.tech | 4000 | LiteLLM Proxy | ✅ Active |
| diy.daveai.tech | 3300 | DIY Studio | 🔐 Active |
| dev.daveai.tech | 3398 | Developer Console | 🔐 Active |
| openhands.daveai.tech | 3333 | OpenHands | ✅ Active |

### Media/Voice (3100-3199, 5000-5099)
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| voice.daveai.tech | 5050 | Edge-TTS | ✅ Active |
| iptv.daveai.tech | 3103 | IPTV Restream | ✅ Active |
| hermestv.daveai.tech | 3080 + 3011 | HermesTV | ✅ Active |

### Database & Dev (8000-8099, 3300-3399)
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| db.daveai.tech | 8080 | Adminer | 🔐 Active |
| git.daveai.tech | 3301 | Gitea | 🔐 Active |
| docs.daveai.tech | 3100 | MkDocs | 🆕 Added |
| staging.daveai.tech | 3399 | Release Gate | 🔐 Active |

### Management (3400-3499)
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| fleet.daveai.tech | 3400 | Fleet Inventory | 🔐 Active |
| ws.daveai.tech | 3401 | WebSocket Lab | ✅ Active |
| apps.daveai.tech | 3200 | Apps Portal | 🆕 Added |

### Bots (8700-8799)
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| hermes-webui.daveai.tech | 8787 | Hermes Bots | ✅ Active |

### Additional Surfaces
| Subdomain | Port | Service | Status |
|-----------|------|---------|--------|
| hermes3d.daveai.tech | 3600 | Live agent graph | ✅ Active |
| game.daveai.tech | 3500 | Game portal | 🔐 Authentication boundary |

## 🛠️ Available Commands

### Port Management
```bash
# Check port status
./port-manager.sh check 8080

# Allocate port for service
./port-manager.sh allocate myapp 8080

# Auto-allocate dynamic port
./port-manager.sh allocate myapp

# Release port
./port-manager.sh release myapp

# List all allocations
./port-manager.sh list
```

### Health Checks
```bash
# Run health check
./health-check.sh

# View health log
tail -f /var/log/daveai/health-check.log
```

### Docker Services
```bash
# Start all Docker services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart grafana

# Update all images
docker-compose pull && docker-compose up -d
```

### PM2 Services (Node.js)
```bash
# View all processes
pm2 status

# Restart all
pm2 restart all

# View logs
pm2 logs

# Save PM2 config
pm2 save
```

## 🔧 Automatic Port Failover

If a preferred port is in use, the system automatically:
1. Tries alternative ports in preferred list
2. Falls back to dynamic ports (49152-65535)
3. Updates nginx configuration
4. Reloads nginx gracefully
5. Logs the port change

Example port priority:
- Bolt.DIY: 3300 → 3301 → 3302 → 3303 → 3304 → dynamic
- Docs: 3100 → 3101 → 3102 → dynamic
- Git: 3301 → 3302 → 3303 → dynamic

## 🚨 Monitoring & Alerts

### Health Check (runs every 5 minutes via cron)
```bash
# Add to crontab
crontab -e

# Add line:
*/5 * * * * /opt/daveai/health-check.sh >> /var/log/daveai/health-cron.log 2>&1
```

### Discord Alerts
Set `DISCORD_WEBHOOK_URL` in `.env` to receive alerts when services fail.

### Grafana Dashboards
Access at https://monitor.daveai.tech
- Authelia protects the public route.
- Anonymous Viewer mode is available only behind that authenticated boundary.
- The provisioned `DaveAI VPS Overview` dashboard displays live Prometheus host metrics.

## 📝 File Structure

```
/opt/daveai/
├── .env                          # Environment variables
├── port-registry.json             # Port allocations
├── docker-compose.yml           # Container services
├── deploy-all-services.sh       # Deployment script
├── health-check.sh              # Health checker
├── port-manager.sh              # Port management
├── nginx/
│   └── daveai-subdomains.conf   # Nginx configuration
├── grafana/
│   ├── dashboards/              # Dashboard configs
│   └── datasources/             # Data source configs
├── prometheus/
│   └── prometheus.yml           # Prometheus config
├── litellm-config.yaml          # LiteLLM configuration
└── apps-portal/                 # Static apps portal
```

## 🔐 SSL Certificates

Certificates are managed by Cloudflare Origin CA:
- Location: `/etc/nginx/ssl/daveai.tech/`
- Files: `cloudflare-origin.pem`, `cloudflare-origin.key`
- Auto-renewed by Cloudflare

## 🔄 Backup & Recovery

### Port Registry Backup
```bash
# Backup
 cp /opt/daveai/port-registry.json /opt/daveai/backups/port-registry-$(date +%Y%m%d).json

# Restore
 cp /opt/daveai/backups/port-registry-YYYYMMDD.json /opt/daveai/port-registry.json
```

### Database Backup
```bash
# Backup PostgreSQL
docker exec daveai-postgres pg_dump -U daveai daveai > backup-$(date +%Y%m%d).sql

# Restore
cat backup-YYYYMMDD.sql | docker exec -i daveai-postgres psql -U daveai daveai
```

## 📊 Current Status

```
Total Subdomains: 22
Live (HTTP 200): 12
Soon (controlled HTTP 503): 9
Authentication portal: 1

Services:
- DaveAI Brain: version 4.0.0
- Runtime tools: 120
- Runtime agents: 4
- Nginx site entries: 22
```

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 3300
ss -tuln | grep :3300
lsof -i :3300

# Kill process if needed
kill -9 <PID>
```

### Nginx Issues
```bash
# Test config
nginx -t

# Reload
systemctl reload nginx

# View error log
tail -f /var/log/nginx/error.log
```

### Service Won't Start
```bash
# Check logs
docker logs <container-name>
pm2 logs <process-name>

# Verify port allocation
cat /opt/daveai/port-registry.json | jq '.services.<service-name>'
```

## 🚀 Next Steps

1. **Deploy remaining services:**
   ```bash
   sudo ./deploy-all-services.sh
   ```

2. **Set up monitoring:**
   ```bash
   docker-compose up -d grafana prometheus
   ```

3. **Configure alerts:**
   - Add Discord webhook to `.env`
   - Set up cron for health checks

4. **Test failover:**
   ```bash
   # Simulate port conflict
   nc -l 3300 &
   ./deploy-all-services.sh  # Should auto-assign 3301
   ```

---

**Last Updated:** 2026-05-31  
**Maintained by:** DaveAI VPS Team
