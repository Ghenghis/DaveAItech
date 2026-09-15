# Cloudflare Setup for bolt.daveai.tech

This guide covers the Cloudflare configuration needed for Bolt.diy VPS deployment.

## Prerequisites

- Cloudflare account with daveai.tech domain
- Access to Cloudflare Dashboard
- VPS IP: 187.77.30.206

## Step 1: DNS Configuration

### Add A Record

1. Login to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select **daveai.tech** domain
3. Go to **DNS** > **Records**
4. Click **Add Record**:

| Setting | Value |
|---------|-------|
| Type | A |
| Name | bolt |
| IPv4 Address | 187.77.30.206 |
| Proxy Status | **Proxied** (orange cloud) |
| TTL | Auto |

5. Click **Save**

### Verify DNS

```bash
# Check DNS propagation
nslookup bolt.daveai.tech
dig bolt.daveai.tech

# Should return: 187.77.30.206 (or Cloudflare proxy IPs)
```

## Step 2: SSL/TLS Configuration

### SSL/TLS Mode

1. Go to **SSL/TLS** > **Overview**
2. Set encryption mode to **Full (strict)**

### Always Use HTTPS

1. Go to **SSL/TLS** > **Edge Certificates**
2. Enable **Always Use HTTPS**
3. Enable **Automatic HTTPS Rewrites**

### Minimum TLS Version

1. Set **Minimum TLS Version** to **1.2**

## Step 3: Origin Server Certificate

### Create Certificate

1. Go to **SSL/TLS** > **Origin Server**
2. Click **Create Certificate**
3. Select:
   - **Let Cloudflare generate a private key and a CSR**: RSA
   - **Hostnames**: 
     - `bolt.daveai.tech`
     - `*.bolt.daveai.tech` (optional)
   - **Certificate Validity**: 15 years
4. Click **Create**

### Download Certificate

1. **PEM format** - Download both files:
   - `cloudflare-origin.pem` (Origin Certificate)
   - `cloudflare-origin.key` (Private Key)

### Upload to VPS

```bash
# SSH to VPS
ssh root@187.77.30.206

# Create SSL directory
mkdir -p /etc/nginx/ssl/daveai.tech

# Upload files (from local machine)
scp cloudflare-origin.pem root@187.77.30.206:/etc/nginx/ssl/daveai.tech/
scp cloudflare-origin.key root@187.77.30.206:/etc/nginx/ssl/daveai.tech/

# Set permissions (on VPS)
chmod 600 /etc/nginx/ssl/daveai.tech/*.key
chmod 644 /etc/nginx/ssl/daveai.tech/*.pem
```

## Step 4: Security Settings

### Security Level

1. Go to **Security** > **Settings**
2. Set **Security Level** to **Medium**

### Bots

1. Enable **Bot Fight Mode**

### Rate Limiting (Optional)

1. Go to **Security** > **WAF** > **Rate limiting rules**
2. Create rule:
   - **Name**: Bolt.diy Rate Limit
   - **When incoming requests match**: All incoming requests
   - **Rate exceeding**: 100 requests per 1 minute
   - **Then**: Block action for 1 hour

## Step 5: Caching (Optional)

### Caching Level

1. Go to **Caching** > **Configuration**
2. Set **Caching Level** to **Standard**

### Page Rules (Optional)

If you want to bypass cache for dynamic content:

1. Go to **Rules** > **Page Rules**
2. Create rule:
   - **URL**: `bolt.daveai.tech/*`
   - **Settings**: 
     - Cache Level: Bypass
     - SSL: Full

## Step 6: Verify Setup

### Test HTTPS

```bash
# Test SSL certificate
curl -v https://bolt.daveai.tech

# Should show SSL handshake and 200 OK
```

### Test Cloudflare Proxy

1. Visit https://bolt.daveai.tech
2. Check response headers (should include `cf-ray` header)
3. Verify certificate is issued by Cloudflare

## Troubleshooting

### SSL Handshake Failed

**Symptom**: `curl: (35) error:0A00010B:SSL routines::wrong version number`

**Solution**:
1. Verify origin certificates are uploaded correctly
2. Check Nginx SSL configuration
3. Ensure Cloudflare SSL mode is "Full (strict)"

### DNS Not Resolving

**Symptom**: `nslookup bolt.daveai.tech` fails

**Solution**:
1. Wait 5-10 minutes for DNS propagation
2. Check DNS record is saved in Cloudflare
3. Verify proxy status is "Proxied"

### 521/522 Errors

**Symptom**: Cloudflare shows 521 (Web Server is Down) or 522 (Connection Timed Out)

**Solution**:
1. Verify Nginx is running: `systemctl status nginx`
2. Check Docker container is running: `docker ps`
3. Verify firewall allows port 443: `ufw status`
4. Check Cloudflare IP ranges are allowed

### Certificate Mismatch

**Symptom**: Browser shows certificate warning

**Solution**:
1. Verify certificate files on VPS:
   ```bash
   openssl x509 -in /etc/nginx/ssl/daveai.tech/cloudflare-origin.pem -text -noout
   ```
2. Check certificate matches domain `bolt.daveai.tech`
3. Verify certificate is not expired

## Quick Reference

| Setting | Value |
|---------|-------|
| DNS Record Type | A |
| DNS Name | bolt |
| DNS Target | 187.77.30.206 |
| Proxy | Enabled (orange cloud) |
| SSL Mode | Full (strict) |
| Always HTTPS | ON |
| Certificate | Origin Server (15 years) |

## Support

- Cloudflare Docs: https://developers.cloudflare.com/
- SSL Troubleshooting: https://developers.cloudflare.com/ssl/troubleshooting/
