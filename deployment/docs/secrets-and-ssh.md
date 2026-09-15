# Secrets & SSH — Setup and Hygiene

How VPS access and secrets are managed for DaveAI.tech. **No secret values appear
in this repo or this doc.**

---

## 1. Where secrets live

| Location                  | Contents                                                                                                                            | In git?           |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `G:\private\`             | All real secrets vault: `.env.ssh` (VPS_PASS), `.env.deploy`, `.env2`, `.davetv-*.env`, `.hermes.env`                               | NO — outside repo |
| `G:\private\env\`         | `.env.vps` (OpenHands/VPS config), `.env.secret` (MINIMAX_API_KEY, JWT_SECRET), `.env.ssh`, `setup-vps.sh`, Cloudflare origin notes | NO — outside repo |
| `C:\Users\Admin\.ssh\`    | SSH keypairs (`id_ed25519`, `id_rsa`), `config`, `known_hosts`                                                                      | NO — user profile |
| `g:\Github\Bolt.DIY\.env` | Local runtime env for Bolt.DIY (gitignored)                                                                                         | NO — gitignored   |

> Canonical backup of the repo runtime env: `G:\private\.env.boltdiy-runtime`.

**Templates that ARE safe to keep in the repo:** `.env.example`, `.env.vps.example`
(placeholders only, no real values).

---

## 2. VPS connection

- **Host:** `root@187.77.30.206` (alias `daveai` in `~/.ssh/config`)
- **Auth:** public key (`id_ed25519`, fallback `id_rsa`). `VPS_PASS` in
  `G:\private\env\.env.ssh` is a password fallback only.

### From Windows / PowerShell (works out of the box)

```powershell
ssh root@187.77.30.206 "echo OK"
scp local.file root@187.77.30.206:/remote/path
```

Uses keys in `C:\Users\Admin\.ssh\`.

### From WSL / bash (`bash deployment/*.sh`)

WSL has its **own** `~/.ssh` (`/home/<user>/.ssh`) and does **not** read the
Windows keys. Run the one-time sync so bash scripts authenticate:

```bash
bash deployment/setup-wsl-ssh.sh
```

This copies the proven Windows keys + `config` into WSL with correct perms
(`700` dir, `600` private keys/config, `644` public/known_hosts), strips CRLF
from `config`, and verifies the VPS login. Safe to re-run; it backs up any
existing WSL `id_*` first.

> **Why this was needed:** `bash` on this machine runs under **WSL Ubuntu**.
> `ssh`/`scp` invoked from bash use `/home/<user>/.ssh`, while the authorized
> keys lived only in `C:\Users\Admin\.ssh`. Mixing them caused
> `Permission denied (publickey,password)`.

---

## 3. Deploying nginx configs

Both paths work now. The repo's `deployment/deploy-nginx-configs.sh` runs under
WSL bash.

> **Caution:** most subdomain configs are already live on the VPS and
> `nginx -t` is green. Do **not** blanket-overwrite — in particular the apex
> `daveai.tech` config (large, working). Deploy only changed files. See
> `deployment/docs/subdomain-status.md`.

---

## 4. Hygiene rules

1. **Never** put real secrets in `g:\Github\Bolt.DIY`. Use `G:\private\`.
2. `.gitignore` blocks `*.pem`, `*.key`, `*.ppk`, `id_rsa*`, `id_ed25519*`,
   `.ssh/`, `secrets/`, `*.env`, and `.env.*` (except `*.example`).
3. **`.env.txt` is banned.** A `.env` dump saved as `.txt` must NEVER live in the
   repo. Patterns `.env.txt`, `*.env.txt`, `*.env.*.txt`, `env.txt`, `*-env.txt`
   are gitignored. If one appears, **move** it to `G:\private\` (reversible,
   timestamped) — do not leave it in the working tree.
4. To share a new config var, add it to `.env.example` with a **placeholder**.
5. Rotate a leaked key immediately: generate a new keypair, update the VPS
   `~/.ssh/authorized_keys`, remove the old public key.

---

## 5. What was cleaned (2026-05-30)

| Action                    | Detail                                                                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Removed stray secret file | `.env.txt` (4 real secrets, exact duplicate of vaulted `G:\private\.env.deploy`) → moved to `G:\private\.env.txt.removed-from-repo-<ts>` |
| Mirrored runtime env      | repo `.env` → `G:\private\.env.boltdiy-runtime`                                                                                          |
| Verified safe to keep     | `.env.production` (only `VITE_GITLAB_URL`, `VITE_GITLAB_TOKEN_TYPE` — no secrets), `.env.example`, `.env.vps.example`                    |
| Fixed WSL auth            | `deployment/setup-wsl-ssh.sh` synced Windows keys into WSL                                                                               |
| Hardened                  | `.gitignore` secrets/keys section                                                                                                        |
