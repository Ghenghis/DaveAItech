# DaveAI v7 Reconciliation — Porting Reference (2026-09-15)

## Overview

**What this compares:** `G:/VPS/daveai-v7/` (dated March 2026 — a modular split of the DaveAI
product into `index.html` + 12 `js/` files + 10 `css/` files, one file per feature area) against
the live/current production source: `G:/Github/Bolt.DIY/vps/daveai-ui-v6.html` (~12,920 lines,
one hand-written file) plus its backend,
`G:/Github/Bolt.DIY/vps/patches/daveai-production-runtime-20260731/brain_llm.py`. Twelve areas
were compared independently: agents, app-init, auth, canvas-games, chat, config, panels,
personality, state, status, tools, voice.

**Why:** the owner wants a clean, modular rebuild at `G:/VPS/daveai-website/` (planned, not yet
created) that follows `daveai-v7`'s proven module-boundary pattern. But `daveai-v7` predates
roughly five months of continuous production feature work, bug fixes, and an ongoing accessibility
hardening pass. Before anything gets ported, the team needs a module-by-module answer to three
questions: what current has that v7 never did (must port forward), what v7 had that current
dropped (needs an explicit human revive-or-leave-behind call), and where the two designs
deliberately diverge (needs a product decision). This document is that answer.

**Method:** 12 parallel agents each independently read both sides' source in full for one area,
followed by one synthesis pass combining all 12 into a single prioritized porting plan. All 13
agents (12 comparisons + 1 synthesis) completed cleanly. Cross-checked here: the totals in the
synthesis's own "at a glance" tally (54 `onlyInCurrent` items, 7 `onlyInV7` items, 61 total
`evolvedDifferently` comparisons with 10 marked unclear, 0 favoring v7 outright) match an
independent recount of all 12 raw comparison outputs performed while writing this document.

**Data quality:** all 12 areas returned substantive, evidenced comparisons — none came back sparse
or empty. Several areas do carry explicit lower-confidence caveats where v7's given source files
show signs of corruption/truncation from whatever process split the original monolith (e.g.
`app.js`'s dead double-nested `DOMContentLoaded`, `panels.js` truncated mid-function twice,
`canvas.js`'s `demoPlay` logic mislabeled `startPolling` and referencing an undefined `url`,
`personality.js`'s brace-unbalanced `buildPersonalityPrompt`, `state.js` cut off mid-body), or
where v7 has sibling modules outside a given area's two reviewed files (e.g. agents.js referencing
functionality that plausibly lives in v7's own separate `voice.js`/`tools.js`). Those caveats are
preserved inline below, not smoothed over.

**Citation convention used below:** `vps/daveai-ui-v6.html:LINE` means current source, relative to
the Bolt.DIY repo root (`G:/Github/Bolt.DIY/`); `daveai-v7/js/<module>.js:LINE` means v7 source,
relative to `G:/VPS/`. Line numbers are as reported by each comparison agent (`~` prefix in the
source data preserved where the agent itself marked a number as approximate).

**Related docs:** this is the detailed reconciliation reference that
[`docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`](./DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md) still needs
merged into it (its own pending-update note says so), and that
[`docs/DAVEAI_ARCHITECTURE_MAP_20260915.md`](./DAVEAI_ARCHITECTURE_MAP_20260915.md) §6 already
summarizes at a headline level ("full reconciliation findings ... will live in
`docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` once that document's pending update pass lands").
Read the roadmap doc for the wider phased plan this fits into and the architecture map for full
production topology. Nothing here supersedes either — this supplies the depth both flagged as
still pending.

### Contents

- Overview (this section)
- Full Synthesis: Prioritized Porting Plan — the complete porting-plan deliverable, reproduced faithfully
- Area-by-Area Detail — all 12 areas, condensed to actionable items (personality and voice in full detail)
- What This Means for daveai-website/

---

## Full Synthesis: Prioritized Porting Plan

*The following is the complete synthesis produced by the reconciliation workflow, reproduced
faithfully (verbatim content; heading levels only have been shifted down by one so it nests under
this document's own headings).*

## DaveAI.tech Modular Rebuild — Prioritized Porting Plan

### Source materials and method

- **v7 (March 2026, modular split)** — `G:\VPS\daveai-v7\js\{agents,app,auth,canvas,chat,config,panels,personality,state,status,tools,voice}.js` + matching `css/*.css`. Used here only as the **structural template** for module boundaries — not as a source of logic to copy. Several v7 files show real signs of corruption/truncation from whatever process split the original monolith (app.js's dead double-nested `DOMContentLoaded`, panels.js truncated mid-function twice, canvas.js's `demoPlay` logic mislabeled `startPolling` and referencing an undefined `url`, personality.js's brace-unbalanced `buildPersonalityPrompt`, state.js cut off mid-body). Treat v7 as "where the seams go," not as working code to restore verbatim.
- **current (July 2026, live production)** — `G:\Github\Bolt.DIY\vps\daveai-ui-v6.html` (one ~12,920-line file) + external `assets/daveai-v6.css` (not reviewed line-by-line for most areas — check it directly before assuming a v7-only CSS class is truly gone) — this is the **functional ground truth** the new build must match or exceed.
- **Backend** — `G:\Github\Bolt.DIY\vps\patches\daveai-production-runtime-20260731\brain_llm.py`: LLM streaming/fallback, ReAct-stream filtering, and per-agent progress/model writes only. Tool-calling and health-check logic live in a separate `brain_graph.py`, not covered by these comparisons.

**Overlap map** — a few mechanisms surface under multiple area headings because the JSON areas' Side-A file pairs overlap. Each is implemented **once** below, cross-referenced from every area that mentions it: the JWT/session/`_currentUser` layer (Auth, App-init, State), the chat auth-gate (Chat, Auth), manual agent-pin (Chat, Agents), narrator routing (Agents, Config), the Projects/game-catalog system (State, Canvas-games), BrainState health polling (Panels, Status), and right-panel resize (Panels, App-init).

### At a glance

- **54** `onlyInCurrent` items → concrete porting tasks (Section 1)
- **7** `onlyInV7` items → human call needed, revive-or-leave-behind (Section 2)
- **10** `evolvedDifferently` findings marked unclear → collapsing into **7** distinct product decisions (Section 3)
- **0** `evolvedDifferently` findings favored v7 outright, out of ~61 total comparisons — the remaining ~51 favored current and need no decision, only implementation

---

### 1. Porting tasks: every `onlyInCurrent` capability, in build order

#### Tier 1 — Chat, Auth, Session/Data Layer
*Nothing else works until these do. "State" is placed here rather than in Tier 4 because its content — `_currentUser`, the token layer, `_dbFetch` — is what Chat's persistence and Auth's gating actually run on.*

##### Chat
- [ ] **Sign-in gate before send** — `think()` calls `isAuthenticated()` before clearing the input or hitting `/api/stream`; shows the auth modal and logs "Sign in required before chat can run." *(daveai-ui-v6.html:4197-4212 — same mechanism referenced under Auth)*
- [ ] **Human-in-the-loop approval workflow** — `completion_gate`/`artifact_contract.preview_url` handling; `approval_required|granted|denied|timeout` SSE event types; `renderDaveAIApproval`/`resolveDaveAIApproval`/`updateDaveAIApproval` POSTing to `/api/approvals/:id`. *(4319-4346, 4506-4578)*
- [ ] **UI/session context + personality prompt on every request** — `getDaveAIUiContext()` (page_url/preview_url/project_id/device_mode/panel/app_mode) plus `system_prompt`/`session_id`/`project_id`/`project_name`/`ui_context` folded into the SSE payload. *(4110-4133, 4271)*
- [ ] **Server-side chat persistence, analytics, and Memory pane** — `_addToMemory`, `_dbSaveChat`, `_dbTrack('chat_send', …)`, plus the Memory pane UI. *(4229, 4449-4450, 2297-2310 — build as one module with the Memory-pane items under Panels/State)*
- [ ] **Manual agent-pin UI** — `setAgent(role)`/`pillClick(short)` force Supervisor/Coder/QA/Asset instead of auto-routing. *(4178-4195 — identical to Agents item below; implement once)*

##### Auth
- [ ] **JWT-claims session validity** — `getTokenClaims()` (decodes JWT payload) + `isAuthenticated()` (token presence + local TTL + decoded `exp`), replacing a bare local-timestamp check; used at 20+ gate sites. *(2378-2395)*
- [ ] **Global 401 fetch guard** — `installAuthFailureFetchGuard()` patches `window.fetch` once at boot; any same-origin, non-public `/api/*` 401 calls `handleAuthFailure()` (clears token/user, shows auth modal). *(2396-2421)*
- [ ] **Hard auth gate inside chat send** — same as Chat item above; implement once, call from both.
- [ ] **Accessible sign-in/sign-up tabs** — real `role="tablist"`/`role="tab"`/`aria-selected`/`aria-controls`/`tabindex` + `activateOnKeyboard()`, plus `aria-label` on admin user-management buttons. *(1203-1208, 2336-2342, 2451-2456)*
- [ ] **`_isCurrentUserAdmin()` helper** — one shared admin check, replacing 5+ inline copies of `_currentUser?.role === 'admin'`. *(2436-2438 — note: current only migrated ~half its call sites; finish the migration during the port rather than re-introducing the inline pattern)*

##### State (session + data layer)
- [ ] **Ambient UI-interaction state block** — keep as its own never-persisted module: `curTgt`, `micOn`, `rpOpen`, `ppOpen`, `selLayout`, `curPanel`, `curFpTab`, `curRpTab`, `curDeviceMode`, `curToolRole`, `toolSearch`, `sessionHistory`, `micRecognition`, `activeToolName`. *(2344-2349)*
- [ ] **JWT token layer + fetch guard** — same mechanism as Auth above. *(Note: v7's `state.js` calls `clearToken()` without ever defining it — it likely lived in a v7 `auth.js` not covered by this review, so treat "new since March" here with slightly lower confidence than the rest of this list.)*
- [ ] **Projects: server-catalog + server-DB merge/reconciliation** — `SERVER_PROJECT_CATALOG_URL`/`PROJECTS_LOCAL_KEY`/`LAST_PROJECT_KEY`/`PROJECT_CATALOG_HOST_STATUS`, `normalizeProjectRecord`/`mergeProjects`, `loadServerUserProjects`, `setLastActiveProject`/`findLastActiveProject`/`resumeLastProject`, `loadServerProjectCatalog`, `shouldUseLaunchCard`/`projectLaunchCardUrl`, `syncRuntimeProject`. v7's Projects was a flat localStorage array with a 5-item hardcoded seed. *(9121-9470 — same system as Canvas-games items below; one Projects module serving both areas)*
- [ ] **Edit Profile modal** — `_renderProfileContent()`/`_saveProfile()`, PATCHes `/api/db/users/:id`, updates `_currentUser`/`daveai_user`. *(10380-10453)*
- [ ] **Always-on dashboard metrics poll** — `_refreshDashboardCards()`, 30s interval, for every visitor (distinct from the admin-only VPS dashboard). *(10760-10782)*
- [ ] **Expanded project seed catalog + URL cleanup pass** — 9 seed rows instead of 5, plus a defensive loop repairing/retiring malformed or dead-link seed URLs on load. *(9339-9375 — see Section 3F for a guard-condition decision buried in this same code)*

#### Tier 2 — Panels & Status

##### Panels
- [ ] **Memory tab/pane** — third right-panel view (`rp-memory-pane`/`rpm-list`), backend-driven, skeleton/empty/error+retry states, location badges (vps/local/local-private/git), SSE-triggered refresh (`_memoryHandleSse`). *(2297-2310, 12693-12909 — one module with the Memory-pane items under Chat/State)*
- [ ] **History pane content logic** — `chatHistory` + localStorage persistence, capped-at-50 render with click-to-replay, live search with highlighting, Markdown export, clipboard copy with `execCommand` fallback. *(4899-4988. Standardize on the absolute-index replay approach — `replayHistoryAbs` — rather than v7/current's other position-shifting `replayHistory`, which can point at the wrong message once new turns push the window.)*
- [ ] **Persistent raw-activity buffer + redraw on mode switch** — `rawActivities` (capped 300) + `renderCoderActivity()`. *(4753, 4777-4795)*
- [ ] **Right-panel drag-to-resize** — `#rp-resizer` (`role="separator"`, keyboard-operable, min/max clamped) + `setRightPanelWidth(width, persist)` writing a `--right-panel-w` CSS variable. *(2238-2240, 5300-5307 — same mechanism as App-init's `initRightPanelResize()`)*
- [ ] **BrainState single-source-of-truth health poller** — see Status item below; same mechanism, implement once.
- [ ] **Second "Phase A1" command palette** — `openCommandPalette`/`paletteInput`/`paletteKey`, layered in front of the original Ctrl+K palette (which now delegates to it first). *(2319-2329, ~12238-12280 — when rebuilding, seriously consider merging these into one implementation instead of carrying forward the legacy-plus-delegate arrangement)*

##### Status
- [ ] **Auth-aware polling short-circuit** — `updateStatusBar()`, `fetchAgents()`, `checkApiHealth()` all check `isAuthenticated()` first and skip authenticated-only endpoints for anonymous visitors, showing a "sign in for workspace stats" placeholder. *(~3876-4052)*
- [ ] **Activity-feed logging of real brain connectivity transitions** — `BrainState.observe(...)` logs an activity entry only on genuine online/offline flips, skipping connecting/degraded noise and the first unknown-to-X transition on load. *(~4882-4891)*
- [ ] **Live tool count fanned out to more surfaces** — beyond v7's two targets: `fp-agent-tools-count`, `adm-tools-count`, `adm-tools-summary`, the tool-search placeholder, the sidebar Tools button's aria-label, plus `_syncRuntimeTools(td.tools)`. *(~4062-4078)*

**Also for this tier**: implement `BrainState`/`pollBrain` (documented internally as "Wave-2 #15," a deliberate fix for a real 3-way race between `updateStatusBar`/`fetchAgents`/`checkApiHealth`) as the canonical health module, with flap-suppression (2 consecutive failures before flipping to OFFLINE) and the 5-state enum (online/offline/degraded/connecting/unknown). While doing so, fix two things the diff itself flags as unfinished in current: collapse the **three still-independent** `/api/health` pollers (5s/5s/30s) into one shared fetch feeding `BrainState`, and delete `updateStatusBar`'s now-dead `ok` variable.

#### Tier 3 — Voice, Agents, Personality

##### Voice
- [ ] **99+ English Azure voices catalog** — `VS_VOICES` holds 99 `en-*` Neural entries across 14 locales, matching the CLAUDE.md-mandated reference catalog field-for-field; self-check enforces `VS_VOICES.length >= 90`. *(6537 onward, 8548 — see Section 4, this is the flagship deliverable of the whole area)*
- [ ] **Auth-gated Azure TTS proxy** — `_vsTierAzureTTS` throws when not authenticated; TTS is now signed-in-only. *(7917-7918, 8550-8553)*
- [ ] **"Moshi Instant Voice"** — new real-time voice-conversation mode over a WebSocket bridge (`vsConnectMoshi`, auto-reconnect, `ws://localhost:8998` default), fully separate from the turn-based TTS pipeline. *(1138-1157, 8426-8493 — port as its own module, not merged into TTS)*
- [ ] **Accessibility retrofit of Voice Studio** — `role="dialog"`/`aria-modal`, real ARIA tabs (`role="tab"`, `aria-selected`, roving `tabindex`), keyboard-operable voice cards, real `<button>` quick-picker items, matching `:focus-visible` CSS. *(878-896, 7751, 8900, daveai-v6.css:88-95)*
- [ ] **Safer load-time defaults** — never auto-requests microphone access; narration/auto-read state resyncs both directions to the persisted chat mode instead of only ever forcing "on." *(8859-8869, 8729)*

##### Agents (role pills)
- [ ] **Interactive pill click = manual routing override** — same as Chat's manual agent-pin item; implement once.
- [ ] **Governance "needs proof" bulk agent state** — on a blocked/denied/timed-out approval event, all four pills reset to `state:'idle', task:'needs proof'`; status bar shows "Blocked: proof required." *(4428-4434, paired with 4340-4346)*
- [ ] **Per-agent model name in UI** — flyout + Admin panel show the live model per agent, backed by real backend writes in `brain_llm.py`'s `agent_set(...)`. *(4026-4041; brain_llm.py:324-332)*
- [ ] **Narrator-first routing, encapsulated** — `AGENT_TRIGGERS` + `shouldUseAgentPipeline(msg)`. **Scope note**: v7's `config.js` already had the trigger-regex and narrator-fallback as an inline expression (`AGENT_TRIGGERS.test(msg) || activeAgent !== 'auto'`) — it just wasn't in agents.js and wasn't a named function. What's genuinely new is: encapsulating it into a testable function, excluding `'narrator'` from the manual-override short-circuit, and the `CHAT_ONLY_DIRECTIVE` negation guard (below). Don't scope this as bigger than it is. *(4099-4108, cross-ref Config)*
- [ ] **Per-agent voice assignment** — default per-role Azure voices, populated selects, agent-keyed narration. *(7669, 8234-8236, 8692-8695 — flagged as likely already existing in v7's separate `voice.js`; verify before building from scratch)*
- [ ] **Tools-to-agent attribution catalog** — ~100+ tools tagged with owning agent, heuristic classifier, role-filter buttons, role-colored badges. *(3183-3306, 3324-3328 — flagged as likely already existing in v7's separate `tools.js`; verify before building from scratch)*

##### Personality
- [ ] **"Mode-Aware UI" 9-mode router** — `classifyMode(msg)` + `MODES`/`MODE_ORDER`/`MODE_OVERRIDE_MS`, citing an internal spec ("wave2-handoffs/08"). This is real new work, but it's a **message-routing/navigation** concern, not a personality feature — give it its own routing module; it only reads as "personality" because of where it sits in the single file. *(This is the only genuine `onlyInCurrent` item in this area — see Section 4 for why.)*

#### Tier 4 — Canvas/Games, Tools, Config, App-Init

##### Canvas-games
- [ ] **Browsable multi-game carousel** — `loadCarouselGames()`/`renderCarousel()`/`bindCarouselActionButtons`/`selectCarouselGame`/`launchCarouselGame`/`carouselPrev`/`Next`; real `<button>` cards with `aria-label`/`aria-pressed`. v7 could only show one hardcoded demo game. *(6113-6179)*
- [ ] **Server-hosted project catalog merge** — same system as State's Projects item; feeds the carousel with 20+ real game entries from `daveai-project-catalog.json`. *(9121-9315)*
- [ ] **Game ↔ PostgreSQL postMessage bridge** — `daveai-hiscore`/`daveai-map-progress`/`daveai-get-leaderboard` handled via `window.addEventListener('message', …)`, persisted via `_dbSaveHiScore`/`_dbSaveMapProgress`/`_dbGetLeaderboard`. *(6027-6059)*
- [ ] **Cross-origin "launch card" fallback** — `shouldUseLaunchCard`/`projectLaunchCardUrl` route auth-walled/cross-origin catalog entries through `/daveai-launch.html` instead of a broken iframe. *(9317-9336)*
- [ ] **Resume-last-active-project + registry export** — `setLastActiveProject`/`findLastActiveProject`/`resumeLastProject`/`downloadProjectRegistry`. *(9239-9296 — same system as State's Projects item)*
- [ ] **Rebuild the launch handler from `demoPlay()`/`loadProject()`**, not from v7's copies (mislabeled `startPolling`/`_syncDemoEditor`, both corrupted extractions) — includes the opt-in (not always-on) voice greeting via `_vsState.narration.gameLaunch`.

##### Tools
- [ ] **Live tool-registry sync from `/api/tools`** — `_runtimeToolMetadata`/`_syncRuntimeTools` reconcile the static 113-entry registry against the backend's real manifest on every health check. *(3309-3352, wired at 4052-4086)*
- [ ] **Capability-broker-gated slash commands** — `/diff`, `/commit` etc. marked `locked: true`, routed through `slashLocked()` instead of executing directly — same broker-approval convention as the Tools-panel Run flow. *(12199-12200, 12399-12401)*
- [ ] Also port (evolved, not `onlyInCurrent`, but no decision needed — current is unambiguously better): the destructive-action-aware `runToolApi()` that composes an approval-gated chat request instead of firing `/api/run-tool` directly; `authHeaders()` on the DB quick-query endpoint; ARIA/keyboard operability on tool and skill list rows.

##### Config
- [ ] **`CHAT_ONLY_DIRECTIVE` negation regex** — stops "don't build X, just answer" from being misrouted into the heavy pipeline. *(4102, 4106)*
- [ ] **Memory-context personalization** — `_DEFAULT_PERSONALITY.memoryEnabled`/`memorySize`, injected into `buildPersonalityPrompt()`. *(9570-9584, 9656-9660 — flagged as possibly already present in v7's separate, unreviewed `personality.js`; verify before treating as net-new)*
- [ ] **Local-LLM / auto-refresh config keys** — `_LLM_KEY`/`_REFRESH_KEY`. Give these an explicit home (config module, or hand off to whichever module owns local-LLM switching — no v7 config module currently claims them). *(9572-9573)*
- [ ] **Cleanup, not a port**: delete the config drift that accumulated with no module boundary to prevent it — `SB_AGENT_COL`, two ad-hoc `roleCol` literals, an inline `agentColors`, and the inverse `shortByRole` map are all re-declarations of the one canonical `AGENT_COLORS`/`AGENT_NAMES` pair. Have every call site import the single source instead of carrying the duplication forward.

##### App-init
*(Most items here duplicate Auth/State/Panels above — listed for completeness, implement once.)*
- [ ] JWT-claims session validation — duplicate of Auth.
- [ ] Global fetch 401 guard — duplicate of Auth.
- [ ] `_setCurrentUser()` normalizer + `window` mirror + `_isCurrentUserAdmin()` — duplicate of Auth/State; this is what fixes `_dbSyncUser`'s otherwise-unsatisfiable `.name` guard, so make sure it's genuinely the *only* place `_currentUser` gets assigned.
- [ ] **Boot-time accessibility auto-labeling pass** — every `button[title]:not([aria-label])` gets `aria-label` mirrored from `title`, on `DOMContentLoaded`. Run this **first** in the new init sequence. *(10512-10515)*
- [ ] `initRightPanelResize()` — duplicate of Panels.
- [ ] **`setFpTab()` ARIA attributes + per-tab content dispatch** — `aria-selected`/`tabindex`, and the tab switch now actually calls each tab's render function (`renderTools`/`renderProjects`/`loadPagesPanel`/`_renderDbPanel`/`_renderSkillsPanel`) instead of only toggling visibility. *(3036-3052)*
- [ ] **Port the whole workspace-layout engine** (`applyWorkspaceLayout` + the rail/activity/chat/density/status schema + stable-id persistence + saved-panel-width restore) — v7's `layouts` array is a non-functional color-swatch name picker; current's is the real, DOM/CSS-variable-mutating implementation. This is a straight port, not a merge. *(2608-2805)*
- [ ] Use current's single top-level `DOMContentLoaded` handler as the reference shape for the new bootstrap entrypoint, not v7's (which registers `DOMContentLoaded` twice, nested, making session-restore/the token watchdog/`renderHistory` dead code as given).

---

### 2. `onlyInV7` items — human call required (revive vs. leave behind)

These were **removed or replaced**, not simply missed. Do not port any of these back silently — each needs an explicit yes/no from whoever owns the product.

#### Cluster: local/self-hosted TTS (4 items — decide as ONE bundle, not four)
The current build deliberately neutralized every non-Azure voice path in favor of a single cloud engine. Reviving any one of these only makes sense if the team decides it wants a non-Azure fallback tier at all — see the matching product decision in Section 3G, which is the same question from the other side.

- **Multi-engine self-hosted TTS backends** (AllTalk, Kokoro, Chatterbox, LM-Studio-TTS, Custom-TTS) with real, working API integrations. Current hard-stubs all of it (`_localVoiceSpeak` returns `false`, `_getLocalLLM`/`_saveLocalLLM` force `voiceEngine: 'none'`) and tells users "DaveAI voice is Azure Neural only." *(v7 personality.js — full fetch implementations per engine)*
  **Decision needed:** revive as an optional local-engine tier, or confirm Azure-only is the permanent architecture.
- **4-second TTS "failsafe" timer** with a spoken warm-up line ("Hey! I'm Dave, AI. The main LLM is warming up…") when every real engine is slow. Only makes sense if a non-Azure tier exists to speak through. *(v7 voice.js:638-648)*
  **Decision needed:** revive in some form (even just a "voice is taking longer than usual" toast) once/if any fallback tier returns.
- **Rich 6-check engine diagnostics in `vsCheckEngine`** (Web Audio, browser-voice count+score, Kokoro/Chatterbox ping, HuggingFace test call, Edge TTS proxy health, audio-output resume test) feeding a computed "best engine" ranking. Current's 3-check version is a reasonable simplification *given* only one engine remains. *(v7 voice.js:1480-1621)*
  **Decision needed:** only relevant if the fallback-tier question above is answered "yes."
- **Original 22-voice Kokoro-ID catalog** with differentiated reliability grades (A through D+), plus an already-built Kokoro→Edge/Azure name map (`_vsEdgeVoiceMap`) that current's one-time migration didn't reuse — it just hard-resets every returning user to Maisie. *(v7 voice.js:264-289, 812-828)*
  **Decision needed:** independent of the bigger fallback question, consider reusing the existing ID map so returning users keep a voice "personality" close to their old choice instead of a blanket reset — this is cheap regardless of what happens with local engines.

#### Cluster: entry-funnel video timing (see also Section 3A — same underlying decision)
- **Post-sign-in welcome-video replay with TTS ducking** — v7 played the intro video after *every* successful sign-in (`vsStopAudio()`/`_vsSpeechQueue.length = 0` then `playIntro()`). Current plays it once, pre-auth, on page load, and never replays it on sign-in. *(v7 state.js:32-58)*
  **Decision needed:** revive the replay for the re-auth/forced-relogin case (e.g., the token-expiry watchdog), especially for shared/kiosk terminals — bundle this decision with Section 3A.

#### Standalone items
- **Semantic CSS classes for activity-feed and history rows** (`.ai`/`.ai-hd`/`.ai-dot`/`.ai-name`/`.ai-ts`/`.ai-txt`/`.ai-cm`, `.hist-item`/`.hist-prompt`/`.hist-meta`). Current hand-rolls the same visuals via inline `style=` strings in JS template literals — nothing is visually lost, but the maintainable pattern is gone. *(v7 panels.css:531-575, 613-633; caveat — current's real external stylesheet wasn't reviewed, so double-check these classes aren't already there unused before assuming.)*
  **Decision needed:** this is close to a "just do it" rather than a real toss-up — recommend reviving proper semantic classes (not necessarily the exact old names) in the new CSS module.
- **Distinct red "error" state from `checkApiHealth`'s own non-exception health failure** (a 200-but-unhealthy `/api/health` response), separate from the amber used for offline/connecting. Current's `BrainState` refactor means this specific signal path now paints nothing (`setApiStatus` is a shim that only reacts to `'online'`). *(v7 status.js:61-70, 80-84)*
  **Decision needed:** the underlying simplification (stop secondary pollers from flapping the shared indicator) is sound and shouldn't be undone — but decide whether `checkApiHealth`'s failure should surface *somewhere* (logged, or fed into `BrainState` as a corroborating signal) instead of being silently swallowed.

---

### 3. Product decisions needed (`evolvedDifferently`, marked unclear)

These are places where the code itself won't tell you the right answer — each needs a product call.

**A. Video-first vs. auth-first entry funnel** *(appears in App-init, Auth, and State — one decision, three facets)*
v7: show sign-in immediately, play the intro video only after a successful login, every time. Current: play the intro video once on page load, before auth, and never replay it on sign-in. Current is more defensively wired (`playIntro()` now guarantees a fallback call to `_showAuthIfNeeded()` on every exit path — a broken/disabled intro can never strand a user), but the two designs serve different goals (marketing "wow" moment vs. never wasting an unauthenticated visitor's time). **Decide:** which ordering the new build should use, and separately, whether the post-sign-in replay should come back for forced re-auth / kiosk use.

**B. Copy for "chat completely unreachable"**
v7: specific, actionable — *"Enable Local LLM in Settings → Admin → Local LLM to chat offline."* Current: generic — *"Chat temporarily unavailable. Please try again."* Current's surrounding mechanism (retry/backoff, a real second endpoint attempt) is strictly better; only the final copy regressed, and the admin-gated Local LLM path it used to point to is still tried first. **Decide:** restore actionable copy, or keep it generic.

**C. "Uptime" metric on the status card**
v7: a quantified but mathematically thin 30-day uptime % (resets to 0 on every process restart/deploy, so it isn't a real rolling SLA number). Current: an honest binary Online/Unknown with no trend data. **Decide:** is a real uptime metric — backed by actual monitoring/history, not a single process's `uptime_seconds` — worth building for v2, rather than reviving v7's specific formula as-is?

**D. Voice-input (mic) architecture**
v7: client-side WebSpeech API — free, instant, live interim captions, Chrome/Edge-only, no auth required — plus a MediaRecorder fallback. Current: authenticated Azure server-side transcription — cross-browser-consistent, presumably higher quality, but not instant and requires sign-in. This is a deliberate fork, not a bug on either side; it was only lightly traced in this review and deserves its own dedicated pass. **Decide:** Azure-only, or reintroduce a client-side/offline option alongside it?

**E. `huggingface_download` vs. `model_hub_download` naming**
The one single-entry difference in an otherwise byte-identical 113-tool registry. Low functional risk either way (tool invocation is now a free-text prompt, not an exact key match), but **decide** with whoever owns the backend tool implementation which name should actually ship, before finalizing the new registry.

**F. `seedProjects` URL-overwrite guard**
v7 only overwrote a stored project's URL when the seed entry supplied a non-empty one, protecting any user-edited URL from being blanked by a bare seed row. Current dropped that guard for `url` specifically (paired with seed rows that now intentionally ship `url:''` to retire dead links) — a one-time cleanup that trades away a general safety property: any future seed row shipped with a blank URL will now silently wipe a real one on every load. **Decide:** keep current's looser behavior, or restore v7's guard and treat URL retirement as an explicit versioned migration instead.

**G. Voice engine architecture: cascade vs. single call** *(the flip side of Section 2's local-TTS cluster)*
v7: a 5-tier fallback cascade (local admin engine → Kokoro/Chatterbox → HuggingFace → Edge → browser SpeechSynthesis), each independently try/caught. Current: calls Azure directly with **no** try/catch around it in `vsSpeakRaw`, and every fallback tier is explicitly stubbed to return `null`/`false`. This directly contradicts a still-standing instruction in `G:\VPS\CLAUDE.md` ("Keep browser SpeechSynthesis as fallback, but server-side Azure/Edge voices should be the polished path") — today, an Azure outage, an expired session, or a signed-out visitor produces **total, silent voice failure**. **Decide:** is that trade-off (simplicity/consistent quality vs. resilience) acceptable, or does the rebuild need at minimum a browser-SpeechSynthesis last-resort tier? This is the single most consequential open decision in the whole plan — see Section 4.

**H. `/voice` slash-command keyword coverage for the 14-locale catalog**
The Voice Studio picker UI was correctly rebuilt to group by all 14 English locales, but the `/voice british`/`/voice american` slash commands still only filter `en-GB`/`en-US`, silently ignoring the other 12 locales (AU/CA/IE/IN/NZ/SG/ZA/HK/KE/NG/PH/TZ) now in the catalog. Lower stakes than the others here. **Decide:** extend the keyword set (e.g. `/voice australian`, `/voice indian`) to match the full catalog, or leave the two original shortcuts as-is.

---

### 4. Scope reality check: personality.js and voice.js

Both were called out as unusually large comparisons. They mean two different things.

**personality.js: not evidence of unlaunched work.** Current is a strict superset of v7 in nearly every respect checked. The actual persona prompt logic is *complete* in current and provably *broken* (unbalanced braces) in v7's given fragment. The humor/adult-humor/long-form modifiers, the undo-capable memory clear (`_clearMemory`/`_undoClearMemory`, a real safety fix over v7's no-recovery delete), the hardened project auto-discovery (URL sanitization, draft-by-default, same-origin-only health rechecks), and the ARIA-annotated picker grids are all live, correct, and already better than v7 today. The only thing genuinely *removed* is the multi-engine local TTS code (Section 2's cluster) — a deliberate, documented architecture trade, not an oversight. The one net-new item (the 9-mode "Mode-Aware UI" router) is real work, but it's a message-routing concern, not a personality feature, that only appears here because of the single file's layout. **Bottom line: there is no hidden personality-system backlog. The size of this diff reflects thorough forensic comparison, not hidden scope.**

**voice.js: real depth in one dimension, a real regression in another — not simply "equivalent."** Current fully delivers the flagship deliverable this repo's own `CLAUDE.md` prioritized (P0 item 5: port the 99+ English Azure voice catalog from the kilocode-Azure2 reference) — verified field-for-field, 99 `en-*` entries across 14 locales. That is genuine, substantial, **already-shipped** work, not a gap. Layered on top of it: an authenticated Azure TTS proxy, a wholly new real-time "Moshi" voice mode, and a full accessibility retrofit — all live in production today. But in the same breath, current **deleted every fallback tier** v7 had and now calls Azure with no safety net at all, which directly contradicts a still-standing instruction in this repo's own `CLAUDE.md`. **Bottom line: nothing here is unlaunched — everything found in this diff, on both the catalog side and the fallback-removal side, is already live in current production. But the fallback removal is a genuine, currently-unaddressed gap against the team's own stated requirements, and the new build should not silently inherit it — see Decision G above.**

Neither file represents a parallel, unshipped build waiting to be merged in. Every `onlyInCurrent` item in both areas is, by definition of what "current" means in this comparison, already running in production today.

---

### 5. Overall estimate

**This is "mostly port forward," not "near-rewrite guided by v7's structure" — and specifically, the direction of the port is current → new modules shaped like v7, not v7 → current.**

The evidence for this is not a hedge, it's a pattern that repeats identically across all 12 independent area comparisons:

1. **`onlyInV7` is empty in 8 of the 12 areas**, and in the 4 where it isn't, the total is 7 items — mostly one deliberate architectural trade (drop self-hosted TTS for a cloud-only voice stack) rather than accidental loss of scattered features.
2. **Not one of the ~61 `evolvedDifferently` comparisons favored v7 outright.** ~51 explicitly favored current (bug fixes, security hardening — auth headers on DB queries, a global 401 guard, auth-gated TTS; race-condition fixes — BrainState; accessibility work across nearly every interactive surface); only 10 were genuinely unclear, and all 10 are product/config calls, not evidence that current lacks capability.
3. **Current added substantial new capability in every single one of the 12 areas** beyond what v7 had — a real workspace-layout engine, a JWT+fetch-guard auth layer, a server-synced Projects/game-catalog system with a browsable carousel, a Memory pane, BrainState health SSOT, human-in-the-loop approval gating, a capability-broker tool model, a 99-voice Azure catalog, and a real-time Moshi voice mode. This is not lateral drift from v7 — it's five months of continuous, compounding growth on top of it.
4. Every one of the 12 areas' own conclusions used language to this effect: "strict subset," "nothing to revive," "no genuine lost work," "port all of it forward with confidence."

The actual work in rebuilding this as a clean modular codebase is therefore almost entirely **mechanical extraction and consolidation**, not new feature engineering:
- Re-split ~13,000 lines of single-file production HTML/CSS/JS back into the module boundaries v7 already drew (agents/auth/chat/config/panels/personality/state/status/tools/canvas/voice/app-init), but populate each module from **current's** logic.
- Fix the small, already-identified set of cross-cutting messes: `AGENT_COLORS` duplicated in 5+ places, dead `.agent-select-btn` lookup code, `/voice` handled on two independent code paths, three uncoordinated `/api/health` pollers that should share one fetch, stale header comments ("POST /api/chat" where the code actually calls `/api/stream`).
- Resolve the bounded list of decisions in Sections 2 and 3 — roughly 7 revive-or-leave-behind calls (which collapse to about 3 real questions once the TTS-fallback cluster is treated as one) and 7 product decisions.

**The one place this verdict needs an asterisk** is voice resilience (Decision G): reintroducing a working non-Azure fallback tier, if the team decides they want one, is genuine new build work, not copy-paste from either side — v7's cascade can inform the *shape* of a solution but its specific engines (Kokoro/Chatterbox/HuggingFace) may or may not be worth resurrecting. That is a real, bounded pocket of net-new engineering inside an otherwise low-risk extraction project — it doesn't change the overall verdict, but it's the one item on this entire plan that isn't just "port current forward."

---

## Area-by-Area Detail

Each subsection lists: **must port forward** (`onlyInCurrent` — concrete porting tasks, with
file:line evidence), **flagged for human call** (`onlyInV7` — revive-or-leave-behind; this document
does not recommend either way beyond what the comparison agent itself said), and **needs a product
decision** (`evolvedDifferently` items marked `unclear-needs-human-call`). Where an area had many
`evolvedDifferently` findings that were clearly resolved in favor of one side, only a representative
sample is included rather than every item — see the full synthesis above and the raw comparison
data for the complete list. Personality and voice are given in full detail (every finding in every
category), per their unusually large/high-stakes scope in the original task.

### Agents — role indicator pills (Supervisor/Coder/QA/Asset)

**Must port forward (6):**
1. **Interactive pill click = manual agent-routing override** (`setAgent()`/`pillClick()` +
   `.pill.is-selected`) — `vps/daveai-ui-v6.html:4178-4195`, CSS at `:61-64`. Clicking a pill now
   forces the next chat message to that agent instead of auto-routing; v7's pills were passive
   telemetry only (zero occurrences of `pillClick`/`setAgent`/`activeAgent`/`is-selected` anywhere
   in `daveai-v7/js/agents.js` or `agents.css`).
2. **Governance "needs proof" bulk agent state** — `vps/daveai-ui-v6.html:4428-4434` (paired with
   the approval-denial flow at `:4340-4346`). On a blocked/denied/timed-out approval event, all four
   pills reset to `state:'idle', task:'needs proof'` and the status bar shows "Blocked: proof
   required." v7's only bulk-reset block is the success path (`daveai-v7/js/agents.js:87`).
3. **Per-agent model name in UI, backed by real backend writes** — `vps/daveai-ui-v6.html:4026-4029,
   4040-4041` (flyout + Admin panel); `vps/patches/daveai-production-runtime-20260731/brain_llm.py:
   324-332` (`agent_set(...)`). v7 captures `.model` in `agentStates` but never renders it anywhere.
4. **Narrator-first routing gate** (`AGENT_TRIGGERS` + `shouldUseAgentPipeline()`) —
   `vps/daveai-ui-v6.html:4099-4108`. Purely conversational messages now bypass the 4-agent pipeline
   entirely; no trace of a narrator concept anywhere in v7's `agents.js`.
5. **Per-agent voice assignment** (defaults, persistence, populated selects, agent-keyed narration)
   — `vps/daveai-ui-v6.html:7669, 8234-8236, 8692-8695`. *Caveat:* v7's `agents.css` already ships
   the matching `.vs-agent-row` visual spec, and v7's own tree has a separate ~106KB `voice.js` not
   included in this comparison's Side A — this most likely already existed there in March rather
   than being new since. Verify before treating as net-new.
6. **Tools-to-agent attribution catalog** (~100+ tools tagged with owning agent, heuristic
   classifier, role-filter buttons, role-colored badges) — `vps/daveai-ui-v6.html:3183-3306
   (array), 3324-3328 (classifier), 1595-1601 (filter buttons)`. Same caveat as above: v7's own
   separate ~26KB `tools.js` plausibly already had an equivalent scheme.

**Flagged for human call:** none — `onlyInV7` is empty for this area.

**Needs a product decision:** none — all 4 `evolvedDifferently` findings resolved to "current."
Representative examples: the `BrainState` single-source-of-truth status derivation replacing an
inline `ok ? green : red` computation (a documented race-condition fix), and a 3-tier responsive
pill-collapse cascade plus a new JS-driven `data-device-mode` axis that is a strict superset of
v7's single breakpoint.

**Also worth noting** (from the comparison agent's own recommendation, not a port item): the
backend already computes a 0-100 progress value per agent on every `agent_set(...)` call in
`brain_llm.py`, but neither v7 nor current renders it anywhere in the UI — a genuine improvement
opportunity for the new build, not something to port from either side.

### App-init

**Must port forward (6):**
1. **JWT-claims session validation** (`getTokenClaims()`/`isAuthenticated()`) —
   `vps/daveai-ui-v6.html:2378-2395`. v7 only ever compares a locally-stored timestamp
   (`isTokenExpired()`) and never decodes the token itself.
2. **Global fetch() 401 guard** (`installAuthFailureFetchGuard()` + `handleAuthFailure()`) —
   `:2396-2421`. Zero matches anywhere in v7 for a `window.fetch` monkey-patch of any kind.
3. **`_setCurrentUser()` normalizer + `window` mirror + `_isCurrentUserAdmin()`** — `:2427-2438`.
   v7 assigns `_currentUser` directly at two call sites with no normalization and no shared helper.
4. **Boot-time accessibility auto-labeling pass** (`button[title]:not([aria-label])` → mirrors
   `aria-label`, run on `DOMContentLoaded`) — `:10512-10515`. Run this first in any new init
   sequence. Zero matches anywhere in v7.
5. **`initRightPanelResize()`** — persisted, user-draggable right-panel width; called at `:10533`.
   The function name does not exist anywhere in the v7 tree under any spelling.
6. **`setFpTab()` ARIA attributes** (`aria-selected`/`tabindex` on tab buttons) — `:3036-3041`.

**Flagged for human call (1):**
- **Post-sign-in welcome-video replay with TTS ducking** — `daveai-v7/js/auth.js:94` (empty-body
  stub) continued in `daveai-v7/js/state.js:32-58`: `vsStopAudio()`/`_vsSpeechQueue.length = 0` then
  `playIntro()` after *every* successful sign-in. Current plays the intro once, pre-auth, on page
  load, and never replays it on sign-in (confirmed absent from `_completeSignIn`,
  `vps/daveai-ui-v6.html:2545-2567`). A mid-session re-auth (e.g. forced by the 60s token-expiry
  watchdog) no longer gets the welcome-video moment. The comparison agent's own framing: this looks
  like a deliberate side effect of flipping the onboarding order rather than an accidental loss, but
  is a real behavior gap worth a call for the re-auth/kiosk case.

**Needs a product decision (1, shared with Auth and State — one decision, three facets):**
- **Video-first vs. auth-first entry funnel.** v7: show sign-in immediately; the intro video plays
  only after a successful login (`daveai-v7/js/panels.js:610-611` comment: *"Show auth/login FIRST
  (intro plays AFTER successful login)"*). Current: play the intro video once on page load, before
  auth, and never replay it on sign-in (`vps/daveai-ui-v6.html:10580-10592`, comment: *"Play intro
  video FIRST on page load (login shows after)"*). Current is more defensively wired —
  `playIntro()` now guarantees a fallback call to `_showAuthIfNeeded()` on every exit path (intro
  pref off, missing manifest, missing DOM nodes, thrown error), so a broken/disabled intro can never
  strand a user — but the two designs serve different goals (marketing "wow" moment vs. never
  wasting an unauthenticated visitor's time). Decide which ordering the new build should use, and
  separately, whether the post-sign-in replay (flagged above) should come back for forced re-auth.

**Representative clear-cut items** (of 6 `evolvedDifferently`, 5 resolved "current"):
- **Workspace-layout engine**: v7's `layouts` array (`daveai-v7/js/canvas.js:4-11`) is a
  non-functional 12-entry color-swatch name picker with no `applyWorkspaceLayout` anywhere in the
  tree. Current's version (`vps/daveai-ui-v6.html:2608-2805`) is a full schema (rail/activity/chat/
  density/status) that mutates ~11 CSS custom properties and DOM classes, with stable-id
  persistence and saved-panel-width restore. Called out as "the single largest functional gap in
  the app-init area" — port the whole engine as one unit, not piecemeal.
- **Main bootstrap handler**: v7's `app.js` registers `DOMContentLoaded` twice, nested — as
  literally given, session-restore, the token watchdog, and `renderHistory` are dead code in v7.
  Current's single top-level handler (`:10509-10537`) is the safe reference shape. *Caveat*: most of
  what v7's inner handler would have called does exist somewhere in v7, just scattered as orphaned,
  uncalled fragments across `canvas.js`/`panels.js`/`status.js`/`chat.js`/`state.js` — treat the
  "dead code" finding as reported-as-given, not certainty about what shipped in March.
- **`setFpTab()` content dispatch**: current actually calls each tab's render function
  (`renderTools`/`renderProjects`/`loadPagesPanel`/`_renderDbPanel`/`_renderSkillsPanel`) on switch;
  v7's intact copy of this same function only ever toggles visibility.

### Auth

**Must port forward (5):**
1. **JWT-claims-based session validity** (`getTokenClaims`+`isAuthenticated`), used at 20+ call
   sites — `vps/daveai-ui-v6.html:2378-2395`, called at `:3057, 3683, 3753, 3876, 3952, 4052, 4205,
   7918, 8550, 10225, 10517, 10525, 10638` and others.
2. **Global fetch-response 401 interceptor** (`installAuthFailureFetchGuard`/`handleAuthFailure`) —
   `:2396-2421`.
3. **Hard auth gate at the top of `think()`**, before input-clear/`/api/stream` — `:4197-4212`.
   Matches the documented production repair for "stale Thinking... state for unauthenticated /
   malformed-token chat attempts."
4. **Accessible sign-in/sign-up tab pattern** (`role="tablist"`/`role="tab"`/`aria-selected`/
   `aria-controls`/`tabindex` + `activateOnKeyboard()`) — `:1203-1208, 2336-2342, 2451-2456`; plus
   `aria-label` on admin user-management buttons (`:5178-5180`).
5. **`_isCurrentUserAdmin()` helper** — `:2436-2438`, replacing 5+ inline
   `_currentUser?.role === 'admin'` copies (`daveai-v7/js/state.js:98, 105, 128, 155, 270`).

**Flagged for human call:** none — `onlyInV7` is empty for this area.

**Needs a product decision (1):** the same video-first-vs-auth-first ordering call as App-init/State
above (`daveai-v7/js/panels.js:610-611` vs. `vps/daveai-ui-v6.html:10580-10592`) — cross-referenced
here, not a separate decision.

**Representative clear-cut items** (of 4 `evolvedDifferently`, 3 resolved "current"):
- **`_currentUser` normalization**: v7 never assigns `.name` anywhere on `_currentUser`, yet its own
  `_dbSyncUser()` guards on exactly that field (`if (!_currentUser || !_currentUser.name) return;`)
  — making Postgres user-sync effectively dead for every real signed-in user in v7. Current's
  `_setCurrentUser()` aliases `.name`/`.id` from `.display_name`/`.user_id` on both the sign-in and
  restore paths, which is what makes the byte-identical guard actually pass in production.
- **`setAuthMode()`** gained `aria-selected`/`tabindex` tab bookkeeping with no functional
  regression versus v7's plain class-toggle.
- The **`_showAuthIfNeeded()`/watchdog guard condition** swapped from a raw `isTokenExpired()`
  timestamp check to the JWT-aware `isAuthenticated()` — a malformed/tampered token that hasn't hit
  the 24h mark yet no longer reads as "still signed in."

**Also flagged:** neither version has an `aria-live` region on `#am-err` or `for`/`id` label
associations on the auth modal — a gap shared by both sides, not a regression, but worth fixing
while this code is being touched given this repo's active accessibility pass.

### Canvas-games

**Must port forward (5):**
1. **Browsable multi-game carousel** (`loadCarouselGames()`/`renderCarousel()`/
   `bindCarouselActionButtons`/`selectCarouselGame`/`launchCarouselGame`/`carouselPrev`/`Next`) —
   `vps/daveai-ui-v6.html:6113-6179`. v7 could only ever show one hardcoded demo game; v7's
   `canvas.css` (919 lines, read in full) has zero `.game-card`/`.carousel-dot`/`#game-carousel`
   rules.
2. **Server-hosted project catalog merge** (`daveai-project-catalog.json`) —
   `SERVER_PROJECT_CATALOG_URL` at `:9121`, `loadServerProjectCatalog()` at `:9298-9315`,
   `normalizeProjectRecord`/`mergeProjects` at `:9124-9218`. Feeds the carousel with 20+ real game
   entries; v7's canvas.js only calls bare `getProjects()`/`saveProjects()`/`seedProjects()` against
   localStorage with no remote-catalog concept at all.
3. **Game ↔ PostgreSQL postMessage bridge** (hi-scores/leaderboard/map-progress) —
   `:6027-6059`. No `window.addEventListener('message', ...)` listener anywhere in v7's `canvas.js`.
4. **Cross-origin "launch card" fallback** for auth-walled catalog entries
   (`shouldUseLaunchCard`/`projectLaunchCardUrl`) — `:9317-9336`, routes through
   `/daveai-launch.html` instead of a broken iframe. v7's `setPreviewUrl()` unconditionally does
   `frame.src = url` with no origin check.
5. **Resume-last-active-project + registry export** (`setLastActiveProject`/`findLastActiveProject`/
   `resumeLastProject`/`downloadProjectRegistry`) — `:9239-9296`. Not games-exclusive, but applies
   directly since a game is just a project with `cat:'games'`.

**Flagged for human call:** none — `onlyInV7` is empty for this area.

**Needs a product decision:** none — this area's single `evolvedDifferently` finding resolved to
"current."

**The one evolved finding** (for completeness, since the area has so few): the game-launch handler
itself. v7's given copy (mislabeled `startPolling()`, `daveai-v7/js/canvas.js:203-214`) references
an undefined `url` variable — a corrupted/mis-merged extraction, not viable code (the same pattern
recurs in v7's `_syncDemoEditor()`, whose second half is verbatim the body of current's
`loadProject()`). Current's `demoPlay()` (`:6257-6284`) is the properly-scoped, functioning version:
reads `url`/`pid` from the hero's dataset, hides the hero first, made the voice greeting opt-in via
`_vsState.narration.gameLaunch` instead of always-on, and wraps the TTS call in try/catch. Rebuild
the launch handler from current's `demoPlay()`/`loadProject()`, not from v7's copies.

**Also flagged:** verify carousel/demo-hero visual styling against the un-reviewed
`/assets/daveai-v6.css`, and decide whether the carousel should surface the catalog's richer status
vocabulary (auth/needs-proof/needs-fix/provider-ready) instead of the simple Live/Draft badge it
still inherits unchanged from v7.

### Chat

**Must port forward (5):**
1. **Sign-in gate before send** — `vps/daveai-ui-v6.html:4197-4212` (same mechanism as Auth).
2. **Human-in-the-loop approval workflow** (`completion_gate`/`artifact_contract.preview_url`
   handling; `approval_required|granted|denied|timeout` SSE event types;
   `renderDaveAIApproval`/`resolveDaveAIApproval`/`updateDaveAIApproval` POSTing to
   `/api/approvals/:id`) — `:4319-4346, 4506-4578`. No trace of "approval"/"completion_gate"/
   "artifact_contract" anywhere in v7's `chat.js`/`chat.css`.
3. **UI/session context + personality prompt on every request** (`getDaveAIUiContext()` —
   page_url/preview_url/project_id/device_mode/panel/app_mode — folded into `system_prompt`/
   `session_id`/`project_id`/`ui_context` in the SSE payload) — `:4110-4133, 4271`.
4. **Server-side chat persistence, analytics, and the Memory pane** (`_addToMemory`, `_dbSaveChat`,
   `_dbTrack('chat_send', ...)`) — `:4229, 4449-4450`, Memory pane markup at `:2297-2310`. v7's only
   persistence is a client-local `localStorage` history array.
5. **Manual agent-pin UI** (`setAgent(role)`/`pillClick(short)`) — `:4178-4195` (identical to the
   Agents-area item; implement once).

**Flagged for human call:** none — `onlyInV7` is empty for this area.

**Needs a product decision (1):**
- **Copy for "chat completely unreachable."** v7: specific and actionable —
  *"⚠ Cloud API unavailable. Enable **Local LLM** in Settings → Admin → Local LLM to chat offline."*
  (`daveai-v7/js/chat.js:59`). Current: generic — *"⚠ Chat temporarily unavailable. Please try
  again."* (`vps/daveai-ui-v6.html:4497`). Current's surrounding mechanism (exponential-backoff
  retry, then a real second `/api/stream` non-stream attempt) is strictly better; only the final
  copy regressed, and the admin-gated Local LLM path it used to point to is still tried first.
  Decide: restore actionable copy, or keep it generic.

**Representative clear-cut items** (of 9 `evolvedDifferently`, 8 resolved "current"):
- **SSE chunk-to-frame parsing**: v7 parses each decoded network chunk independently line-by-line,
  so a `data: {...}` JSON payload split across two reads throws inside `catch(e){}` and is silently
  dropped. Current buffers (`sseBuffer`) and splits on blank lines before parsing — the standard fix
  for exactly that failure mode.
- **Assistant-text sanitization** (`cleanAssistantForUser()`/`isDenseAgentTraceLine()`,
  `:4135-4176`, strips `<think>` blocks and THOUGHT/ACTION/OBSERVATION lines): v7 has no
  sanitization step at all. Corroborated server-side by `brain_llm.py`'s `_ReActStreamFilter`,
  whose own docstring dates it "Wave 2 ReAct leak fix, 2026-05-25" — two months after the v7
  snapshot.
- **Activity feed dual-mode pipeline** (`setActMode`/`renderActivityCenter`/`friendlyMsg`/
  `timeAgo`): current *completes* something v7 only started — identical variable/function names on
  both sides, but v7's file cuts off mid-declaration before ever defining them. Flagged as a
  low-risk, high-confidence port.

**Also flagged:** `/voice` is now handled on two independent code paths (`think()`'s inline check
always wins since it returns first, ahead of the general slash-command dispatcher) — worth
collapsing into one path when re-modularized.

### Config

*Scope: agent UI constants (colors/IDs/names/models), agent-pipeline routing flags, and
personality-prompt configuration.*

**Must port forward (3 features + 1 cleanup item):**
1. **`CHAT_ONLY_DIRECTIVE` negation regex** — `vps/daveai-ui-v6.html:4102, 4106`. Stops "don't build
   X, just answer" style messages from being misrouted into the heavy pipeline; v7's routing test
   was a single `AGENT_TRIGGERS.test(msg)` clause with no negation handling — a real bug fix, not
   just a style change.
2. **Memory-context personalization** (`_DEFAULT_PERSONALITY.memoryEnabled`/`memorySize`, injected
   into `buildPersonalityPrompt()`) — `:9570-9584, 9656-9660`. *Caveat*: may already exist in v7's
   separate, unreviewed `personality.js` — verify before treating as net-new.
3. **Local-LLM / auto-refresh config keys** (`_LLM_KEY`/`_REFRESH_KEY`) — `:9572-9573`. No v7 config
   module claims them; give them an explicit home in the new build.
4. **Cleanup, not a port**: delete the config drift that accumulated with no module boundary to
   prevent it — `SB_AGENT_COL`, two ad-hoc `roleCol` literals, an inline `agentColors`, and the
   inverse `shortByRole` map are all re-declarations of the one canonical `AGENT_COLORS`/
   `AGENT_NAMES` pair that v7 defines exactly once. Have every call site import the single source.

**Flagged for human call:** none — `onlyInV7` is empty for this area.

**Needs a product decision:** none — both `evolvedDifferently` findings resolved to "current": the
active-agent pill's `aria-pressed`/`is-selected` state now survives the 5s polling refresh (real
a11y work, though it leaves one piece of dead code inherited unchanged from v7 — `setAgent()`'s
first two lines still target a `.agent-select-btn`/`as-<role>` lookup that matches nothing in
current's HTML, safe to drop rather than port); and `shouldUseAgentPipeline()`'s encapsulation +
`CHAT_ONLY_DIRECTIVE` guard is a strict behavioral superset of v7's inline `_needsAgent` expression.

### Panels

*Scope: right-panel Activity Feed / Memory / History, plus the surrounding panels.js/panels.css
chrome (fly-out auto-hide timer, Ctrl+K command palette, keyboard-shortcuts overlay, build
timeline, real-time stats, clock, voice mic).*

**Must port forward (6):**
1. **Memory tab/pane** — a third right-panel view (`rp-memory-pane`/`rpm-list`), backend-driven,
   skeleton/empty/error+retry states, location badges (vps/local/local-private/git), SSE-triggered
   refresh (`_memoryHandleSse`) — `vps/daveai-ui-v6.html:2297-2310, 12693-12909`. Zero trace of
   "memory" or an "rpm-" prefix anywhere in v7's `panels.js`/`panels.css`.
2. **History pane content logic** (`chatHistory` + localStorage persistence, capped-at-50 render
   with click-to-replay, live search with highlighting, Markdown export, clipboard copy with
   `execCommand` fallback) — `:4899-4988`. *Fix while porting*: standardize on the absolute-index
   `replayHistoryAbs()` approach used by the filtered list — the default list view's
   `replayHistory(idx)` re-slices `chatHistory.slice(-50)` fresh each call, so a stale button can
   point at the wrong message once new turns push the window.
3. **Persistent raw-activity buffer + redraw on mode switch** (`rawActivities`, capped 300;
   `renderCoderActivity()`) — `:4753, 4777-4795`.
4. **Right-panel drag-to-resize** (`#rp-resizer`, `role="separator"`, keyboard-operable, min/max
   clamped; `setRightPanelWidth(width, persist)` writing a `--right-panel-w` CSS variable) —
   `:2238-2240, 5300-5307`. v7's panel was a fixed 268px with only an open/closed toggle.
5. **BrainState single-source-of-truth health poller** (5s interval, drives every status indicator
   AND writes activity-feed entries on state transitions) — `:4803-4822, 4883-4891` (same mechanism
   as Status; implement once).
6. **Second "Phase A1" command palette** (`openCommandPalette`/`paletteInput`/`paletteKey`), layered
   in front of the original Ctrl+K palette, which now delegates to it first — `:2319-2329,
   ~12238-12280`. Consider merging into one implementation rather than carrying forward the
   legacy-plus-delegate arrangement.

**Flagged for human call (1):**
- **Semantic CSS classes for activity-feed and history rows** (`.ai`/`.ai-hd`/`.ai-dot`/`.ai-name`/
  `.ai-ts`/`.ai-txt`/`.ai-cm`, `.hist-item`/`.hist-prompt`/`.hist-meta`) —
  `daveai-v7/css/panels.css:531-575, 613-633`. Current hand-rolls the same visuals via inline
  `style=` strings in JS template literals instead — nothing is visually lost, but the maintainable,
  class-based pattern is gone. *Caveat the comparison agent raised*: current's real external
  stylesheet (`/assets/daveai-v6.css`) was not reviewed for this area, so double-check these classes
  aren't already there unused before assuming they're gone.

**Needs a product decision (2):**
- **"Uptime" metric semantics.** v7: a quantified but mathematically thin 30-day uptime %
  (`daveai-v7/js/panels.js:312-322`) that resets to 0 on every process restart/deploy, so it isn't a
  real rolling SLA number. Current: an honest binary Online/Unknown with no trend data
  (`vps/daveai-ui-v6.html:3796-3803`). Decide whether a real uptime metric — backed by actual
  monitoring/history, not a single process's `uptime_seconds` — is worth building for v2.
- **Voice-input (mic) architecture.** v7: client-side WebSpeech API — free, instant, live interim
  captions, Chrome/Edge-only, no auth required — plus a MediaRecorder fallback
  (`daveai-v7/js/panels.js:441-453, 515-542`). Current: authenticated Azure server-side
  transcription (`vps/daveai-ui-v6.html:5444-5450`, `_hasWebSpeech = false`). This is a deliberate
  fork, not a bug on either side; the comparison agent flagged it as only lightly traced in this
  review and recommended a dedicated pass (cross-referenced under Voice and Status too).

**Representative clear-cut items** (of 8 `evolvedDifferently`, 6 resolved "current"):
- **Activity-feed dual-mode pipeline**: v7's `addRichActivity()` cuts off mid-body with no
  `setActMode`/`renderActivityCenter` defined anywhere in the file; current has the complete,
  working implementation. *Caveat*: v7's truncation may be an extraction artifact rather than proof
  March genuinely lacked this — check pre-split git history if certainty matters.
- **Right-panel tab semantics** gained a third "Memory" tab plus real ARIA roles/`aria-selected`/
  roving tabindex, replacing v7's plain class-toggle tabs.
- **Real-time clock**: current dropped a `worldtimeapi.org` network round-trip (with a 3s timeout
  compensating for its own latency/failure) in favor of the browser's own `Intl` timezone — removes
  a third-party dependency and a minor privacy leak (shipping the visitor's IP externally just to
  learn a timezone the browser already knows) with no real accuracy loss for most users.

**Also flagged:** the admin dashboard (`_loadAdminDashboard`, `_fmtBytes`, `_fmtUptime`) could not
be reconciled at all — v7's copy is truncated to a bare function signature with no body. Treat as
unverified/out of scope, not as "safe to skip."

### Personality (full detail)

*Scope: DaveAI "AI Personality & Memory Brain" system — style/humor/memory config, local-LLM+voice
integration, intro video, and several UI-customization subsystems bundled into the same v7 file
(`daveai-v7/js/personality.js`, 1,822 lines).*

**Flagged for human call — 1 item (a 5-sub-feature cluster, decide as one bundle):**
- **Multi-engine self-hosted local TTS voice backends** (AllTalk, Kokoro, Chatterbox,
  LM-Studio-TTS, Custom-TTS) with real, working per-engine API integrations —
  `_VOICE_ENGINE_URLS` mapping each to a localhost port (7851/8880/8003/1234/5000), full fetch
  implementations per engine (e.g. AllTalk's `FormData` POST to `/api/tts-generate`). Confirmed
  **actively neutralized** in current, not just absent: a full-text search finds zero occurrences of
  "alltalk"/"kokoro"/"chatterbox"/"tts-generate" anywhere in the 12,920-line current file;
  `_getLocalLLM()`/`_saveLocalLLM()` hard-override `voiceEngine` to `'none'`, and
  `_localVoiceSpeak()` is stubbed to `return false`. Current instead ships a full "DaveAI Voice
  Studio" panel built on Azure Neural only, telling users "DaveAI voice is Azure Neural only."
  Reads as a deliberate architecture decision (one reliable cloud engine that works on every device,
  vs. requiring the admin's own PC to run extra local software), not an accidental regression — do
  not silently revive without confirming product still wants it. (This is the same underlying
  decision surfaced from the voice-area side below, and in the synthesis's Decision G.)

**Must port forward — 1 item:**
- **"Mode-Aware UI"** — a 9-mode keyword classifier + router (chat/web/build/code/research/
  problem/game/hermes/admin) with per-mode badge color/icon and a 5-minute manual-override window,
  citing an internal spec ("Phase 3 + 5 — spec wave2-handoffs/08"): `classifyMode(msg)` +
  `MODES`/`MODE_ORDER`/`MODE_OVERRIDE_MS`. Verified absent from v7 entirely (zero hits for
  `classifyMode`/`wave2-handoffs`/`MODE_OVERRIDE`/`MODE_LS_KEY`/`const MODES` anywhere in the v7
  tree). **This is called out as the only genuine `onlyInCurrent` item in this area** — and it is a
  message-routing/navigation concern, not a personality feature; it only appears in this file region
  because of the single-file monolith's incidental layout. Give it its own routing module in the
  rebuild, not the personality module.

**`evolvedDifferently` — all 8 items (none marked unclear; all resolved "current"):**
1. **`buildPersonalityPrompt()`** (the actual system-prompt text): v7's given copy is provably
   brace-unbalanced/truncated — the function's own opening brace is never closed, and the humor/
   adultHumor/longForm modifier branches are entirely absent even though the config schema and the
   settings-UI sliders/checkboxes for all three already existed and synced in v7. Current is
   complete: `PERSONALITY_PROMPTS` (witty/professional/comedian/storyteller/poet/flirty/custom) plus
   explicit humor-level, adult-humor, and long-form modifier strings. *Caveat*: v7's truncation may
   mean some of this was lost in extraction rather than never built in March.
2. **Memory-clear safety**: v7's `_clearMemory()` permanently deletes on `confirm()` accept with
   zero recovery path. Current snapshots the prior memory into `_MEMORY_BACKUP_KEY` first and ships
   a real `_undoClearMemory()` plus an "Undo Clear" button (`stg-memory-undo`). The underlying
   fact-extraction/memory-store code (`_getMemoryStore`, `_addToMemory`, `_getMemoryContext`) is
   otherwise byte-for-byte identical between the two versions.
3. **Chat-send SSE payload/retry policy**: current enriches the payload with `session_id`/
   `project_id`/`project_name`/`ui_context` (unambiguous improvement) but also changed
   `_SSE_MAX_RETRIES` from 3 exponential-backoff retries (up to ~7s wait) to 1 fast retry
   (documented as "cloud-primary, fail fast to fallback"). A genuine trade-off (less patience with
   transient blips vs. much less dead-air for the user) a human could reasonably weigh differently —
   the comparison agent leans "current" only because the change is intentional, documented, and
   pairs with a working fallback path.
4. **`_refreshProjects()`** (auto-discovery of new game folders): current adds three concrete
   hardenings — strict `[A-Za-z0-9_-]+` folder-name validation instead of accepting raw HTML
   directory-listing text as-is; auto-discovered games default to `'draft'` instead of instantly
   `'live'`, avoiding surprise-publishing unverified content; and the live-status re-check is
   restricted to same-origin URLs already `'live'` (v7 HEAD-checked every non-archived URL including
   cross-origin ones, so a CORS failure — not an actual outage — could wrongly flip a genuinely-live
   external project to draft).
5. **Accessibility semantics on picker grids** (icon-theme packs, waveform color swatches, waveform-
   type cards): v7's are mouse-only `<div>`s with no keyboard path. Current adds `role="option"`/
   `role="radio"`, `tabindex`, `aria-selected`/`aria-checked`/`aria-disabled`/`aria-label`, and a
   shared `activateOnKeyboard()` handler — consistent with this repo's active accessibility
   initiative.
6. **`amtScreenshot()`** (App Mode toolbar's "capture the preview" action): v7's approach
   (`<canvas>.drawImage()` on the preview iframe) is fundamentally broken for any cross-origin
   preview iframe by browser security policy — v7's own error message ("Screenshot failed —
   cross-origin iframe") admits this likely never worked for the real daveai.tech use case. Current
   abandons client-side capture entirely and instead pre-fills the chat composer with a
   natural-language screenshot request for the agent pipeline to fulfill server-side.
7. **`_amRestorePos()`** (App Mode floating toolbar position restore): v7 references an undefined
   variable `b` (should be `tb`, the element it just looked up) — a `ReferenceError` on every call
   that, because `_amApply()` invokes it unguarded in sequence, would also silently abort the two
   functions after it (`_amRestoreChatPos()`, `_amApplyTbOpacity()`) on every App Mode toggle/reload.
   Current fixes the typo outright — a clear bug fix.
8. **`playIntro()`** auth-overlay guarantee: v7 simply `return`s if the intro pref is `'off'`, the
   manifest/pick fails, or the overlay elements are missing — meaning the sign-in overlay might
   never appear, potentially stranding an unauthenticated visitor on a blank/stuck screen. Current
   calls `_showAuthIfNeeded()` on every one of those early-exit paths.

**Bottom line for this area** (from the synthesis's own scope-reality-check section): current is a
strict superset of v7 in nearly every respect checked — **there is no hidden personality-system
backlog**; the size of this diff reflects thorough forensic comparison, not hidden scope. One
correction to the original task's framing, from the comparison agent: "Alice" (the narrator persona)
is *not* a current-only addition — it already existed in the March codebase, just in v7's sibling
files (`voice.js`'s British-female preset mapped to `en-GB-MaisieNeural`; `chat.js`'s identical
"Narrator-first routing... (Alice)" comment), not in `personality.js`. Keep Alice/narrator-routing
in chat/voice modules in the new split, not personality — it only shows up here because this file
happened to reference `_routedAgent` in passing.

### State

*Scope: session + data layer.*

**Must port forward (6):**
1. **Dedicated ambient UI-interaction state block** (`curTgt`, `micOn`, `rpOpen`, `ppOpen`,
   `selLayout`, `curPanel`, `curFpTab`, `curRpTab`, `curDeviceMode`, `curToolRole`, `toolSearch`,
   `sessionHistory`, `micRecognition`, `activeToolName`) — `vps/daveai-ui-v6.html:2344-2349`. Never
   persisted to storage; keep as its own never-persisted module.
2. **JWT token layer + fetch guard** (same mechanism as Auth/App-init) — `:2357-2377, 2396-2421`.
   *Lower-confidence caveat*: v7's `state.js` calls `clearToken()` without ever defining it — it
   likely lived in a v7 `auth.js` not covered by this review, so treat this specific item with more
   caution than the rest of this list.
3. **Projects: server-catalog + server-DB merge/reconciliation** (`SERVER_PROJECT_CATALOG_URL`/
   `PROJECTS_LOCAL_KEY`/`LAST_PROJECT_KEY`/`PROJECT_CATALOG_HOST_STATUS`,
   `normalizeProjectRecord`/`mergeProjects`, `loadServerUserProjects`,
   `setLastActiveProject`/`findLastActiveProject`/`resumeLastProject`, `loadServerProjectCatalog`,
   `shouldUseLaunchCard`/`projectLaunchCardUrl`, `syncRuntimeProject`) — `:9121-9470`. v7's Projects
   was a flat localStorage array with a 5-item hardcoded seed — same system as the Canvas-games
   items; one Projects module should serve both areas.
4. **Edit Profile modal** (`_renderProfileContent()`/`_saveProfile()`, PATCHes
   `/api/db/users/:id`) — `:10380-10453`.
5. **Always-on dashboard metrics poll** (`_refreshDashboardCards()`, 30s interval, every visitor,
   distinct from the admin-only VPS dashboard) — `:10760-10782`.
6. **Expanded project seed catalog** (9 vs. 5 entries) plus a defensive URL-cleanup pass repairing
   malformed/dead-link seed URLs on load — `:9339-9375` (the guard-condition decision below lives in
   this same code).

**Flagged for human call:** none — `onlyInV7` is empty for this area, though `state.js` itself is a
fragment (several functions start or end mid-body).

**Needs a product decision (2):**
- **`seedProjects` URL-overwrite guard.** v7 only overwrote a stored project's URL when the seed
  entry supplied a non-empty one (`daveai-v7/js/state.js:202-206`), protecting any user-edited URL
  from being blanked by a bare seed row. Current dropped the `req.url &&` guard specifically for
  `url` (`vps/daveai-ui-v6.html:9361-9365`), paired with seed rows that now intentionally ship
  `url:''` to retire dead links — a one-time cleanup that trades away a general safety property: any
  future seed row shipped with a blank URL will now silently wipe a real one on every load. Decide:
  keep current's looser behavior, or restore v7's guard and treat URL retirement as an explicit
  versioned migration instead.
- **Sign-in-completion coupling to the intro video** — the State-layer facet of the same
  video-first-vs-auth-first decision from App-init/Auth: the mechanism (`playIntro`/`vsStopAudio`/
  speech-queue reset) is intact and arguably richer in current (adds a device-chooser splash and
  persisted volume/pref), but the trigger moved from "after every successful login" (v7) to "once,
  before auth, on page load" (current) — so a shared/kiosk terminal no longer replays the intro per
  sign-in.

**Representative clear-cut items** (of 7 `evolvedDifferently`, 5 resolved "current"):
- **Postgres `_dbFetch` authentication posture**: v7 sent zero auth header and its own heartbeat
  payload defaults confirm anonymous DB traffic was expected (`username: _currentUser?.name ||
  'anonymous'`) — every `/api/db/*` write was effectively an open POST endpoint. Current requires a
  valid session before any non-analytics DB call and attaches the bearer token to every request.
  *Side effect flagged*: anonymous/guest visitors no longer show up in the heartbeat-driven "Online
  Users" admin panel, since their heartbeat calls now silently no-op.
- **`renderProjects` card markup**: current adds keyboard operability (`role="button"`/`tabindex`/
  `onkeydown`+`aria-label`) and a 10-value status vocabulary via `projectStatusLabel()`, and —
  functionally, not just cosmetically — only shows the delete button for `source === 'server-db' ||
  'local'` records, so a user can no longer accidentally delete a server-catalog-seeded entry that
  was never really theirs to remove.
- The **`_setCurrentUser`/`_isCurrentUserAdmin` migration is only partial**: current still has
  plenty of inline `_currentUser && _currentUser.role === 'admin'` checks (e.g. lines 4237, 6508,
  10801) that never call the new helper — both patterns coexist. Worth finishing the migration
  during the port rather than reintroducing the inline pattern.

**Also flagged:** `daveai_ext_unlocked` is read in both versions but never written by anything in
either file — a permanently unreachable "admin unlocked this for a user" path. Either wire up a real
admin action for it or drop the dead branch when rebuilding.

### Status

**Must port forward (3):**
1. **Auth-aware polling short-circuit** — `updateStatusBar()`, `fetchAgents()`, `checkApiHealth()`
   all check `isAuthenticated()` first and skip authenticated-only endpoints for anonymous visitors,
   showing a "sign in for workspace stats" placeholder — `vps/daveai-ui-v6.html:~3876-4052`. v7
   polled authenticated-only endpoints unconditionally regardless of login state.
2. **Activity-feed logging of real brain connectivity transitions** — `BrainState.observe(...)`
   logs an activity entry only on genuine online/offline flips, skipping connecting/degraded noise
   and the first unknown-to-X transition on load — `:~4882-4891`.
3. **Live tool count fanned out to more surfaces** — beyond v7's two targets: `fp-agent-tools-count`,
   `adm-tools-count`, `adm-tools-summary`, the tool-search placeholder, the sidebar Tools button's
   aria-label, plus `_syncRuntimeTools(td.tools)` — `:~4062-4078`.

**Flagged for human call (1):**
- **Distinct red "error" state from `checkApiHealth`'s own non-exception health failure** (a
  200-but-unhealthy `/api/health` response), separate from the amber used for offline/connecting —
  `daveai-v7/js/status.js:61-70, 80-84`. Current's `BrainState` refactor means `setApiStatus` is now
  a shim that only reacts to `'online'`, so this specific signal path paints nothing today. Reads as
  an intentional trade-off of the Wave-2 refactor (stop secondary pollers from flapping the shared
  indicator), not lost work worth reviving as-is — but decide whether `checkApiHealth`'s failure
  should surface *somewhere* (logged, or fed into BrainState as a corroborating signal) instead of
  being silently swallowed.

**Needs a product decision:** none marked unclear in this area's own findings (both
`evolvedDifferently` items resolved to "current"). The voice-input mic-architecture decision
surfaced under Panels also touches this area's polling design but is filed there.

**The area's key evolved finding** (for completeness): the **BrainState/pollBrain consolidation** is
a documented ("Wave-2 #15") fix for a real 3-way race where `updateStatusBar`/`fetchAgents`/
`checkApiHealth` could each independently paint conflicting online/offline/error text onto the same
3 DOM nodes with no ordering guarantee. Current adds flap-suppression (2 consecutive failures before
flipping to OFFLINE) and a genuine intermediate DEGRADED tier v7 never had, plus a corrected
severity color mapping (offline=red, degraded/connecting=amber, unknown=gray — v7 confusingly gave
offline and connecting the same amber). The synthesis flags the refactor as **incomplete**, not
finished: `pollBrain`/`updateStatusBar`/`checkApiHealth` still each independently fetch
`/api/health` on their own cadence (5s/5s/30s) instead of sharing one fetch, and `updateStatusBar`'s
now-dead `ok` variable was never deleted — both called out as fix-during-port items, not optional
polish.

### Tools

**Must port forward (2):**
1. **Live tool-registry sync from `/api/tools`** (`_runtimeToolMetadata`/`_syncRuntimeTools`
   reconcile the static 113-entry registry against the backend's real manifest on every health
   check) — `vps/daveai-ui-v6.html:3309-3352`, wired at `:4052-4086`. v7's 113-entry `TOOLS` array
   is 100% static with no manifest fetch or runtime mutation of any kind.
2. **Capability-broker-gated slash commands** (`/diff`, `/commit` etc. marked `locked: true`,
   routed through `slashLocked()` instead of executing directly) — `:12199-12200, 12399-12401`. Same
   broker-approval convention as the Tools-panel Run flow — a sitewide gating pattern, not a
   one-off.

**Flagged for human call:** none — `onlyInV7` is empty for this area.

**Needs a product decision (1):**
- **`huggingface_download` vs. `model_hub_download` naming** — the single one-entry difference in an
  otherwise byte-identical 113-tool registry (`daveai-v7/js/tools.js:71` vs.
  `vps/daveai-ui-v6.html:3225`; confirmed via full-array diff that every other entry and both `CATS`
  arrays are byte-identical). Low functional risk either way since tool invocation is now a
  free-text prompt rather than an exact backend key match, but decide with whoever owns the backend
  tool implementation which name should actually ship before finalizing the new registry.

**Representative clear-cut items** (of 4 `evolvedDifferently`, 3 resolved "current"):
- **Tool "Run" execution flow** (`runToolApi()`): v7 fires `/api/run-tool` directly and shows the
  raw result immediately in the modal. Current composes an approval-gated natural-language broker
  request into the chat composer instead for destructive tools (delete/reset/restore/deploy/db/
  etc.) — closing exactly the kind of "irreversible action without explicit permission" gap this
  environment's own safety rules warn about. *Real trade-off flagged*: current applies the composer
  round-trip to *every* tool, including obviously read-only ones (`git_status_tool`,
  `health_check`), so a quick status check now requires a full manual compose-and-send round trip
  instead of an instant inline result. The comparison agent suggests keeping current's broker-gated
  model as the default but considering a fast synchronous "peek" path for a human-curated allowlist
  of verified read-only tools.
- **`authHeaders()`** added to the DB quick-query endpoint — v7 sent arbitrary raw SQL with zero
  auth header on `/api/db/query`.
- **ARIA/keyboard operability** added to tool-list and skills-list rows (`role="button"`/
  `tabindex`/`aria-label`/`activateOnKeyboard`) — v7's rows were mouse-only `<div>`s.

### Voice / TTS system (full detail)

*Scope: Voice Studio, narration hooks, voice bar —`daveai-v7/js/voice.js` (2,088 lines) +
`css/voice.css` vs. the inline voice code in `vps/daveai-ui-v6.html` plus its external
`vps/assets/daveai-v6.css`. Cross-checked against `G:/VPS/CLAUDE.md`'s "99+ English Azure voices"
mandate and the reference catalog at
`G:/Github/kilocode-Azure2/packages/kilo-vscode/webview-ui/src/data/azure-voices.ts`. `brain_llm.py`
contains no TTS/voice-selection logic — only a "voice-safe" (stack-trace-free) fallback chat
message, which complements but does not overlap this client-side module.*

**Flagged for human call — 3 items:**
1. **4-second TTS "failsafe" timer** that speaks a friendly warm-up line via browser TTS whenever
   every real engine is slow (`daveai-v7/js/voice.js:638-648` — *"Hey! I'm Dave, AI. The main LLM is
   warming up, give me just a moment!"*). Has no equivalent in current — it only makes sense while a
   browser-TTS tier exists to speak the warm-up line through, and that tier was removed. The
   comparison agent's own framing (not this document's recommendation): worth reviving in some form
   — even just a "voice is taking longer than usual" toast — once/if any fallback tier returns.
2. **Rich 6-check engine diagnostics in `vsCheckEngine`** (Web Audio API, browser-voice count+score,
   Kokoro/Chatterbox health ping, HuggingFace test call, Edge TTS proxy health, audio-output resume
   test) feeding a computed "best engine" ranking — `daveai-v7/js/voice.js:1480-1621`. Current's
   version (`vps/daveai-ui-v6.html:8539-8588`) is reduced to 3 checks — a reasonable simplification
   *given* only one engine remains, but it's the diagnostic mirror of the fallback-cascade removal
   in decision G below; only relevant if that question is answered "yes."
3. **Original 22-voice Kokoro-ID catalog** (`bf_emma`, `bm_george`, `af_heart`, `am_fenrir`, etc.)
   with differentiated reliability grades (A through D+), plus an already-built Kokoro→Edge/Azure
   name map (`_vsEdgeVoiceMap`, `daveai-v7/js/voice.js:812-828`) that current's one-time migration
   didn't reuse — it hard-resets every returning user to Maisie instead
   (`vps/daveai-ui-v6.html:7685`). The comparison agent's framing: independent of the bigger
   fallback-tier question, reusing the existing ID map so returning users keep a voice "personality"
   close to their old choice would be cheap regardless of what happens with local engines — flagged
   here for a human decision, not adopted as this document's own recommendation.

**Must port forward — 5 items:**
1. **The mandated 99+ English Azure voices catalog**: `VS_VOICES` holds 99 `en-*` Neural entries
   across 14 English locales (en-GB, en-US, en-AU, en-CA, en-IE, en-IN, en-NZ, en-SG, en-ZA, en-HK,
   en-KE, en-NG, en-PH, en-TZ), ported essentially verbatim from the kilocode-Azure2 reference —
   field-for-field match on names/descriptions/emotional `styles` arrays —
   `vps/daveai-ui-v6.html:6537` onward, self-check at `:8548` (`VS_VOICES.length >= 90`). This
   directly closes `CLAUDE.md`'s P0 item 5. Described in the synthesis as "the single biggest
   confirmed delta between the two sides" and "the flagship deliverable of the whole area."
2. **Auth-gated Azure TTS proxy** — `_vsTierAzureTTS` throws `"Sign in required for Azure TTS"` when
   not authenticated — `:7917-7918, 8550-8553`. v7's `/api/tts` had no such check; a real product
   change (anonymous visitors now get zero voice, not even a degraded one).
3. **"Moshi Instant Voice"** — a new real-time voice-conversation mode over a WebSocket bridge
   (`vsConnectMoshi`, auto-reconnect, `ws://localhost:8998` default) — `:1138-1157, 8426-8493`.
   Wholly new; zero v7 trace. Port as its own module, not merged into the turn-based TTS pipeline.
4. **Accessibility retrofit of the entire Voice Studio UI** — `role="dialog"`/`aria-modal`, real
   ARIA tabs (`role="tab"`, `aria-selected`, roving `tabindex`), keyboard-operable voice cards
   (`role="option"`), real `<button>` quick-picker items, matching `:focus-visible` CSS —
   `:878-896, 7751, 8900`, `vps/assets/daveai-v6.css:88-95`. v7's version is plain `<div>`s with only
   `onclick`/`.on` class toggling.
5. **Safer load-time defaults**: never auto-requests microphone access (prompts the user to click
   instead); narration/auto-read state now resyncs in both directions to the persisted chat mode
   instead of only ever forcing "on" — `:8859-8869, 8729` (`_dvAutoRead` now defaults `false`).

**`evolvedDifferently` — all 6 items, full detail:**
1. **Core TTS request path** — *marked unclear-needs-human-call; the single most consequential open
   decision in the entire plan.* v7 runs a 5-tier fallback cascade (local admin engine →
   Kokoro/Chatterbox → HuggingFace → Edge → browser SpeechSynthesis), each independently try/caught
   with its own cache tag (`daveai-v7/js/voice.js:594-723`). Current calls Azure directly with **no
   try/catch** around the call in `vsSpeakRaw` — confirmed the fallback tiers are truly gone, not
   just deprioritized: `_vsBestBrowserVoice()` returns `null`, `_localVoiceSpeak()` returns `false`,
   and there are zero remaining `SpeechSynthesisUtterance`/`onvoiceschanged` references anywhere in
   the 12,920-line current file. This directly contradicts a still-standing instruction in
   `G:/VPS/CLAUDE.md`: *"Keep browser SpeechSynthesis as fallback, but server-side Azure/Edge voices
   should be the polished path."* Current satisfies the second half and violates the first half.
   Today, an Azure outage, an expired session, or a signed-out visitor produces **total, silent
   voice failure**. **Decide:** is that trade-off (simplicity/consistent quality vs. resilience)
   acceptable, or does the rebuild need at minimum a browser-SpeechSynthesis last-resort tier?
2. **`/voice` slash-command keyword coverage for the 14-locale catalog** — *marked
   unclear-needs-human-call, lower stakes.* The Voice Studio picker UI was correctly rebuilt to
   group by all 14 English locales (`const locales = [...new Set(VS_VOICES.map(v =>
   v.locale))]` — `:8889-8891`), but the `/voice british`/`/voice american` slash commands still
   only filter `en-GB`/`en-US` (`:8974-8980`), silently ignoring the other 12 locales (AU/CA/IE/IN/
   NZ/SG/ZA/HK/KE/NG/PH/TZ) now in the catalog. **Decide:** extend the keyword set (e.g. `/voice
   australian`, `/voice indian`), or leave the two original shortcuts as-is.
3. **Per-voice quality "grade" badge**: v7's grades varied meaningfully and reflected real quality
   notes (A down to C-, e.g. `af_sky` "Light and airy" graded C- next to `af_heart` "Premium quality
   voice" graded A). Current hardcodes every voice to `"A+"`/`"A"`, and the rendered badge doesn't
   even show the grade field — it always prints the literal text `"AZ"` (`:7754`). Verdict: current
   (Azure Neural voices are uniformly high quality, so a manufactured differentiator would mislead)
   — but the leftover per-voice `grade` field and unreachable `.vc-grade.b/.c/.d` CSS rules are dead
   weight that should be **deleted**, not carried into the new module, so a future maintainer
   doesn't assume the grade means something.
4. **Voice Studio tab-pane switching** (`vsTab()`): current added proper roving-tabindex ARIA tabs
   (`aria-selected`/`tabindex`) plus native `hidden` instead of CSS-only visibility, replacing v7's
   plain class-toggle. Verdict: current, no downside identified.
5. **"Always-On" continuous voice-input**: v7's `voice.js` owns a private `SpeechRecognition`
   instance directly and auto-starts it 2 seconds after page load if the persisted chat mode is
   `alwaysListen`. Current delegates to the app's shared `toggleMic()` subsystem instead of a second
   independent recognition lifecycle, and replaced the load-time auto-start with a user-facing
   prompt. Verdict: current — cleaner in every dimension checked, and removes a surprise-mic-
   activation privacy smell.
6. **Default narration/auto-read state consistency**: v7's defaults actively contradict each other
   (`_dvAutoRead = true` and `narration.chat: true` at the module level, while the default chat-mode
   resolves to "Text" with `voiceOut:false` — and the load-time sync only ever forces values to
   `true`, never back to `false`), so a fresh v7 session in default "Text" mode would still speak
   chat replies. Current syncs both directions off the actual persisted chat mode. Verdict: current
   — fixes a genuine state-consistency bug, and the resulting "new user hears nothing until they opt
   in" behavior matches `CLAUDE.md`'s contemporaneous ask to quiet default voice behavior.

**Bottom line for this area** (from the synthesis's scope-reality-check section): nothing here is
unlaunched — everything found in this diff, on both the catalog side and the fallback-removal side,
is already live in current production today. The 99-voice catalog is genuine, substantial,
already-shipped work, not a gap. But the fallback removal is a real, currently-unaddressed gap
against the team's own stated `CLAUDE.md` requirement, and the new build should not silently
inherit it.

**Also flagged:** when splitting the monolith, isolate voice/TTS/narration code cleanly — v7's own
`voice.js` was not a clean cut either (it also carried unrelated admin-user-management,
activity-center rendering, and log-tailing code from the original monolith) — the new module
boundary should not repeat that mistake.

---

## What This Means for daveai-website/

1. **Direction of the port is current → v7-shaped modules, not v7 → current.** Across all 12 areas,
   `onlyInV7` is empty in 8 of them, and where it isn't, the total is only 7 items (mostly one
   deliberate architectural trade — dropping self-hosted TTS for a cloud-only voice stack — rather
   than scattered accidental loss). Not one of the 61 `evolvedDifferently` comparisons favored v7
   outright. **Do not copy any v7 file's contents into the new build.** Use only `daveai-v7`'s
   directory/module boundaries (`js/{agents,app,auth,canvas,chat,config,panels,personality,state,
   status,tools,voice}.js` + matching `css/`) as the target shape for `daveai-website/`, and populate
   every module from **current** (`vps/daveai-ui-v6.html` + `brain_llm.py`).

2. **Build in the same 4 tiers the synthesis lays out**, because later tiers depend on earlier ones
   working:
   - **Tier 1 — Chat, Auth, Session/Data Layer.** Nothing else works until sign-in, the JWT/token
     layer, `_currentUser`, and `_dbFetch` exist, since Chat's persistence and Auth's gating run on
     top of them.
   - **Tier 2 — Panels & Status.** The BrainState health SSOT and the Memory/History panes.
   - **Tier 3 — Voice, Agents, Personality.** The 99-voice Azure catalog, narrator-first routing, and
     the personality-prompt system.
   - **Tier 4 — Canvas/Games, Tools, Config, App-Init.** The game carousel/catalog, the live
     tool-registry sync, and the workspace-layout engine.

3. **Resolve or explicitly defer the open calls before finalizing scope**, not after:
   - The **3 revive-or-leave-behind clusters** (self-hosted TTS + its failsafe timer + its
     diagnostics — one bundle; the post-sign-in video replay; two smaller standalone items on
     semantic CSS classes and the swallowed health-check error state).
   - The **8 product decisions** (video-first vs. auth-first entry funnel — spanning App-init, Auth,
     and State; chat-unreachable copy; the uptime metric; voice-input mic architecture; the
     `huggingface_download`/`model_hub_download` name; the `seedProjects` URL guard; and, most
     importantly, **voice engine resilience** — Azure-only vs. restoring at least a browser-
     SpeechSynthesis last-resort tier — plus the `/voice` slash-command locale-keyword gap).
   - **Voice resilience is the one item on this entire plan that is not just "port current
     forward."** Reintroducing a working non-Azure fallback tier, if the team wants one, is genuine
     new engineering — v7's cascade can inform the *shape* of a solution, but its specific engines
     (Kokoro/Chatterbox/HuggingFace) may or may not be worth resurrecting. Get this decision early,
     since it affects the Voice module's whole architecture, not a small patch.

4. **Personality and voice need special handling, not just a file copy:**
   - Pull the "Mode-Aware UI" 9-mode router out of `personality.js`'s eventual replacement entirely
     — it belongs in a routing/navigation module.
   - Keep "Alice"/narrator-first routing in the chat/voice modules, not personality — it predates
     March and lives there conceptually on both sides.
   - Decide the Azure-only-vs-cascade question (item 3 above) before finalizing the voice module,
     and delete the decorative, hardcoded-`"A+"` voice `grade` field/CSS rather than porting it.

5. **Do the cross-cutting cleanup once, centrally, rather than per-module:**
   - Consolidate `AGENT_COLORS`/`AGENT_NAMES` — currently re-declared as `SB_AGENT_COL`, two ad-hoc
     `roleCol` literals, an inline `agentColors`, and an inverse `shortByRole` map.
   - Collapse the three independent `/api/health` pollers (`pollBrain` 5s, `updateStatusBar` 5s,
     `checkApiHealth` 30s) into one shared fetch feeding `BrainState`; delete `updateStatusBar`'s
     dead `ok` variable.
   - Collapse `/voice` slash-command handling onto one code path (currently `think()`'s inline check
     and the general slash-command dispatcher both exist).
   - Finish the partially-migrated `_setCurrentUser()`/`_isCurrentUserAdmin()` pattern — several
     inline `_currentUser?.role === 'admin'` checks still coexist with the helper.
   - Fix stale header comments (e.g. "POST /api/chat" where the code actually calls `/api/stream`).

6. **Verify before assuming something is truly lost.** Several `onlyInV7` findings carry an explicit
   lower-confidence caveat because v7's *given* files were corrupted/truncated by whatever process
   split the original monolith, or because v7 has sibling modules outside a given area's two
   reviewed files — most notably: a separate ~106KB `voice.js` and ~26KB `tools.js` referenced from
   `agents.js` (per-agent voice assignment and the tools-attribution catalog may already exist
   there), and a separate `auth.js` referenced from `state.js`/app-init (the JWT token layer may
   predate March). Before finalizing scope for `daveai-website/`, spot-check the real `daveai-v7/`
   tree at `G:/VPS/daveai-v7/` for these specific items rather than trusting only this comparison's
   per-area file slices. Likewise, `/assets/daveai-v6.css` (current's real external stylesheet) was
   not reviewed line-by-line for most areas — check it directly before treating any v7-only CSS
   class as confirmed-gone.

7. **Nothing here should block starting the rebuild.** The synthesis's own overall estimate is that
   this is "mostly port forward, not near-rewrite" — the actual work is almost entirely mechanical
   extraction and consolidation (re-splitting ~13,000 lines of current production HTML/CSS/JS along
   v7's module boundaries), not new feature engineering, with one bounded exception: voice
   resilience (item 3 above), which is genuine new build work regardless of which side of the
   decision the team lands on.
