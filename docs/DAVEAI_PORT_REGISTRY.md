# DaveAI VPS Port Registry
**Server:** 187.77.30.206 (Hostinger)  
**Purpose:** Centralized port allocation to prevent conflicts

## 🔒 **Reserved Port Ranges**

| Range | Purpose | Allocation |
|-------|---------|------------|
| 3000-3099 | **Core Services** | Main apps, APIs |
| 3100-3199 | **Media/Streaming** | IPTV, voice, video |
| 3300-3399 | **Development** | Staging, dev tools |
| 4000-4099 | **AI/LLM Proxies** | LiteLLM, model serving |
| 5000-5099 | **Voice/TTS** | Edge-TTS, audio |
| 8000-8099 | **Management** | Dashboards, monitoring |
| 8700-8799 | **Hermes Bots** | Discord bot interfaces |
| 10000-10999 | **Dynamic/Auto** | Ephemeral containers |

## 📋 **Allocated Ports**

### Core Services (3000-3099)
| Port | Service | Subdomain | Managed By |
|------|---------|-----------|------------|
| 3001 | DaveAI Next.js | daveai.tech | PM2 (id=4) |
| 3080 | HermesTV Web | hermestv.daveai.tech | PM2 |
| 3011 | HermesTV API | hermestv.daveai.tech/api | PM2 |

### Media/Streaming (3100-3199)
| Port | Service | Subdomain | Managed By |
|------|---------|-----------|------------|
| 3103 | IPTV Restream | iptv.daveai.tech | Docker |
| 5050 | Edge-TTS | voice.daveai.tech | PM2 (id=3) |

### AI/LLM Proxies (4000-4099)
| Port | Service | Purpose | Managed By |
|------|---------|---------|------------|
| 4000 | LiteLLM | deepseek, minimax, openrouter | Docker |

### Hermes Bots (8700-8799)
| Port | Service | Subdomain | Managed By |
|------|---------|-----------|------------|
| 8787 | Hermes WebUI | hermes-webui.daveai.tech | PM2 |

### Container Services (3333-3333)
| Port | Service | Subdomain | Managed By |
|------|---------|-----------|------------|
| 3333→3000 | OpenHands | openhands.daveai.tech | Docker |

## 🚀 **Request New Port**

### For New Projects:
1. Check this registry first
2. Choose from appropriate range
3. Update this file with PR
4. Add to nginx config
5. Update DNS if subdomain needed

### Port Allocation Rules:
- **Core services:** 3000-3099 (persistent)
- **User projects:** 3300-3399 (temporary)
- **Containers:** Auto-allocate from 10000+
- **AI proxies:** 4000-4099 (centralized)

## 🔧 **Auto-Port Script**

Use `scripts/find-port.ps1` to find available ports:

```powershell
$port = & scripts/find-port.ps1
# Returns available port from preferred list or random high port
```

## 📝 **Last Updated**
2026-05-31 - Added Bolt.DIY port 5173 (dev only, local)
