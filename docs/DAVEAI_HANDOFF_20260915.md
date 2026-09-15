# DaveAI.tech Master Handoff — 2026-09-15

This is the entry-point handoff for DaveAI.tech, written for **cold pickup**: another AI coding
agent (Devin, Kilocode, Codex, a future Claude session, or anything else) or a human, with **zero
conversation history** and no prior context. Assume the reader can read files and run commands and
knows nothing else about this project.

This exact document is saved in two places, kept in sync:

- `G:\Github\Bolt.DIY\docs\DAVEAI_HANDOFF_20260915.md` (inside the source repo)
- `G:\VPS\HANDOFF.md` (inside the separate, non-git-tracked workspace — see "Map" below for why
  that workspace exists and why it matters that it isn't git-tracked)

If you're reading one copy, the other exists too — check it hasn't drifted before trusting either
one as current.

This document does **not** repeat architectural detail — production topology, the multiple-codebase
reality, the v7 reconciliation, diagrams. All of that lives in
`G:\Github\Bolt.DIY\docs\DAVEAI_ARCHITECTURE_MAP_20260915.md`, written the same day as this
document. **Read it.** This document covers only what that one doesn't: standing rules, current
state, where to look, and how to verify any of it yourself.

One more thing before you read further: while this document was being written, **two other files it
now cites — `docs/DAVEAI_CONTRACT_KIT_20260915.md` and `docs/contracts/CT-INDEX.json` — were created
on disk by a concurrent process**, mid-session, by something other than whatever produced this file.
That is not a hypothetical risk this document warns about in the abstract — it happened during its
own writing. Treat every fact below as dated, not permanent, and re-verify before relying on it.

---

## Project identity

**DaveAI.tech** is a live product at `daveai.tech` (plus subdomains: `brain.`, `voice.`, `api.`,
`iptv.`, and others) built and operated by its owner, who goes by **Dave** or **ShadowByte**. It
runs on a Hostinger VPS at **187.77.30.206** (hostname `srv1376124.hstgr.cloud`), Ubuntu 24.04 with
Docker, 4 vCPU / 16 GB RAM.

The owner runs **multiple AI coding tools on this same project in parallel** — Claude, Codex,
Kilocode, Windsurf, Devin, and OpenHands have all touched it at various points, per the owner. This
document exists because context does not survive a tool switch otherwise. This session independently
corroborated several of these directly, from files, not just from being told:

- `G:\VPS\CLAUDE.md` (2026-05-24) is a standing coordination contract dividing labor between
  **Claude** and **Codex**, with **Windsurf** named as active on a separate lane of the same box.
- `C:\Users\Admin\Downloads\daveai-vps-handoff.md` is addressed directly to Claude Code, written to
  resume work a **claude.ai chat session** started.
- `G:\Github\Bolt.DIY\docs\DAVEAI_RC1_TO_RC2_HANDOFF_20260801.md` hands work off from a Claude
  session to **Codex** on a different, more stable PC.
- The VPS itself has a long-stopped container explicitly named for **OpenHands** CI (see the
  architecture map §2.4).
- This exact session watched a **concurrent, unidentified process** write two new files into this
  same repo's `docs/` folder in real time (see the callout above and the Contract kit item below) —
  live proof that "another tool is touching this right now, without telling you" is not a
  once-in-a-while risk on this project, it is closer to the default condition.

Whichever tool or agent you are, assume a *different* tool made real, uncommitted changes very
recently, possibly while you were reading this sentence. Read the Incident log and the architecture
map before changing anything live.

---

## Non-negotiable standing rules

These come directly from the owner, repeated across sessions from at least 2026-05-24 through
2026-09-15. Reproduced verbatim below; each is followed by where it's independently attested so you
don't have to take this document's word for it.

1. **No stubs, placeholders, or TODOs in runtime code — fully wired, production-ready output is
   expected.**
   Source: `C:\Users\Admin\Downloads\daveai-vps-handoff.md` ("Working conventions for this
   project"). Consistent with the mechanical `forbidden_claim_patterns` discipline in
   `G:\Github\Bolt.DIY\docs\contracts\CT-000-stop-the-bleeding.json`.

2. **Docs (architecture, schema, roadmap) are first-class deliverables, not optional extras.**
   Same source, verbatim. Consistent with the 20+ dated `DAVEAI_*.md` documents already in
   `G:\Github\Bolt.DIY\docs\`, and with this document itself being commissioned as a deliverable in
   its own right.

3. **Never claim "100% complete", "everything works", "production-ready", "no bugs remain", or
   "perfect" without a specific proof command/output next to the claim.**
   Enforced as a literal regex list (`forbidden_claim_patterns`) in every file under
   `G:\Github\Bolt.DIY\docs\contracts\`, and restated as a first-principles rule in
   `G:\Github\Bolt.DIY\docs\DAVEAI_CONTRACT_KIT_20260915.md` §3.4: *"This is not about banning
   confidence — it's about banning unearned confidence on a codebase this size."* Also stated as a
   top-level rule in both `DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` and
   `DAVEAI_ARCHITECTURE_MAP_20260915.md`. This document follows the same rule — see the citations
   throughout.

4. **Do not replace the live `daveai-ui-v6.html`, change Cloudflare/DNS/SSL, change auth gates,
   rotate secrets, or make firewall/security changes without stopping for explicit approval first.**
   These have all caused real production outages before.
   `G:\VPS\CLAUDE.md`, "Stop Conditions," lists this exact set verbatim (plus deleting docs/source
   trees and changing model/provider routing). Today's firewall incident (see Incident log below) is
   the concrete proof this rule exists for a reason, not as a formality.

5. **Preserve the current approved visual direction (dark command-center shell, purple DaveAI
   identity, top status chrome, left tool rail, right activity panel) unless the owner explicitly
   requests a redesign.**
   `G:\VPS\CLAUDE.md`, "Approved UI Direction," 2026-05-24: *"Dave approved the current
   Claude-produced DaveAI visual direction... Do not redesign the shell unless Dave requests a
   specific change."*

6. **Chat completion is the standing #1 priority, ahead of menus, games, and everything else.**
   `G:\VPS\CLAUDE.md` (2026-05-24), "Current Override: Chat E2E First": *"Dave explicitly redirected
   the work to finish the chat first, end to end."* Repeated four months later in
   `DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` §3 (2026-09-15): *"You were explicit: chat completion is
   the top priority, then menus/tabs, then games..."* A dedicated contract already exists for it:
   `G:\Github\Bolt.DIY\docs\contracts\CT-001-chat-completion.json`.

---

## Current state as of 2026-09-15

**This section will go stale — every line is dated; check whether it's still true before acting on
it.** Facts marked *(verified live)* were independently reproduced while writing this document;
facts marked *(reported)* were copied from another doc's own claim and not personally re-checked
here.

- **Production is up.** *(Verified live)*: `daveai.tech/api/health` → 200, `brain.daveai.tech/health`
  → 200, `api.daveai.tech/health` → 200, `ssh daveai uptime` → `44 days` (the box itself never
  rebooted — consistent with today's firewall incident being a network-layer block, not a crash; see
  Incident log).
- **`voice.daveai.tech` and `iptv.daveai.tech` are both down**, separately from today's incident, for
  roughly 6 weeks. *(Verified live)*: nothing listens on `:5050` or `:3103` at all (`ss -ltnp` on the
  VPS shows only `:8888` for these three ports); the `iptv-restream-*` (3 containers) and
  `hermestv-vps-api`/`-web` Docker containers all show `Exited ... 6 weeks ago`. **Caution:**
  `curl https://voice.daveai.tech/` returns HTTP 200 — but that's a static landing page
  (`last-modified: 2026-04-26`) served without touching the dead backend, not proof voice works.
  `https://iptv.daveai.tech/` correctly returns 502 (no static fallback). Don't let a root-path 200
  fool you on subdomains — check the actual port/process, not just the homepage. No decision has been
  made on reviving or retiring either service — that is the owner's call.
- **The real, live source of daveai.tech** is one hand-written file,
  `G:\Github\Bolt.DIY\vps\daveai-ui-v6.html` (**12,920 lines**, confirmed via `wc -l` this session),
  its stylesheet `G:\Github\Bolt.DIY\vps\assets\daveai-v6.css` (**8,382 lines**), and a Python
  backend, `G:\Github\Bolt.DIY\vps\patches\daveai-production-runtime-20260731\brain_llm.py` (**430
  lines**). *(Verified live)*: it is served by systemd unit `agent-brain.service`
  (`loaded/active/running`), running `/opt/agent-brain/venv/bin/python -m uvicorn brain_api:app
  --host 127.0.0.1 --port 8888`. This resolves an item the architecture map left open (§9 item 3:
  none of the six `pm2` processes matched it — correct, because it isn't a pm2 process at all; it's
  systemd). The `app/` Remix folder in this same repo is a separate, disconnected bolt.diy scaffold
  sharing no code with any of this — low priority, not what a visitor experiences. Full detail:
  `G:\Github\Bolt.DIY\docs\DAVEAI_ARCHITECTURE_MAP_20260915.md`.
- **A section-by-section bug audit of that real source is in progress, not complete.** Per
  `G:\Github\Bolt.DIY\docs\DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`: **133 candidate findings, 83
  independently confirmed real, 50 pending re-verification** after an unrelated rate-limit
  interruption — the 50 are *not* confirmed false, they're unresolved. Check that document's own
  header before trusting this count; it was still being finalized as this handoff was written, and a
  companion contract kit (see below) explicitly says *"re-check `DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`
  directly for the current number, since it may have moved since this kit was written."*
  Three findings were flagged by independent verifiers as **understated severity**, each now pinned
  to the phase contract that owns the relevant file section so they can't be silently deprioritized:
  - **Iframe sandbox escape**, *(verified directly by this document, `vps/daveai-ui-v6.html:1808-1812`)*:
    the AI-generated preview iframe's own adjacent comment reads *"SECURITY: allow-scripts +
    allow-same-origin can escape sandbox. We use allow-scripts only for user-generated previews"* —
    but the actual attribute on the very next line is
    `sandbox="allow-scripts allow-same-origin allow-forms allow-popups"`, i.e. it ships with exactly
    the combination its own comment names as unsafe. Owned by `CT-001` (chat completion), finding
    `F-P1-01`. Not yet fixed.
  - **Unauthenticated admin panel**, *(reported — not personally reproduced by this document or, as
    far as recorded, by anyone yet)*: opens with zero auth check and immediately leaks internal infra
    details, including the raw VPS IP and internal service ports — verifiers noted this defeats the
    entire point of running behind Cloudflare. Partial lead only:
    `G:\Github\Bolt.DIY\vps\patches\daveai-production-runtime-20260731\nginx\daveai.tech` around line
    210 defines `location = /api/admin/login` proxying straight to the backend on `:8888`, but this
    repo's copy of `brain_llm.py` has **no matching admin-route handler at all** (confirmed via
    grep) — the real implementation isn't in this repo copy. Owned by `CT-000` (stop the bleeding),
    finding `F-P0-05`.
  - **Inaccessible settings toggles**, *(verified directly by this document,
    `vps/daveai-ui-v6.html:266-270`)*: the settings toggle `<input type="checkbox" id="stg-ext-cb">`
    is wrapped in a `<label>` that contains only the checkbox and a decorative slider `<span>` — the
    actual descriptive text ("Show file extensions") lives in a sibling `<div>` outside that label,
    with no `aria-label`/`aria-labelledby` connecting them. The checkbox has no accessible name at
    all. This pattern repeats for roughly 23 toggles in the Settings modal, plus the primary sign-in
    form. Verifiers flagged this as a **WCAG Level A failure that blocks screen-reader users from the
    app entirely**, not a minor polish gap. Owned by `CT-002` (menu/nav polish), findings `F-P2-01`
    / `F-P2-02`.
- **A reconciliation comparing the older March 2026 modular split (`G:\VPS\daveai-v7\`) against
  current production completed cleanly (13/13 agents succeeded** — per
  `DAVEAI_ARCHITECTURE_MAP_20260915.md` §6; *reported*, not independently re-run by this document).
  Current production has gained real functionality since March that `daveai-v7/` never saw: a manual
  per-message agent-routing override, an approval/governance gating layer, a "narrator-first" routing
  gate that splits conversational messages from action messages, and a ~100-tool agent-attribution
  catalog. **`daveai-v7/` is a useful structural pattern, not a safe drop-in replacement.**
- **Both of the above (the 133-item audit and the v7 reconciliation) still need a final merge pass
  into `DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`.** As of this writing that document does not yet
  contain the full 133-item list or the full reconciliation detail — the architecture map says so in
  four places (§4.3, §6.3, §7, §10), and `CT-000-stop-the-bleeding.json` states plainly: *"No
  consolidated ledger of all 133 findings exists in this repository as of 2026-09-15."* Check the
  roadmap doc's own top section — this may have changed by the time you read it.
- **A ground-truth danger exists right now, at a specific, confirmed line.** *(Verified live)*
  `G:\Github\Bolt.DIY\vps\daveai-project-catalog.json` line 43 still contains the rejected/broken
  game entry:
  ```json
  { "id": "srv-game-checkers-crowning", "name": "Checkers Crowning Draft", "url": "https://daveai.tech/checkers-game-crowning-jumping-do-not.html", "cat": "games", "status": "needs-fix", "embed": true, "description": "Agent-created page with mismatched checkers/hangman history; kept visible but not accepted." }
  ```
  Production already replaced this by hand weeks ago. **Do not redeploy this file as-is** — doing so
  puts the broken page back in front of users. A separate, presumably-safe entry (`srv-game-checkers`,
  line 39, pointing at `/checkers.html`) already exists, but confirm against live production which
  entry/URL is actually correct before editing — don't assume line 39 is automatically the fix.
  Designated fix location: `G:\Github\Bolt.DIY\docs\contracts\CT-000-stop-the-bleeding.json`, item 1.
- **The contract kit is now complete — but it appeared while this very document was being written.**
  `G:\Github\Bolt.DIY\docs\DAVEAI_CONTRACT_KIT_20260915.md` did **not** exist when this session
  started checking for it; it and `G:\Github\Bolt.DIY\docs\contracts\CT-INDEX.json` were both written
  to disk by a separate, unidentified process partway through this session (file timestamps: both
  created within the last hour of this document being written). The full kit, as it now stands:
  the overview doc plus `docs\contracts\CT-INDEX.json` (machine-readable index) and six phase
  contracts — `CT-000-stop-the-bleeding.json` through `CT-005-strategic-decisions.json` — matching the
  roadmap's five-phase-plus-decisions structure. **All of this is still untracked in git** as of this
  writing (see "How to verify," git-hygiene note, below) — it will not survive a careless `git clean`
  or a fresh clone of this branch.
  **Load-bearing fact, easy to miss: nothing in this kit is authorization to start work.** Per
  `DAVEAI_CONTRACT_KIT_20260915.md` §7, "The standing go/no-go gate": *"Producing this contract kit
  is preparatory work — it is not, by itself, the owner's authorization to begin editing
  `vps/daveai-ui-v6.html`, `brain_llm.py`, or anything else in scope."* Every one of the six
  contracts' `status` field is `not_started`. Before picking up `CT-000` or any later phase, confirm
  an actual, dated start signal from the owner is on record — do not infer permission from the
  kit's existence alone.
- **Plan in progress, not yet started:** a clean, modular rebuild at `G:\VPS\daveai-website\`, using
  `daveai-v7` as the structural pattern but populated with current content per the reconciliation
  findings above. *(Confirmed live: this directory does not exist yet.)*

---

## Map of where everything actually lives

Full detail — including the complete cross-drive table and a diagram of how these pieces relate — is
in `G:\Github\Bolt.DIY\docs\DAVEAI_ARCHITECTURE_MAP_20260915.md`, §4 and §5. Summary only:

| Location | What it is | Live at daveai.tech? |
| --- | --- | --- |
| `G:\Github\Bolt.DIY\vps\` | The real production source: `daveai-ui-v6.html`, `assets\daveai-v6.css`, `patches\daveai-production-runtime-20260731\brain_llm.py`, `daveai-project-catalog.json`. | **Yes.** |
| `G:\Github\Bolt.DIY\app\` | Stock, unmodified bolt.diy/Remix chat app. Zero "DaveAI" references anywhere. Deploys to an unrelated Cloudflare Pages project named "bolt". | No — parked, low priority. |
| `G:\Github\Bolt.DIY\docs\contracts\` + `docs\DAVEAI_CONTRACT_KIT_20260915.md` | The phase contract kit (see above). Untracked in git as of this session. | Planning artifacts, not code. |
| `G:\VPS\` | A separate, sprawling local workspace outside this repo entirely. Has a `.git` folder with **zero commits ever**. Contains `CLAUDE.md` (source of several standing rules above), `daveai-v7\` (real March-2026 modular split, structural pattern only), `agentic-ui\` (Next.js, likely source of `/studio`), `daveai-web-pages-launcher-20260529\` (likely source of `/web-pages.html`), `daveai\` (a much bigger parked Docker-Compose multi-agent vision), and dozens of dated scratch/wave/backup directories from many past agent sessions. | No — none of it is currently live. |
| `G:\VPS\daveai-website\` | Planned clean modular rebuild. | Does not exist yet (confirmed live, this session). |
| `G:\VPS\docs\` | A **different** `docs` folder than the one in the Bolt.DIY repo. Do not confuse the two when a path just says `docs\something.md` without the drive/repo root spelled out. | N/A |
| `K:\private\.env` | Hostinger API token and other credentials. | Existence/purpose only — never read or reproduce its contents. |
| `S:\Github\DAVE-AI-HARNESSED-CONTRACT-KIT-v1.0.0` | A reusable, mobile/Android-focused audit/contract methodology, not DaveAI-specific in content. `docs\contracts\CT-0XX-*.json`'s per-phase JSON shape (index + contracts + evidence/definition-of-done fields) is explicitly modeled on this kit's structure only — nothing about chat, catalogs, or accessibility comes from it. | Reference only. |
| `G:\Github\Bolt.DIY\.hermes3d_orchestrator\` | Local state for an MCP multi-agent lock/coordination tool used by coding-agent sessions on this machine. Untracked in git. **Not the same "Hermes" as** the Hermes-agent backend-bridge concept in `G:\VPS\CLAUDE.md`, or the `hermes1`–`5`/`hermestv` containers on the VPS — three unrelated things share one name. | Tool state, not a DaveAI product component. |
| `G:\Github\Bolt.DIY\proofs\` | Real E2E/audit evidence (screenshots, JSON) from the 2026-07-31 sessions. Untracked in git. | Historical evidence — keep it, it is not disposable scratch. |

---

## Read these next, in order

1. **`G:\Github\Bolt.DIY\docs\DAVEAI_ARCHITECTURE_MAP_20260915.md`** — read this first. Full
   production topology, the multiple-codebases reality, the v7 reconciliation, and a freshness table
   for every other doc in this list.
2. **`G:\Github\Bolt.DIY\docs\DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`** — the phased plan (Phase 0
   "stop the bleeding" through Phase 5 "open strategic questions"), the findings behind the
   133/83/50 numbers above.
3. **`G:\Github\Bolt.DIY\docs\DAVEAI_CONTRACT_KIT_20260915.md`** and
   **`G:\Github\Bolt.DIY\docs\contracts\CT-INDEX.json`** — confirmed to exist as of this writing (see
   "Current state" above for the story of exactly how current that confirmation is). Start at
   `CT-INDEX.json` to find which of the six `CT-0XX-*.json` phase contracts applies to the work
   you've been asked to do, then read that one contract in full before touching anything. Re-check
   both paths yourself regardless — this kit was still being assembled by another process minutes
   before this sentence was written.
4. **`G:\Github\Bolt.DIY\docs\DAVEAI_SYSTEM_MAP.md`**, **`DAVEAI_PORT_REGISTRY.md`**,
   **`DAVEAI_SUBDOMAIN_STATUS.md`** — dated 2026-05-30/05-31. The architecture map found these
   describe a **since-superseded** backend (a Next.js server on `:3001` behind Authelia auth, a much
   wider live-subdomain list) that does not match today's verified topology (static HTML +
   `agent-brain` on `:8888`, systemd-supervised). Treat with caution; do not trust their topology over
   the architecture map §2.
5. **`G:\Github\Bolt.DIY\docs\DAVEAI_PRODUCTION_E2E_AUDIT_20260731.md`** — the July 31 production
   truth table (what was proven working, with proof-file citations) that the RC1→RC2 handoff and this
   document both build on.
6. **`G:\Github\Bolt.DIY\docs\DAVEAI_RC1_TO_RC2_HANDOFF_20260801.md`** — the previous master handoff
   in this same style, written for a PC/Codex switch. Still accurate on the `agent-brain:8888` →
   Ollama topology and the E2E runner.
7. **`G:\Github\Bolt.DIY\docs\DAVEAI_RC2_E2E_ROADMAP_20260801.md`** — the RC2 completion matrix
   (public E2E, auth-chat E2E, games, StreamHub, LiteLLM, VPS maintenance, docs) this project was
   working through before the 2026-09-15 audit wave started.
8. **`G:\VPS\CLAUDE.md`** — the standing Claude/Codex/Windsurf coordination contract, dated
   2026-05-24. Source of several of the standing rules above and of the full "Stop Conditions" list.

---

## How to verify anything you're told (including this document)

Every command below was run live while writing this document, on 2026-09-15, from a Claude Code CLI
session on the machine this copy was written on. Re-run them yourself rather than trusting the output
pasted here — it is already stale by the time you read it, on a project with no deploy pipeline (see
architecture map §4.3).

**Production health:**
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://daveai.tech/api/health     # -> 200
curl -s -o /dev/null -w "%{http_code}\n" https://brain.daveai.tech/health   # -> 200
curl -s -o /dev/null -w "%{http_code}\n" https://api.daveai.tech/health     # -> 200
curl -s -o /dev/null -w "%{http_code}\n" https://voice.daveai.tech/        # -> 200, but see caution above: static page, not proof the TTS backend works
curl -s -o /dev/null -w "%{http_code}\n" https://iptv.daveai.tech/        # -> 502, confirmed down
```

**SSH access:** the alias `daveai` already exists in `~/.ssh/config` on the machine this document was
written on:
```
Host daveai 187.77.30.206
    HostName 187.77.30.206
    User root
    IdentityFile ~/.ssh/id_ed25519
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
```
(The comment sitting above that block in the actual config file calls it a "SlitherWorm game server"
— that label is stale/mislabeled from an unrelated prior use of the same alias name; the `Host` line
itself and the IP are correct for DaveAI.)
```bash
ssh daveai uptime   # -> "44 days..." (verified this session; consistent with no reboot since today's firewall incident)
```
**This is machine-specific.** A new machine or a fresh agent sandbox will not have this key
authorized. One prior claude.ai chat session (`C:\Users\Admin\Downloads\daveai-vps-handoff.md`) found
outbound SSH **totally blocked** from that sandbox; this Claude Code CLI session found it works fine.
Don't assume either way — test it, and if it fails, the onboarding steps that worked before are in
that same file: generate a keypair, have the owner paste the public key into
`~/.ssh/authorized_keys` via Hostinger's web console (hPanel → VPS → Web console), then test again.

Once SSH works, these are the read-only commands that produced the "Current state" facts above — safe
to re-run, nothing here changes production:
```bash
ssh daveai "ss -ltnp | grep -E ':5050|:3103|:8888|:11434'"    # what's actually listening
ssh daveai "systemctl status agent-brain.service"              # chat backend supervisor
ssh daveai "pm2 jlist"                                          # the six daveai-* processes (none of which is agent-brain)
ssh daveai "docker ps -a --format '{{.Names}}\t{{.Status}}'"    # iptv/hermestv container status
```

**End-to-end test runner:**
```powershell
cd G:\Github\Bolt.DIY
npm run test:daveai:prod
```
This runs `node vps/production-e2e-runner.cjs` (defined in `package.json`). Set `$env:DAVEAI_PROOF_DIR`
first (PowerShell) to control where proof artifacts land; set `$env:DAVEAI_E2E_EMAIL` /
`$env:DAVEAI_E2E_PASSWORD` to also run the authenticated-chat assertion. Last reported result,
2026-08-01: `6 passed, 0 failed, 1 skipped` (the skip was authenticated chat, for lack of
credentials) — re-run it, don't assume that result still holds four months later on a system with no
deploy pipeline.

**Source control / PR state:** *(verified live)* draft PR **#2186**, "Persist DaveAI production
runtime repairs," against `stackblitz-labs/bolt.diy`, still `DRAFT`, +40226/−0
(`gh pr view 2186 --repo stackblitz-labs/bolt.diy`). This repo's remotes: `origin` =
`Ghenghis/bolt.diy` (fork), `upstream` = `stackblitz-labs/bolt.diy`. A CI workflow exists at
`G:\Github\Bolt.DIY\.github\workflows\daveai-production-e2e.yml` — check its last run
(`gh run list --workflow daveai-production-e2e.yml`) before assuming it's green.

**Git-hygiene warning specific to this checkout, verified live this session:** `.gitignore` has an
old, broad `*.md` rule (line 48) that ignores every markdown file in the repo by default, with
specific `!docs/DAVEAI_X.md` negation lines added underneath to re-include each named handoff/audit
doc one at a time. As of this writing, the working copy of `.gitignore` has **four negation lines that
are not yet committed** (`git diff -- .gitignore` shows them as pending additions) — for
`DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`, `DAVEAI_ARCHITECTURE_MAP_20260915.md`,
`DAVEAI_CONTRACT_KIT_20260915.md`, and this file, `DAVEAI_HANDOFF_20260915.md`. If anyone discards
working-tree changes to `.gitignore` (a careless `git checkout -- .gitignore`, `git stash`, or reset)
before these lines are committed, all four of these documents silently become un-trackable by git
again — the files stay on disk, but `git add` will refuse to pick them up until the negation lines are
restored. **A related quirk observed live this session:** immediately after a new file lands directly
in `docs/` on this Windows checkout, plain `git status` can fail to list it at all (neither `??` nor
`!!`) even though it is genuinely untracked-and-not-ignored — confirmed by
`git status --porcelain -uall -- <path>` and `git ls-files --others --exclude-standard -- docs/`
showing it correctly when `git status` alone did not. It self-corrected within the same session with
no action taken. If a file you expect to see under `docs/` seems to be missing from a plain
`git status`, don't conclude it isn't there — check with an explicit pathspec or `-uall` before
assuming.

**How to verify this document itself:** every fact above marked "(verified live)" was reproduced with
the exact commands in this section, in this session. Facts marked "reported" were not — they're
copied from another doc's own claim. If you find either category is now wrong, that is expected
eventually (see the standing note at the top of this document) — fix the doc, don't just quietly work
around the discrepancy.

---

## Incident log

*(Append future incidents below. Do not delete or rewrite history — correct forward, in a new entry,
the way the rest of this project's docs do.)*

### 2026-09-15 — Hostinger firewall group swap took the entire site offline

| | |
| --- | --- |
| Symptom | `daveai.tech` and every subdomain returned Cloudflare 522; nothing reachable on 22/80/443 from outside. |
| Root cause | A Hostinger cloud firewall group named **"Claude"**, created earlier the same day (`2026-09-15T01:48 UTC`) by a prior session with exactly one rule (`TCP 22` from a single `/32` IP), became the **sole active** firewall group on the VPS — Hostinger allows only one active group at a time — replacing the correct group, **"Kilo"** (id `263387`; `TCP 22/80/443/5050/8080` from anywhere), active since April. With no 80/443 rule active, Cloudflare could not reach the origin at all. |
| Fix | Reactivated the "Kilo" firewall group via the Hostinger API, with the owner's explicit go-ahead. |
| Verification | Same day: health endpoints returned 200 across the board, `ssh daveai uptime` succeeded showing no reboot had occurred (only the firewall blocked traffic; the box itself stayed up). Re-verified independently while writing this document: production health endpoints still 200, `ssh daveai uptime` still shows continuous uptime. |
| Residual risk | The "Claude" firewall group is now inactive but **still exists** on Hostinger. Low urgency — its only rule pointed at a sandbox egress IP that reportedly can't use SSH productively anyway — but it should be deleted as cleanup at some point. Not yet done as of this writing. |
| Full detail | `G:\Github\Bolt.DIY\docs\DAVEAI_ARCHITECTURE_MAP_20260915.md` §3 (includes the full sequence diagram) and `G:\Github\Bolt.DIY\docs\DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` §2. |

---

*Written 2026-09-15. If you update this document, keep both copies (`G:\Github\Bolt.DIY\docs\DAVEAI_HANDOFF_20260915.md` and `G:\VPS\HANDOFF.md`) in sync, and append to the Incident log rather than rewriting it.*
