# DaveAI.tech Confirmed Findings — Punch List (2026-09-15)

**130 of 133** candidate findings from the section-by-section production-source audit are
confirmed real. **3 were rejected** as false positives (see [Rejected Candidates](#rejected-candidates-3)).

**Fix status update (2026-09-15, same day):** all 12 Fix-First findings are resolved except two
explicitly deferred security items:

- **Security: 7/9 fixed** — S1, S2, S3, S4, S6, S8, S9. **S5** (hardcoded nginx secret) and **S7**
  (hardcoded internal IPs/ports) are explicitly *not* fixed — both need more than a quick edit (S5
  needs coordinated secret rotation with whatever consumes the token, plus the old value stays
  exposed in git history regardless; S7 needs a real authenticated backend endpoint to replace
  static markup) and are left for deliberate, separate handling.
- **Accessibility: 3/3 fixed** — A1 (all 23 Settings toggles now have a real `aria-label` matched
  to their own description text, mapped and applied programmatically so none were mistyped or
  swapped), A2 (`for`/`id` pairing added to all 4 auth-form fields), A3 (the mode-switcher menu
  now moves focus in on open, supports ArrowUp/ArrowDown/Home/End navigation and Escape-to-close
  with focus return to the trigger — the ARIA `menu`/`menuitem` roles it already declared are now
  actually backed by the keyboard model they promise).

Every fix was re-verified with a fresh `node --check` of the entire embedded script block after
editing (still passes), and the two Phase 0 drift fixes were confirmed byte-for-byte identical to
a live production fetch. **None of these fixes have been deployed to production** — they exist
only in this git working tree pending review and an explicit deploy step.

**Batch 2 (same day, continuing into §5):** Infra (all 6 — see per-finding notes: #4 and #5 were
explicitly NOT fixed, left with clear comments per the same "don't fake it" standard as S5/S7),
all 5 Chat broken/non-functional HTML findings (SSE-failure recovery, transcript rehydration,
game mini-chat's fake reply replaced with the real one, voice indicator now turns off, Memory
panel's "Open" no longer falsely claims to resume a session), and all 8 Settings broken/non-
functional findings (personality-toggle `|| true` bug, Refresh Now's missing `.catch()`, the
stale-custom-model-blocks-preset bug, the settings-lock that didn't actually disable anything,
admin tool counts now computed from the real registry instead of hardcoded — two of the eight,
Moshi and the icon-pack switcher, are genuine feature gaps rather than bugs and were deliberately
left honest rather than faked, matching S5/S7's treatment), the external CSS file (all 8 —
including a real `!important`-vs-specificity bug defeating the desktop grid layout, and two
contrast fixes with computed ratios rather than guesses), and `brain_llm.py` (all 10 — including
a redesigned ReAct-marker filter, real Stage-4 streaming/exception-handling fixes, a balanced-
bracket JSON extractor, and one dead-code removal judged safer than implementing a check that
would have misfired on every normal chat turn). All three background agents' work was
independently re-verified (syntax/AST checks re-run by the orchestrating session, not just
trusted from their own reports).

**Batch 3 (same day): all 20 Menu & Navigation findings, plus both `daveai-sites-config.json`
findings.** Notable: the sidebar active-icon highlight was off by one for Tools/Agents/Skills
(the map only budgeted one slot for two buttons — Deploy and Analytics — that sit before them);
the Files/Code cache guard checked `window._filesTreeData`, which nothing ever set, while the
real data lived in a same-scope variable of the same name minus `window.` — always false, tree
refetched every mode switch; ~95 lines of a second, entirely dead Ctrl+K command-palette
implementation were removed (confirmed unreachable — the real one always ran first), and its ~17
real commands (New Page, Open Projects, Toggle Dark/Light, Clear Chat, etc.) were carried forward
into the live palette rather than left stranded in deleted code; the keyboard-shortcuts panel
previously advertised 6 shortcuts wired to nothing and mislabeled plain `Enter` as `Ctrl+Enter` —
rebuilt from the file's actual keydown handlers; 5 dead links to a `docs/` path that is never
published on the live site were removed rather than "fixed," since no relative-path correction
makes an unpublished folder reachable. One accessibility item (canvas Preview/Code tabs) got only
a partial fix — `aria-controls` added, but the missing `role="tablist"` wrapper was deliberately
not added since it required restructuring a flex-layout container this offline session has no way
to visually verify.

**Batch 4 (same day): all 14 "Other" findings, plus the remaining 15 Settings Panel findings
(8 accessibility/cosmetic items already tallied above were carried in this batch too — see
corrected Settings count below).** Other: the Memory panel's "Open saved project" now sets
`_projSelected` and no longer hardcodes the production marketing URL as a fallback preview
target; fabricated Analytics/Admin-Agents numbers and the scripted fake Supervisor/Coder/QA
chat exchange were replaced with neutral `—`/`idle` placeholders matching the honest
"connecting…" pattern used elsewhere; `renderTools()`'s case-sensitive name search fixed;
admin dashboard VPS/PM2 rows now escaped (parity with the Online Users rows next to them); the
Spectrum waveform hue bug fixed (`parseFloat` couldn't parse a `0x`-prefixed literal — switched
to `parseInt(..., 16)`); Memory panel gets a real re-entrancy guard independent of the force
flag, and its auto-refresh interval now restarts on tab-visibility change instead of dying
permanently the first time the tab is hidden; keyboard-shortcuts dialog, Activity Center feed,
and Profile modal all get focus/Escape/`aria-live` wiring; three fully-dead code paths removed
(`typeEmoji`, `_demoIdleTimer`, `_dvGetWfGlow`). **14/14 addressed.**

Settings Panel's remaining 15 (of 23 total — 8 "Broken/non-functional" were already covered in
Batch 2): 8 `for`/`id` label pairs added (Settings modal descriptive text + Admin Users form),
`role="group"`/`aria-labelledby` added to 4 picker grids, Voice Studio's nested-tabbable card
button fixed (the option itself, not a child `<button>`, is now the sole tab stop), a
click-outside-close handler added to the Settings overlay, and 2 dead-code cleanups
(`_vsAzureOnlyVoiceCache` state variable, `_testLocalVoice`/`_localVoiceSpeak` functions — none
had any caller anywhere in the file). The Local Voice Engine "hardcoded settings" item was
re-examined and reclassified as **working as intended, not a bug**: DaveAI's only implemented
voice path is Azure Neural, so a single-option, non-configurable control here is honest, not
broken. **13/15 fixed, 1/15 reclassified (not a bug), 1/15 still open** — the Icon/Theme
Studio's waveform-color/type/icon-studio grids are still populated exactly once via a 1.5s
`setTimeout` on page load (`_dvInitNewFeatures`, ~line 11904) with nothing re-rendering them if
the relevant settings panel is opened before that timer fires; a real fix means finding (or
adding) a panel-open hook to call `_dvRenderColorGrids()`/`_dvRenderWfTypeGrid()`/
`_dvRenderIconStudio()` directly, which needs the panel's open path traced first rather than
guessed at.

**Corrected Settings Panel running total: 19/23 fixed, 3/23 honest feature-gap deferrals (Voice
Blend, Moshi Instant Voice, icon-pack switching beyond Stock — each would need real backend/audio
work: server-side voice mixing, WebSocket audio streaming, or a file-wide icon-name abstraction
layer respectively; the icon-pack switcher's old fake-then-revert behavior was replaced with an
honest "not implemented" message rather than patched, which also structurally eliminates the
separate stale-30-second-revert-timer bug that only existed because the fake switch existed),
1/23 still open (grids-populate-once timing, above).**

**Batch 5 (same day): Chat's remaining findings.** Building on Batch 2's 12/32, this batch closed
essentially all of the rest:
- **`think()` re-entrancy** (the `chat-mode:overwrite` / concurrent-`/api/stream` finding): the
  dead `chatEs` EventSource reference (declared, never assigned — the real path streams via
  `fetch()` + a `ReadableStream` reader, not `EventSource`) is replaced with a working
  `AbortController`-based guard. Sending a new message now actually cancels a still-running
  previous stream instead of both mutating the same bubble/build-bar/agent-pill elements at once.
  Required hoisting the controller alongside the already-hoisted `bubbleId`/`fullText` (the same
  pattern Batch 2 used) so the `catch` block can see it, an abort-check in the SSE retry loop so
  a cancelled send isn't mistakenly retried, and an `AbortError`-specific early return in `catch`
  so a superseded call's error handling doesn't fire (no false "interrupted" bubble, no fallback
  fetch for a message the user already replaced).
- **Retry-loop dead code**: the post-loop `if (!res || !res.ok) throw ...` was unreachable
  (every non-break loop exit already throws) — removed. Its **no idempotency key** is *not*
  fixed: `/api/stream`'s route handler lives only on the VPS, not in this repo, so there's no way
  to confirm whether adding a key to the request body is safe (a strict schema could reject it
  and break every chat send) — documented in place rather than guessed at.
- **Force-scroll ignoring manual scroll-up**: `keepTranscriptAnchored()` now checks actual scroll
  position and only snaps to bottom unconditionally when a caller explicitly says this is a
  deliberate anchor point (new message sent/received, layout/panel change, approval events) —
  all 11 existing call sites were individually reviewed and given `force=true` except
  `updateChatBubble`'s (the one invoked once per streamed token), which is exactly the call site
  the finding was about.
- **`appendChatBubble`/`updateChatBubble` markdown inconsistency**: AI-role bubbles now render
  through the same `md2html()` call `updateChatBubble` already used, instead of plain `escHtml()`
  — fixes the one path (the non-streaming network-fallback reply) that showed raw markdown syntax.
- **No way to clear chat history**: added — a trash-can button next to Export/Copy in the History
  panel (`_clearChatHistory()`, confirm-gated since it's irreversible, also carried into the
  command palette), clearing both the persisted array and the visible transcript.
- **History search reverting on new messages**: `renderHistory()` now delegates to the active
  filter (reading `#hist-search`'s current value) instead of always re-rendering the unfiltered
  list, so `addToHistory()` firing mid-search no longer wipes it.
- **Replay doesn't replay**: rather than implementing silent auto-send (a misclick would fire a
  real LLM call the user didn't ask for), the row's label/tooltip/aria-label were corrected to
  honestly describe what they do — load into the composer, not send — matching the same
  honesty-over-guessing choice already made for the Memory panel's "resume" wording in Batch 2.
- **Duplicate edge-zone listeners**: the `ez-*` hover strips were already fixed (cloned to drop
  old listeners); the persistent `topbar`/`lsb`/`rp`/`chat` panels were not, and can't safely be —
  they're wired up elsewhere in the file too, so cloning them would silently destroy unrelated
  listeners. A one-time-wire `dataset` marker stops `_initEdgeZones()` (called from 2 separate
  settings toggles) from stacking duplicates on repeat calls, without touching the panels at all.
- **`gameToggleVoice` no await/catch**: `.catch()` added.
- **TTS race on `_vsPlaying`**: root-caused to `_vsPlayBlob`'s `onended` closure trusting its own
  captured `source` reference instead of checking whether it's still current — a source
  force-stopped by a newer overlapping call still fires `onended` afterward, and it was
  unconditionally resetting shared state/hiding the overlay even when a *newer* source was by
  then actively playing. Fixed with an identity check (`source !== _vsCurrentAudio`) before any
  shared-state mutation, mirroring the guard pattern used for `think()`'s `_thinkAbort` above.
- **Chat-mode overwriting the narrate preference**: the cold-load line forcing
  `_vsState.narration.chat` to match the chat mode's `voiceOut` flag ran unconditionally in both
  directions. The "force OFF in text-only mode" direction is real safety intent (never let the AI
  unexpectedly talk) and is kept; the "force ON in a voice-capable mode" direction was silently
  overwriting the user's own separately-saved preference on every page load and was removed —
  a voice-capable mode now leaves the loaded preference alone instead of stomping it.
- **Both accessibility-gap items**: the composer (`#pi`) gets a real `:focus-visible` outline
  (CSS — the existing 1px border-color change was too subtle to count as a visible indicator).
  The History-replay-rows-are-mouse-only item turned out to already be fixed — `role="button"`/
  `tabindex`/`onkeydown="activateOnKeyboard(event)"` are present on those rows now, added earlier
  in the session as a side effect of applying that same pattern broadly, but never credited
  against this specific finding until this cross-check caught it.
- **All 4 cosmetic/dead-code items**: the dead Web Speech API scaffold (`_speechRec`,
  `_hasWebSpeech`, `_initSpeechRec` — real voice input is server-side `MediaRecorder` +
  `/api/transcribe`, unrelated) removed; the duplicate never-wired `handleChatKey` (confirmed via
  exact-match grep to appear exactly once in the whole file — its own definition) removed; the
  voice-bar "speaking" pulse indicator's dead wrapper comment/unused capture were replaced with a
  real implementation wired into the same already-race-safe start/stop points `_vsPlaying` uses,
  rather than an independent wrapper that would have reintroduced the same overlap race being
  fixed elsewhere in this batch; the agent-pill `s-done → s-idle` auto-reset timer now re-checks
  `aria-pressed` at fire time instead of hardcoding a class string that always dropped
  `is-selected`, regardless of whether the pill was still actually selected.
- **The 2 stray Chat-area nginx findings** (outside every prior batch's scope): `Accept-Encoding
  ""` added to the `/hermes/` block so `sub_filter` can see a plain-text response instead of
  silently no-op'ing against gzip (the standard documented nginx fix for this exact interaction);
  `Host`/`X-Real-IP`/`proxy_http_version` added to the sibling `_app/static/assets/favicon` block,
  which had none of its neighbor's `proxy_set_header` directives.

**Corrected Chat (32) running total: 31/32 addressed** (30 fixed outright + 1 honestly-relabeled
per the replay-doesn't-replay item above), **1/32 partially addressed** (the retry-loop's dead
code is removed; its missing idempotency key is a documented, deliberately-not-guessed-at gap,
same treatment as S5/S7/VISION/Voice Blend/Moshi/icon-pack-switching). Independently
`node --check`-verified after every edit in this batch (7 separate checks across the batch, all
passing) plus a final full-file check at the end.

**CSS (10) — corrected:** all 8 findings that live in the external `daveai-v6.css` file were
fixed as part of Batch 2's CSS agent work (verified item-by-item against that batch's own
description: the desktop-grid `!important` defeat, the `.demo-btn-play`/`.dev-choice.recommended`
split-rule merges, the `--t3` and `.demo-meta` contrast fixes, the 44×44 touch targets, the
focus-visible outlines, the redundant breakpoint removal, and the `--topbar-h` sync all match).
**8/10 fixed.** The other 2 (`vps/daveai-ui-v6.html:16-20` dead status-color rule,
`vps/daveai-ui-v6.html:15` dropdown position) are inline in the HTML file itself, outside that
batch's scope, and remain **open**.

**Backend (8) — corrected:** of the 4 `brain_llm.py` findings, 3 were fixed alongside that file's
other Batch 2 work — the ReAct-filtered accumulator is now what `_litellm_call` actually returns
(closing the raw-vs-filtered mismatch), `llm_json`'s balanced-bracket extractor now tolerates
trailing prose after a valid JSON value, and the dead `_seen_any_final` field was removed. The
4th (`VISION` imported but never wired into any function here) was **not** fixed — a `# TODO`
comment documents the gap rather than papering over it, since actually wiring a vision stage in
is new functionality, not a bug fix. **3/8 fixed, 1/8 honestly documented as a gap, 4/8 (the
HTML-side `_dbFetch`/`_dbSyncUser`/polling findings) not yet started.**

Chat is now fully addressed (32/32 — 31 fixed/reclassified/honestly-relabeled outright, plus the
retry-loop finding whose dead-code half is fixed and whose idempotency-key half is a documented,
deliberately-not-guessed-at gap, the same treatment as the deferred items below). Nothing in Chat
is untouched any more.

**Batch 6 (same day): Auth & Session (all 5, previously untouched), the 2 CSS findings inline in
the HTML file, all 4 Backend HTML-side findings, and one Settings item that turned out to already
be fixed.**

- **Auth & Session, all 5**: the `iptv.daveai.tech` provider-vault prefix block gets its own
  generic-JSON 401 error page instead of falling through to the server-wide HTML login redirect
  (a *new* named location, not reusing the sibling `/providers` endpoint's `{"providers":[]}`
  shape, since that would be the wrong response for whichever other endpoint under this prefix
  isn't "list providers"); the Admin Dashboard's auto-refresh now starts from a shared,
  once-only-guarded helper called both at page load and from `_setCurrentUser()`, so an admin
  who authenticates mid-session (not just one who already held a valid token at page load) gets
  it; the legacy `/api/admin/login` fallback is no longer gated to one hardcoded personal email
  (the server, not a client-side allowlist of one address, should decide eligibility) and no
  longer hardcodes `role:'admin'`/`display_name:'DaveAI'` on every success regardless of who
  authenticated — it now prefers the server's own response fields; profile-save's `serverSaved`
  flag now defaults to `false` and is only set `true` right after a request actually succeeds,
  instead of defaulting `true` and reporting "Profile saved!" for a save that never contacted the
  server; the admin panel's duplicate `_authHeaders()` now delegates to the shared `authHeaders()`
  instead of always sending `Authorization` (even `Bearer null`) when logged out.
- **CSS's 2 HTML-inline findings**: the dead `#b2bec3`-keyed status-color rule was removed (with
  an explanation of why it was unreachable — `#fp-sites` is static hand-written markup with
  hardcoded statuses, never populated from live data, so nothing ever sets that color inline);
  `#dd`'s hardcoded `top:68px` (matching none of `--topbar-h`'s real values) now reads
  `var(--topbar-h)`, the same variable other topbar-anchored elements in the CSS file use.
- **Backend's 4 HTML-side findings**: `_dbFetch`'s header-merge bug fixed (`...opts` now comes
  before the computed `headers:` key, so a caller-supplied `opts.headers` can no longer silently
  replace the Content-Type/auth merge outright — no current caller triggers this today, but the
  next one to pass custom headers would have); the Admin Logs tab's 5-second poll now actually
  stops (`stopLogTail()`, called from `setAdmTab()` whenever navigating to any other admin tab)
  instead of running forever after the first visit. The other 2 — `_dbSyncUser`'s display-name
  collision and the BrainState/`pollBrain` polling-consolidation claim — are **not fixed**: both
  need visibility into the actual `/users/*` backend route (not in this repo, lives on the VPS
  only) or a real multi-function refactor respectively, and guessing wrong on either risks making
  things worse (e.g. a wrong unique-key guess would turn "rare name collision" into "a new
  duplicate user row on every login"). Left with detailed comments explaining exactly why, plus a
  correction to the misleading "canonical"/"POLLING COORDINATOR" naming that overclaimed a
  consolidation that was never actually done.
- **Settings' previously-reported "1 open" item was already fixed** — cross-checking against the
  live file found `refreshSettingsUI()` (called every time Settings actually opens) already
  re-renders the waveform/icon-studio grids, with a comment describing the exact same fix this
  running tally had listed as still needed. This was done in an earlier batch as a side effect of
  other Settings work and simply hadn't been credited against this specific finding until now —
  the second time in this document that happened (the first was Chat's History-rows keyboard
  finding in Batch 5), which is itself worth flagging: this tally has undercounted real progress
  at least twice from batch-narrative trust rather than checking the file directly. Settings is
  therefore corrected from 22/23 to the full 23/23.

**Grand total: 130/130 confirmed findings addressed. 0 open.** This is not "zero bugs" or
"complete" — read that plainly as what it is: every one of the 130 confirmed findings from the
original audit has been fixed outright, correctly reclassified as not-a-bug, honestly relabeled
instead of guess-implemented, or deliberately deferred with a documented reason a reader can go
verify in the code itself. **11 findings remain deliberately unfixed by design, not silently
skipped**: S5 (hardcoded nginx secret — needs coordinated rotation), S7 (hardcoded VPS IP/ports in
public HTML — needs a real authenticated backend endpoint), Infra #4 (hardcoded health-check
response) and #5 (dual-hardcoded site count, partially mitigated only), Voice Blend, Moshi, and
icon-pack-switching (all three are real unbuilt features, not bugs), VISION wiring (needs new
vision-stage routing), `/api/stream`'s missing idempotency key, `_dbSyncUser`'s display-name
collision (both need visibility into backend code outside this repo), and the BrainState/
`pollBrain` polling-consolidation claim (needs a real multi-function refactor to migrate each of
4 other polling functions' distinct side effects into the BrainState observer pattern one at a
time — the misleading "canonical"/"coordinator" naming that claimed this was already done is
corrected, but the actual consolidation isn't attempted) — every one of these has an inline
comment at its exact location explaining the gap. Per-area, all fully addressed: Fix-First 12/12,
Infra 6/6, Menu & Navigation 20/20, Other 14/14, Settings Panel 23/23, CSS 10/10, Backend 8/8,
Chat 32/32, Auth & Session 5/5 — 12+6+20+14+23+10+8+32+5 = 130.

This reflects a same-session cross-check against actual file content for every area (not just
batch-narrative trust — which, per the note above, materially changed two totals when applied).
It has **not** been re-verified by a fresh independent reviewer with no stake in the prior work,
and nothing in this list is deployed to production. Treat "130/130 addressed" as an honest
same-session tally, not an external audit sign-off — the responsible next steps are an
independent review pass and, separately, a deliberate decision on the 11 real deferred items
above (none of which should be actioned casually; several touch security or live user data).

## Methodology

DaveAI.tech's real production source — [`vps/daveai-ui-v6.html`](../vps/daveai-ui-v6.html) (12,920
lines), [`vps/patches/daveai-production-runtime-20260731/brain_llm.py`](../vps/patches/daveai-production-runtime-20260731/brain_llm.py),
[`vps/assets/daveai-v6.css`](../vps/assets/daveai-v6.css), and the nginx configs / verification
scripts under `vps/` — was audited section by section. Every one of the 133 candidate findings
that came out of that pass was then **independently re-verified against the live file by a second
agent** before being counted: re-reading the exact quoted lines, checking the evidence is accurate
verbatim, and checking whether related code elsewhere in the file (other JS handlers, other CSS
rules, backend routes, other repo docs) changes the picture. 130 held up; 3 did not (§6).

This document feeds the phased plan in
[`docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`](./DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md) and the six
phase contracts (`CT-000` – `CT-005`) in [`docs/contracts/`](./contracts/); see those documents for
how and when each finding gets scheduled. Two of the security findings below are already referenced
there by ID (`F-P1-01-preview-iframe-sandbox-escape`, `F-P0-05-unauthenticated-admin-panel`).

**A note on severity in this document.** The audit workflow's own automated `bySeverity`
aggregation is broken — it used each finding's free-text verifier note as a dictionary key, so
its output is not usable and is not reproduced anywhere below. Instead, every one of the 130
confirmed findings had its **effective severity** re-derived here, finding by finding, from the
second-pass verifier's own notes:

- Where a verifier's note is a short severity category on its own, that category is used directly.
- Where a verifier's note is a long explanation that affirmatively argues for **escalating** the
  finding — using language like “security,” “CWE,” “vulnerability,” “WCAG Level A,”
  “critical,” or “reclassify” — that escalation is applied, and the verifier's own words are
  quoted as justification. A **Security** category (not part of the original five-value taxonomy)
  was added for the 9 findings verifiers flagged as security issues.
- Where a verifier's note argues for a **downgrade** instead (e.g. “downgrade to cosmetic,”
  “not blanket broken,” “lower than stated”), that recommendation was **not** applied — the
  finding keeps its original, more conservative severity. This document only ever moves a finding's
  severity up from what the audit originally recorded, never down, so nothing here is understated
  relative to the source audit.
- Where a verifier explicitly says the original severity is fair with no correction needed, the
  original severity is kept.

The same logic applies to which accessibility-gap findings appear in **Fix First** below: only
findings whose verifier note affirmatively called out a **WCAG Level A** criterion together with
**critical/high/blocking** impact were pulled forward; several other accessibility-gap findings
touch real WCAG criteria too (mostly Level AA, e.g. color contrast, focus-visible) but their
verifiers explicitly declined to call them critical or blocking, so they remain in the by-area
lists in §5.

## Summary by Effective Severity

| Effective severity | Count |
|---|---|
| **Security** (new category, see Methodology) | 9 |
| Broken / non-functional | 30 |
| Degrades quality | 55 |
| Accessibility gap | 21 |
| Cosmetic / polish | 15 |
| Blocks chat completely | 0 |
| **Total confirmed** | **130** |

`blocks-chat-completely` was part of the original taxonomy but no confirmed finding — after re-verification — rose to “core chat send/receive is completely broken for everyone.” The closest candidates (e.g. cache-hit turns skipping the SSE stream, an uncaught Stage-4 exception path) are real but scoped to specific conditions, not a total outage; they are listed under **Chat** in §5 at their original `broken-non-functional` severity.

## Summary by Area

| Area | Count |
|---|---|
| Chat | 32 |
| Settings Panel | 26 |
| Menu & Navigation | 21 |
| Other | 16 |
| CSS | 10 |
| Infra | 9 |
| Backend | 9 |
| Auth & Session | 7 |
| **Total confirmed** | **130** |

Of the 130, **12** (9 security + 3 critical accessibility) are pulled out into **Fix First** below regardless of area; the remaining **118** are grouped by area in §5.

## Fix First — Security & Critical Accessibility (12 findings)

These 12 findings are pulled out of their area groupings because a second-pass verifier
explicitly argued the audit workflow mis-classified their severity — as a security vulnerability
that the original “broken-non-functional”/“degrades-quality” label obscured, or as a WCAG Level A
accessibility failure with critical/blocking impact rather than a routine “accessibility-gap.” They
are real, confirmed, and **not fixed**. This is the highest-value section of this document.

### Security (9)

#### S1. Unescaped admin user list enables stored XSS into an admin session (Critical) — `vps/daveai-ui-v6.html:5168-5182`

**Summary:** loadAdminUsers() renders u.display_name and u.email directly into innerHTML and into inline onclick(...) JS-string arguments with no HTML/JS escaping, so a crafted display name or email can execute arbitrary script in an admin's session.

**Evidence:** Line 5174: `${u.display_name || u.email}` is interpolated raw into the template with no escHtml() call (contrast with renderHistory's `escHtml(h.text)` at line 4935). Line 5178: `onclick="adminResetPw(${u.id},'${u.email}')"` puts u.email raw inside a single-quoted JS string embedded in a double-quoted HTML attribute — an email/display_name containing a quote or an inline event attribute breaks out and runs as script the moment any admin opens the Users tab and that row renders. Lines 5179-5180 repeat the same unescaped pattern for adminToggleRole/adminDeleteUser.

**Why it matters:** Self-registration is public and unauthenticated (`/api/auth/register`) with no sanitization on `display_name`. Any anonymous visitor can register an account using a script payload as their display name; the instant an admin opens the Users tab, that payload executes with full admin privileges in the admin's own session — a direct path from an anonymous signup to admin session/token compromise, requiring no admin interaction beyond routine use of the panel.

> Verifier's own reasoning for the severity correction: "Not ‘broken-non-functional’ — the code isn't broken, it's insecure. This is a critical-severity stored XSS / privilege-escalation vulnerability... Reclassify as security-critical (stored XSS leading to admin session/token compromise), not a functional/UI defect."

#### S2. Game postMessage handler accepts unauthenticated production-database writes — `vps/daveai-ui-v6.html:6028-6049`

**Summary:** The window 'message' handler that writes hi-scores, map progress, and leaderboard data to the production database never validates e.origin or e.source, so anything that can post a message to this window can forge those database writes.

**Evidence:** `window.addEventListener('message', async (e) => { if (!e.data || typeof e.data.type !== 'string') return; ... await _dbSaveHiScore(d.playerName, d.score, d.mapId, d.mapName, d.difficulty, d.waves, d.stars, d.mode, d.timeSec); ... })` (lines 6028-6049) branches only on e.data.type. There is no `e.origin === ...` or `e.source === document.getElementById('preview-frame').contentWindow` check anywhere in the handler, so any frame/window able to reach this page (e.g. whatever HTML is currently loaded into #preview-frame) can send a fabricated daveai-hiscore/daveai-map-progress event with arbitrary player name/score and have it persisted.

**Why it matters:** The handler performs authenticated production-database writes (hi-scores, map progress, leaderboard) based solely on the shape of `e.data`, never checking `e.origin` or `e.source`. Anything capable of posting a message into this window — including whatever content is currently loaded into the sandboxed `#preview-frame` from the finding above — can forge arbitrary leaderboard/score data straight into the production database.

> Verifier's own reasoning for the severity correction: "Reclassify from ‘broken-non-functional’ to a security vulnerability (high/critical). The feature is not broken... The real defect is missing origin/source validation in a postMessage handler that performs authenticated production-database writes, which is a security/authorization defect."

#### S3. Preview-iframe sandbox allows a same-origin escape — `vps/daveai-ui-v6.html:1809-1812`

**Summary:** The live-preview iframe's sandbox attribute combines allow-scripts with allow-same-origin, directly contradicting the security comment immediately above it and creating a known sandbox-escape path for AI-generated/user preview content.

**Evidence:** Line 1809: '<!-- SECURITY: allow-scripts + allow-same-origin can escape sandbox. We use allow-scripts only for user-generated previews. -->' but line 1810-1812's actual element is '<iframe id="preview-frame" ... src="about:blank" ... sandbox="allow-scripts allow-same-origin allow-forms allow-popups" loading="lazy"></iframe>' — both flags are present together. Since the default src is about:blank (which inherits the embedding page's origin), combining these two flags is the textbook configuration that lets framed script content break out of the sandbox and access the parent app's origin/DOM/storage instead of being isolated, which is exactly what the comment says was supposed to be avoided.

**Why it matters:** `about:blank` inherits the embedding page's origin, and `normalizePreviewTarget()` resolves generated preview content to the same origin as production (`https://daveai.tech/...`). Combining `allow-scripts` with `allow-same-origin` on that frame is the textbook configuration that lets framed script content escape the sandbox and reach the parent app's DOM, storage, and session — on a frame explicitly built to hold AI-generated or user-generated content. The inline comment immediately above the element shows the team already knew this combination was dangerous and shipped it anyway. This is already tracked as `F-P1-01-preview-iframe-sandbox-escape` in `docs/contracts/CT-001-chat-completion.json`.

> Verifier's own reasoning for the severity correction: "Recategorize from ‘broken-non-functional’ to a security vulnerability (high/critical)... the allow-scripts + allow-same-origin combination is a practically exploitable same-origin sandbox escape for any AI-generated/user-generated preview content, not merely a theoretical about:blank edge case."

#### S4. brain.daveai.tech bypasses all login brute-force / scanner throttling — `vps/patches/daveai-production-runtime-20260731/nginx/brain.daveai.tech:14-40`

**Summary:** brain.daveai.tech proxies to the identical backend as daveai.tech's rate-limited /api/ routes (127.0.0.1:8888) but defines no limit_req zones and none of the kilo bot/scanner guards used on the main domain, so all of daveai.tech's login-brute-force and scanner throttling can be bypassed by calling the same endpoints through this hostname instead.

**Evidence:** brain.daveai.tech's only location block (lines 29-39) is `proxy_pass http://127.0.0.1:8888;` with no proxy_pass URI, so `https://brain.daveai.tech/admin/login` reaches the exact same backend path as daveai.tech's `location = /api/admin/login { proxy_pass http://127.0.0.1:8888/admin/login; limit_req zone=login burst=5 nodelay; }`. A repo-wide search confirms `kilo_bad_probe`, `kilo_bad_ua`, `kilo_bad_return_to`, `limit_req zone=api`, and `limit_req zone=login` are referenced only inside daveai.tech among all 6 files in this nginx directory -- brain.daveai.tech, iptv.daveai.tech, stories.daveai.tech, and voice.daveai.tech contain none of them.

**Why it matters:** daveai.tech's main domain carries explicit `limit_req` zones and kilo bot/scanner guards on its login and API routes specifically to blunt brute-force and scanning. `brain.daveai.tech` proxies to the identical backend (`127.0.0.1:8888`) with none of those protections, so an attacker only has to address the same endpoints through the second hostname to bypass all of that throttling entirely.

> Verifier's own reasoning for the severity correction: "Not ‘broken-non-functional’ — the proxy works correctly, nothing is broken. This is a missing security control... Should be classified as a security vulnerability, high or critical severity (auth brute-force exposure)."

#### S5. Hardcoded shared-secret token committed to a checked-in nginx config — `vps/patches/daveai-production-runtime-20260731/nginx/stories.daveai.tech:86-96`

**Summary:** The /local-rig/ location's entire access control is a single long-lived shared-secret token compared in plaintext directly inside this checked-in nginx config file.

**Evidence:** Line 87: `if ($http_x_bridge_token != "552e5787c1030d4b56077adfc504897c116287c59dc7314b") { return 403; }` guarding a proxy_pass to https://127.0.0.1:18788/ (line 88). Anyone with read access to this repository or its git history has the exact token needed to reach that internal backend; there is no rotation, hashing, or secret-store indirection.

**Why it matters:** The only access control on `/local-rig/` is one long-lived token compared in plaintext inside a file checked into git — no rotation, no hashing, no secret-store indirection. Because it lives in git history, it stays exposed even after being rotated in a future commit unless history itself is rewritten. Anyone with read access to this repository, or an old clone of it, holds a permanent bypass credential to an internal backend service.

> Verifier's own reasoning for the severity correction: "Reclassify from ‘broken-non-functional’ to a security finding (hardcoded-credential / secret committed to VCS)... Recommend severity High: anyone with repo or clone access has permanent, un-rotatable bypass credentials to an internal backend service."

#### S6. Sidebar “Settings” button exposes the full Admin panel to any signed-in non-admin — `vps/daveai-ui-v6.html:1416`

**Summary:** The left icon-rail 'Settings' button opens the same admin-only panel as the topbar 'Admin' tab via an identical setPanel('admin') call, but only the topbar tab carries the data-admin attribute the page's own gating logic keys off, so the sidebar route is never hidden from non-admin users.

**Evidence:** Line 1316: '<button class="ptab" id="pt-admin" data-admin onclick="setPanel(\'admin\')">' is gated with data-admin (and the file's admin-hiding logic at line 2571 does 'document.querySelectorAll(\'[data-admin]\').forEach(...)'). Line 1416: '<button type="button" class="sb-btn" data-tip="Settings" aria-label="Settings" onclick="setPanel(\'admin\')">' has no data-admin attribute at all, yet calls the exact same setPanel('admin') function that renders #admin-panel, including the Users tab's '+ New User' admin-account-creation form.

**Why it matters:** The left icon-rail Settings button reaches the exact same admin panel as the gated topbar Admin tab, but carries none of the `data-admin` attribute the page's own show/hide logic depends on. Any signed-in non-admin who clicks it sees the full admin surface — raw infrastructure details (VPS IP, DB engine, internal ports, see the next finding) and user-management controls (create/delete/reset-password/promote-to-admin) — gated only by client-side markup, never by a server-side check. This is already tracked as `F-P0-05-unauthenticated-admin-panel` in `docs/contracts/CT-000-stop-the-bleeding.json`.

> Verifier's own reasoning for the severity correction: "This is a broken access-control / sensitive-info-disclosure defect (CWE-284-style)... I'd recommend classifying it as a security-relevant issue (e.g., High) rather than a generic broken/non-functional UI bug."

#### S7. Internal IPs and service ports are hardcoded into public HTML — `vps/daveai-ui-v6.html:1889-1895`

**Summary:** Internal service topology (LiteLLM's port, the ZeroClaw gateway's port, and the raw production VPS IP) is hardcoded in plain text inside the Admin panel markup, which ships in the initial HTML to every visitor's browser regardless of role since the only admin gating here is client-side display toggling, not server-side exclusion.

**Evidence:** Lines 1890-1895 inside #adm-config (a plain child of #admin-panel with no data-admin attribute of its own): '<div class="adm-row"><span>LiteLLM</span><code>:4000 (local)</code></div>', '<div class="adm-row"><span>ZeroClaw</span><code>:3000 (gateway)</code></div>', and '<div class="adm-row"><span>VPS</span><code>187.77.30.206</code></div>' are delivered as static text to every client and are visible via view-source/devtools regardless of whether the panel is ever displayed to that particular user.

**Why it matters:** The production stack sits behind Cloudflare specifically so the origin IP is hidden from attackers and DDoS/WAF mitigation stays effective. Shipping the literal origin IP and two internal service ports in plaintext, unauthenticated HTML lets anyone who views source bypass Cloudflare entirely and probe the origin and its internal services directly — and it ships to every visitor's browser regardless of role, because the only gating on this markup is client-side display toggling.

> Verifier's own reasoning for the severity correction: "Shipping the raw origin IP ... in plaintext, unauthenticated HTML defeats [the Cloudflare-origin-hiding] control outright... I'd reclassify this as a security/infrastructure-exposure finding (e.g. 'security-medium' or higher) rather than 'degrades-quality.'"

#### S8. escHtml() never escapes quotes — attribute-injection XSS in the Files tree — `vps/daveai-ui-v6.html:12480-12499`

**Summary:** The project Files tree is rendered with `escHtml()`, which never escapes quote characters, inside double-quoted HTML attributes built from user-supplied, unsanitized file/folder names, so a crafted name breaks out of the attribute and can inject markup or handlers.

**Evidence:** `escHtml` (line 4707) is `String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')` — it never touches `"` or `'`. `filesRenderTree()` (lines 12480-12499) uses it inside double-quoted attributes and assigns the result to `treeEl.innerHTML`: `'<div class="ft-node ft-file" role="button" tabindex="0" aria-label="Open file ' + escHtml(rel) + '" data-file-rel="' + escHtml(rel) + '" title="' + escHtml(rel) + '" onclick="filesOpenFile(decodeURIComponent(\'' + encoded + '\'))" ...>'` (line 12494). `filesNewFile()`/`filesNewFolder()` (lines 12548-12572) take the new path directly from an unvalidated `prompt()` and PUT it to the backend with no character filtering, so a path containing a `"` (e.g. `foo" onmouseover="alert(1)`) created via that same prompt will break out of the `title`/`aria-label`/`data-file-rel` attributes the next time the tree renders, corrupting the row's markup and letting attacker/owner-controlled attributes be injected into the page. No alternative attribute-escaping helper (escAttr/escapeAttr) exists anywhere in the file.

**Why it matters:** `escHtml()` escapes `&`, `<`, `>` but never `"` or `'`, and `filesRenderTree()` uses it inside double-quoted HTML attributes built from user-controlled file/folder names — names that come from unvalidated `prompt()` calls in `filesNewFile()`/`filesNewFolder()`. A name containing a double quote breaks out of the attribute and injects an arbitrary handler: self-XSS at minimum, stored/cross-user XSS on any project shared between users.

> Verifier's own reasoning for the severity correction: "Recategorize from ‘broken-non-functional’ to a security defect (HTML/attribute-injection, DOM-based XSS vector) rather than a functional break — the tree renders fine for normal names. Severity: medium — genuinely exploitable (self-XSS at minimum ... stored/cross-user XSS on any shared project)."

#### S9. Custom icon-pack name is XSS-injectable via unescaped innerHTML — `vps/daveai-ui-v6.html:11431-11438`

**Summary:** Importing a custom icon pack takes a free-text name straight from prompt() and inserts it into innerHTML with no escaping when the grid re-renders, so a name containing markup executes as HTML/script in the page.

**Evidence:** Line 11434: `const name = prompt('Give this icon pack a name:') || 'Custom Pack';` is pushed verbatim into `_DV_ICON_PACKS` at line 11435; `_dvRenderIconStudio` (called immediately after, line 11436) builds `+ '<div class="icon-pack-name">' + p.name + '</div>'` (line 11352) and assigns the joined string via `el.innerHTML =` - no escHtml()/textContent anywhere in that path.

**Why it matters:** A pack name typed into `prompt()` is pushed straight into the icon-pack array and later concatenated into an `innerHTML` string with no escaping anywhere in the path. The trigger is narrower than a remote attack — the operator has to type or paste the payload into their own dialog — but it is still a genuine CWE-79 DOM-XSS bug with zero sanitization, not a cosmetic defect.

> Verifier's own reasoning for the severity correction: "Bump from ‘degrades-quality’ to a security-classed severity (e.g. security-medium). This is a genuine CWE-79 HTML/DOM-injection-to-XSS bug (unescaped value into innerHTML), not a cosmetic/quality issue."

### Accessibility — WCAG Level A / Critical Impact (3)

#### A1. All 23 Settings-modal toggles have no accessible name (WCAG 4.1.2, Level A) — `vps/daveai-ui-v6.html:261-788`

**Summary:** All ~23 toggle switches in the Settings modal wrap only the checkbox and a decorative slider span inside <label class="stg-toggle">, while the actual human-readable description lives in an unconnected sibling <div class="stg-toggle-label">, leaving every one of these checkboxes with no accessible name.

**Evidence:** E.g. lines 274-283: the descriptive text 'Auto-immersive on project load' sits in '<div class="stg-toggle-label">' (lines 275-278), while the checkbox is wrapped by a separate '<label class="stg-toggle">' (line 279) containing only '<input type="checkbox" id="stg-immersive-cb">' and '<span class="stg-slider"></span>' — no text. A count in this range found 23 occurrences of class="stg-toggle" and zero instances of aria-label near any of their checkboxes, so a screen reader announces only 'checkbox, not checked' for each of the ~23 settings controls with no indication of what it does.

**Why it matters:** All ~23 toggle switches in the Settings modal put their real label text in an unconnected sibling `<div>`, leaving the checkbox itself with no accessible name at all — a screen reader announces only “checkbox, not checked” for every single one. This is a WCAG 2.1 Level A failure (SC 4.1.2 Name, Role, Value) that, per the verifying agent, makes the entire Settings modal non-functional for screen-reader and voice-control users, not merely degraded.

> Verifier's own reasoning for the severity correction: "Understated rather than overstated. This is a WCAG 2.1 Level A failure (SC 4.1.2 Name, Role, Value)... it affects all 23 toggle controls in the Settings modal, making the entire modal non-functional for screen-reader/voice-control users... Recommend rating this high/blocking severity rather than a minor accessibility-gap."

#### A2. Auth form fields have no programmatic label association (WCAG 1.3.1/4.1.2, Level A) — `vps/daveai-ui-v6.html:1211-1216`

**Summary:** The sign-in/sign-up form's Display Name, Email, Password, and Confirm Password fields use bare <label> text with no for attribute pointing at the input's id, so screen readers cannot associate the labels with their fields and clicking the label text does not focus the input.

**Evidence:** Lines 1211-1216, e.g. '<div class="am-field"><label>Email</label><input id="am-email" type="email" placeholder="you@example.com"></div>' — <label> and <input> are unconnected siblings with no for="am-email"/id pairing, repeated identically for am-name, am-pass, and am-pass2.

**Why it matters:** The sign-in/sign-up form's Display Name, Email, Password, and Confirm Password fields all use bare `<label>` text with no `for` attribute linking to the input's `id`. Screen readers cannot associate the labels with their fields, and clicking the label text does not focus the input — on the one flow every other feature in the app depends on. WCAG 2.1 Level A (1.3.1 + 4.1.2); the equivalent axe-core rule for unlabeled form fields is rated critical impact.

> Verifier's own reasoning for the severity correction: "Consider labeling this ‘serious/critical’ rather than a generic ‘accessibility-gap’: it's a WCAG 2.1 Level A failure (1.3.1 Info and Relationships + 4.1.2 Name, Role, Value) on a blocking authentication flow, and the equivalent axe-core rule for unlabeled form fields is rated ‘critical’ impact."

#### A3. Mode-switcher menu implements zero of the keyboard interaction its ARIA role promises (WCAG 2.1.1/4.1.2, Level A) — `vps/daveai-ui-v6.html:12079-12105`

**Summary:** The mode-switcher's dropdown carries ARIA `menu`/`menuitem` roles but implements none of the keyboard behavior that role implies — opening it never moves focus into the menu, and there is no arrow-key or Escape handling scoped to it.

**Evidence:** `toggleModePicker()` (lines 12079-12105) only toggles the `.open` class and computes fixed-position coordinates; it never calls `.focus()` on the picker or its first item. `renderModePicker()` (lines 12055-12077) builds `<button type="button" role="menuitem">` items with no keydown handling of their own. The only keyboard entry point tied to the picker anywhere in the file is the global Ctrl+M toggle (lines 12162-12171); there is no ArrowUp/ArrowDown/Home/End handling scoped to `#mode-picker`, and the only way to dismiss it besides re-pressing Ctrl+M is a click-outside listener (lines 12154-12160) — there is no Escape-key handler for it. Keyboard/screen-reader users who open the menu therefore have no standard way to navigate between the 9-10 mode items or dismiss the menu with Escape.

**Why it matters:** The mode-switcher dropdown declares `role="menu"`/`menuitem`, which promises assistive-tech users a standard keyboard interaction model — but opening it never moves focus in, and there is no arrow-key, Home/End, or Escape handling scoped to it anywhere in the file. That is a complete gap between the ARIA contract the markup makes and the behavior actually implemented, on a primary, frequently-used navigation control.

> Verifier's own reasoning for the severity correction: "...if a severity tier is required, this qualifies as high — it's a Level A WCAG failure (2.1.1 Keyboard + 4.1.2 Name/Role/Value) on a primary, frequently-used nav control, since role=‘menu’/menuitem promises AT users a keyboard interaction model that is 0% implemented."

## Remaining Confirmed Findings by Area (118 findings)

Grouped by area; within each area, sorted broken/non-functional → degrades-quality →
accessibility-gap → cosmetic-polish, then by line number. Each bullet is intentionally tight —
file:line, a one-sentence summary drawn from the original finding, and its severity — full
evidence quotes are not repeated here (see §4 for that level of detail, or the source audit data
for verbatim quotes on any specific finding). A handful of bullets carry one extra sentence where
the real-world impact is broader than the one-line summary suggests.

### Chat (32)

- **`vps/patches/daveai-production-runtime-20260731/nginx/daveai.tech:179-191`** — The Hermes chat proxy's sub_filter injection of <base href="/hermes/"> silently fails whenever the Open WebUI backend returns a gzip-compressed response, since nothing strips Accept-Encoding or enables gunzip before the filter runs. *(Broken / non-functional)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:350-356`** — A cache hit in llm() returns the cached text directly without ever calling emit() on the SSE queue, so a repeated prompt produces zero streamed output even though llm_fast() enables caching by default. *(Broken / non-functional)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:386-388`** — The Stage-4 fallback call inside llm() omits q/stream_label, so it silently runs as a fully blocking, non-streaming Ollama request instead of the token-by-token streaming _local_direct_call was written to provide. *(Broken / non-functional)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:386-388`** — Unlike Stages 1-3, the Stage-4 call in llm() is not wrapped in a try/except, so any exception _local_direct_call doesn't catch internally crashes the whole llm() call instead of degrading to the friendly _NO_LLM_USER_MSG. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:4294-4504`** — If the SSE reader throws mid-stream after the build-status bar or agent pills were already set to 'working', the catch block never resets them and abandons the partially-filled AI bubble instead of marking it failed. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:4898-4918`** — The visible chat transcript (#chat-feed) is never rehydrated from persisted history on page load, so a refresh silently wipes the visible conversation even though the data still exists in localStorage and in the database. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:6383-6425`** — The Game Mode floating mini-chat never displays a real AI reply: it always shows a hardcoded fake 'Processing...' bubble and then mirrors only an empty string for the actual response. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:6411-6418`** — The '#game-voice-indicator' speaking badge in Game Mode can only ever be switched on, never off by its own mechanism, so it stays visibly active long after DaveAI actually stops talking. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:12867-12872`** — Clicking 'Open' on a chat/session card in the Memory panel claims to resume the prior conversation but only focuses the input box and prints a canned confirmation bubble, with no code anywhere that actually reloads or restores that session's messages. *(Broken / non-functional)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:74-79`** — The ReAct stream filter drops any line starting with "THOUGHT:", "ACTION:", or "OBSERVATION:" unconditionally and with no way to recover it, so ordinary assistant text that happens to start a line with one of those exact words is silently and permanently deleted from the visible chat stream. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:185-210`** — The Stage-1 streaming loop in _litellm_call has no exception handling or partial-text recovery, so a mid-stream failure discards already-emitted SSE tokens while llm() silently regenerates a completely independent answer via Stage 2. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/nginx/daveai.tech:192-194`** — The regex location that catches Open WebUI's root-relative asset requests (_app/static/assets/favicon) proxies to the Hermes backend with no proxy_set_header directives at all, unlike the primary /hermes/ block immediately above it. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:337-388`** — Stage 1 (streaming) and Stage 2 (non-streaming) both reuse the same full caller-supplied timeout (default 300s) against the same model/proxy with no reduction between attempts, so a stalled-but-connected upstream can keep one chat turn in flight for up to twice the configured timeout before the more resilient Stage 3/4 ever run. *(Degrades quality)*
- **`vps/assets/daveai-v6.css:1851-1908`** — #chat-feed's max-height/display are declared with !important in the base rule, forcing roughly 15 later context-specific overrides (has-chat-transcript, workspace-chat-side, app-mode, and the mobile media query) to also use !important just to resize the transcript -- a specificity-fight the base rule itself created. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4096-4233`** — think() has no re-entrancy guard, and its 'cancel the previous stream' line is dead code, so sending two messages quickly runs two concurrent /api/stream requests that both mutate the same singleton UI elements. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4273-4291`** — The /api/stream retry loop re-POSTs the identical chat/build payload with no idempotency key, and its final defensive error check is unreachable dead code. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4589-4598`** — keepTranscriptAnchored force-scrolls #chat-feed to the bottom on every bubble append/update with no check for whether the user has scrolled up to read earlier messages. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4599-4641`** — appendChatBubble() renders bubble text with plain escHtml() while updateChatBubble() renders the same kind of text through md2html(), so any AI bubble populated directly via appendChatBubble (the non-streaming network-fallback reply) shows raw markdown syntax instead of formatted text/code. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4911-5012`** — There is no way to clear or delete chat history from the UI — the History panel only exposes search, export, and copy, and chatHistory is never reset to an empty array anywhere in the file. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4919-4968`** — Typing a query into the History search box and then sending or receiving any chat message silently reverts the History list from filtered back to the full unfiltered list, because two independent render functions write to the same #hist-list element with no shared filter state. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4939-4945`** — replayHistory()/replayHistoryAbs() never actually replay (resend) a past message despite the row's 'Click to replay' tooltip — they only copy the old text into the composer and focus it, requiring the user to press Enter/Send manually. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:5860-5911`** — _initEdgeZones() resets old listeners on the ez-* edge-hover strips by cloning them, but attaches mouseenter/mouseleave listeners straight to the persistent topbar/lsb/rp/chat panels without ever removing prior ones, so duplicate listeners accumulate on the chat dock every time the function re-runs. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:6336-6345`** — gameToggleVoice() calls the async vsSpeakRaw() with no await and no .catch(), so any TTS failure while re-enabling voice in Game Mode surfaces only as a silent unhandled promise rejection. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:7947-8030`** — Overlapping TTS playback requests race on the shared _vsPlaying flag: a stale onended callback from an audio source that was just interrupted can wrongly mark newly-started audio as stopped, killing its waveform animation and hiding the speaking overlay while that audio keeps playing. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:8867-8869`** — On every page load, the saved chat-mode setting unconditionally overwrites the user's independently-set "Narrate: Chat Responses" preference, silently discarding it whenever the active chat mode's voice-out flag is off. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11905-11908`** — Two of classifyMode's auto-mode-switch keyword regexes ('vs.' for research, 'c++' for code) can practically never match real chat messages because their trailing `\b` word-boundary requires a word character immediately after a literal '.' or '+', which normal spacing/punctuation never provides. *(Degrades quality)*
- **`vps/assets/daveai-v6.css:1963-1983`** — The main chat message composer (#pi) has no outline or box-shadow focus indicator; on focus the only visible change is a 1px border going from 7%-opacity white to 40%-opacity purple. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:4925-4967`** — History rows that replay a past message are mouse-only: they carry onclick handlers but no role="button", tabindex, or keyboard handler, so keyboard and screen-reader users cannot use replay at all. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:4006-4037`** — The 1.5-second 'done -> idle' auto-reset in updateAgentUI unconditionally strips the .is-selected outline from a pinned agent pill even though aria-pressed stays true, desyncing the visual selection indicator from the actual selected agent for several seconds. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:5444-5450`** — The client-side speech-recognition scaffold (_speechRec, _hasWebSpeech, _initSpeechRec) is entirely dead code left over from a removed feature, now that voice input is done via server-side MediaRecorder + /api/transcribe. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:5804-5806`** — handleChatKey(e) is a duplicate of chatKeydown(e) (the function actually wired to the chat textarea) that is never attached to any element or called from anywhere in the file. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:9026-9032`** — The voice-bar "speaking" pulse indicator is dead code: vsSpeakRaw is never reassigned to the wrapper meant to trigger it, and the wrapper function itself is never called anywhere in the file. *(Cosmetic / polish)*

### Settings Panel (23)

- **`vps/daveai-ui-v6.html:1938-1952`** — The Admin > Tools tab's per-category tool counts are plain hardcoded <code> text with no id attributes, so unlike sibling counters in the same file they have no hook for JavaScript to ever update them and will always show the same fixed numbers regardless of the real tool registry. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:8033-8036`** — The Voice Blend feature never actually blends two voices; it always silently plays a single hardcoded fallback voice instead, because the composite blend string it builds can never match a real Azure voice ID. Base single-voice TTS is unaffected; only the Blend sub-feature is 100% inert with an undetectable fallback. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:8449-8475`** — Enabling "Moshi Instant Voice" only opens a WebSocket and updates a status label; no code anywhere sends audio to it or plays audio received from it, so the toggle has zero effect on how DaveAI actually speaks. Turning it on emits a false “connected” success signal while doing nothing — deceptive, not just inert. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:9096-9114`** — The "admin-locked" Show File Extensions toggle enforces nothing in code: the checkbox is never actually disabled, and the flag meant to let an admin unlock it for a normal user is never written anywhere in the file, so the lock can be bypassed and can also never be legitimately lifted. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:9591-9600`** — The "Long-form responses" and "Enable Memory / Learning" toggles in Settings can never actually be turned off because _savePersonality() falls back to true instead of the checkbox's real unchecked value. The forced-`true` fallback also leaks into `buildPersonalityPrompt()` and the memory-write gate, so the AI's actual prompt content and conversation-memory persistence cannot be turned off by the user at all. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:9814-9815`** — Once a custom LM Studio model name has been typed, choosing a different preset from the "Chat / Story Model" dropdown is silently ignored because the stale custom value keeps taking precedence. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:10149-10156`** — The Settings "Refresh Now" button gets stuck reading "Refreshing..." forever if the refresh chain throws or rejects, because _manualRefreshProjects() chains .then() with no .catch()/.finally(). *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:11313-11381`** — The Icon/Theme Studio's icon-pack switcher changes only internal state; the selected pack's stylesheet is never loaded and no icon classes are ever remapped anywhere in the file, so choosing any pack besides Stock can never visibly change a single icon. 11 icon packs are offered in the picker; choosing any of them beyond Stock has zero visible effect anywhere in the app. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:6428-6501`** — Clearing the admin showcase demo leaves stale custom title/subtitle text in the settings form, which then gets silently reapplied to the next, different project the admin picks. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:7781-7795`** — vsTestVoice reports "Playback complete" even when voice output is muted and no audio was actually generated or played. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:7797-7801`** — vsTestTuned (and the same pattern in vsQuickPreview) discards every TTS error in an empty catch block, so the Tuning tab's Test control gives zero feedback of any kind when playback fails. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:8331-8335`** — vsPreviewPreset calls the async vsSpeakRaw() with neither await nor a .catch(), so any TTS failure becomes an unhandled promise rejection with no feedback on the built-in preset's Preview button. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:9797-9806`** — The Local Voice Engine settings are hardcoded to fixed values on every read and write, silently discarding any stored configuration, and the corresponding <select> offers only one option so it can never actually be changed. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11264-11280`** — FX visual-effect classes (hover lift, shimmer, spark border) are applied via a one-shot querySelectorAll pass and never reapplied later, so .vs-voice-card elements - which are only created afterward when Voice Studio is opened - never receive them even though the corresponding settings default to ON. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11359-11381`** — Each icon-pack selection schedules its own 30-second safe-mode revert timer that is never stored or cancelled, and the deferred revert never checks whether its packId is still the active selection, so switching packs more than once within 30 seconds causes a stale confirm() dialog to silently revert the user's later choice back to stock and mislabel an unrelated pack as broken. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11855-11870`** — The waveform-color, waveform-type, and icon-studio grids are populated exactly once via a hardcoded 1.5-second setTimeout after page load, and are never re-rendered when their own panel is opened, so opening that panel before the timer fires shows empty grids. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:355-715`** — Descriptive <label> text preceding selects/inputs throughout the Settings modal (e.g. 'Select project to showcase', 'Personality Style', 'LM Studio URL') is never linked to its control via a for/id pair, so the relationship is only visual/positional, not programmatic. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:1904-1917`** — The Admin > Users '+ New User' form has no <label> elements at all for its Email, Display Name, Password, or Role fields, relying entirely on placeholder text that disappears on input and is not a substitute for a programmatic label. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:7747-7757`** — Voice Studio's voice-grid cards are marked role="option" with their own tabindex="0" but each also contains a separately-tabbable native <button>, breaking the listbox/option keyboard pattern where the option itself (not a nested control) should be the sole focus target. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:11003-11011`** — The waveform color/type and icon-pack pickers render individual role="radio"/role="option" items with per-item tabindex="0" but no radiogroup/listbox container role, no accessible group name, and no arrow-key navigation, so keyboard and screen-reader users get 44+ ungrouped, individually-tabbable items instead of a standard radio group. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:222-227`** — The Settings overlay is the only major modal in this range with no click-outside-to-close handler on its backdrop, forcing users to find the small X button while every other non-auth modal supports dismissing by clicking outside. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:7660`** — The Voice Studio state variable `_vsAzureOnlyVoiceCache` is declared but never read or written anywhere else in the file, leftover dead state from a removed feature. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:9945-9952`** — _testLocalVoice() and _localVoiceSpeak() are dead code, defined but never invoked or wired to any button anywhere in the file. *(Cosmetic / polish)*

### Menu & Navigation (20)

- **`vps/daveai-sites-config.json:25-35`** — The daveai-api catalog entry documents api.daveai.tech as the 'Agent Brain API gateway' on port 8888, but the live nginx vhost for that hostname actually proxies everything to the unrelated Stories/Supabase backend on port 18000. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:2008-2105`** — Every mode-pane stub screen (Web/Code Agent/Research/Problem Solver/Hermes Team, reachable by any signed-in user via the mode picker) links to internal roadmap/status markdown files that do not exist anywhere in the repository under those names, so the links dead-end. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:3024-3029`** — updateSbActive() maps the Tools/Agents/Skills flyout tabs to sidebar-button indices that are off by one, so the active-state highlight always lights up the wrong rail icon for those three tabs. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:3534-3628`** — The fallback command-palette implementation built from _CMD_PALETTE_ITEMS is entirely dead code because _openCmdPalette() always delegates to the real openCommandPalette() and returns before any of its own code runs. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:3557-3618`** — The Ctrl+K command palette implementation in this range (_openCmdPalette, _cmdPaletteKey, _CMD_PALETTE_ITEMS and its helpers) is permanently unreachable dead code because _openCmdPalette immediately delegates to a separate, later-defined openCommandPalette() and returns. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:3643-3654`** — The keyboard-shortcuts help panel advertises 10 shortcuts, but 6 of them (Ctrl+., Ctrl+Shift+P, Ctrl+Shift+T, Ctrl+Shift+D, Ctrl+B, Ctrl+\\) are wired to no handler anywhere in the file, and 'Ctrl + Enter' is mislabeled. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:12032`** — The mode-switcher's pane router maps 'code' mode to the Files pane instead of the fully-built dedicated 'Code Agent Mode' panel, so that panel is permanently unreachable from anywhere in the app. *(Broken / non-functional)*
- **`vps/daveai-sites-config.json:113-123`** — The daveai-docs entry sets "category": "docs", a key that does not exist anywhere in this file's categories map. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:182-202`** — On the very first splash screen every visitor sees, the Desktop, Tablet, and Mobile device-choice cards all carry an identical 'RECOMMENDED' badge, which defeats the purpose of a recommendation and reads as a copy-paste content error. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:2968-2998`** — Closing the fly-out panel via togglePp's own toggle-close branch skips the pull-tab/timer cleanup that closePp() performs, leaving the auto-hide pull-tab stuck hidden and its 3-minute interval running after the panel is already closed. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11827-11870`** — App Mode restoration from a previous session is gated behind the same arbitrary 1.5-second page-load timer instead of running immediately, so a user who left App Mode on sees the ordinary (non-streamlined) layout for up to 1.5 seconds on every load before it switches. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11844-11850`** — The App Mode keydown listener turns App Mode off on any Escape press with no check on focus or on whether a modal is open, and it coexists with a separate independent document-level Escape handler that closes the tool modal/layout picker/settings panel, so dismissing a dialog with Escape while App Mode is active also unintentionally exits App Mode. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11905-11908`** — classifyMode's keyword regexes for 'vs.' and 'c++' are wrapped in \b(...)\b, but since both alternatives end in punctuation, the trailing \b only matches when followed immediately by a word character, so these two keywords can never trigger their mode switch in normal phrasing (followed by a space, punctuation, or end of message). *(Degrades quality)*
- **`vps/daveai-ui-v6.html:12040-12042`** — The Files/Code pane's 'already loaded' cache guard tests `window._filesTreeData`, a property nothing ever sets, so the guard is always false and the project file tree is refetched from the backend on every single mode switch. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:12202-12236`** — The newer Ctrl+P command palette's action catalog replaced the older Ctrl+K palette but omits more than a dozen of its commands, which are now unreachable from any command palette because the old palette unconditionally defers to the new one. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:122-163`** — Every button in the floating App Mode toolbar is icon-only with only a title attribute (no aria-label), and the toggle buttons among them (mute, autoread, status bar, voice bar, chat) expose their on/off state solely via a visual .on CSS class with no aria-pressed, so assistive tech gets little to no indication of what each control does or whether it is active. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:1435-1667`** — The side-panel's fp-tabs (Projects/Pages/Sites/Tools/Agents/DB/Skills) are correctly marked role="tablist"/role="tab" with aria-controls pointing at each fp-body panel, but none of those panels ever receives role="tabpanel" or aria-labelledby, breaking the ARIA tabs relationship for screen-reader users. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:1674-1680`** — The canvas toolbar's Preview/Code tabs use role="tab" on each item but their container has no role="tablist" and neither tab has an aria-controls pointing at the panel it switches, so the relationship is entirely unexposed to assistive tech. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:3633-3671`** — The keyboard-shortcuts dialog (role=dialog, aria-modal=true) is not wired into the app's global Escape-to-close handler and never moves focus into itself on open, unlike every other modal in the file. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:12254-12269`** — The command palette (and the slash-command dropdown) renders `role="option"` suggestion items with no `listbox` container role and no `aria-activedescendant` link back to the text input, so screen readers cannot perceive which suggestion is highlighted while the user types. *(Accessibility gap)*

### Other (14)

- **`vps/daveai-ui-v6.html:12860-12866`** — Opening a saved project from the Memory panel never marks it as the app's selected project, and when no explicit deploy metadata exists it hardcodes the top-level production marketing URL as that project's preview target. Any VPS project lacking `deploy_url` metadata (confirmed to be all of them) gets its preview silently pointed at the production marketing homepage instead of its own deployment — a wrong-content bug, not just a missing convenience. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:1832-1865`** — The Analytics panel, right-panel stat tiles, Admin Agents tab, and the default chat 'thinking' bubble all ship with specific, confident-looking fabricated numbers and a fake Supervisor/Coder/QA exchange baked directly into markup instead of neutral loading placeholders, inconsistent with the honest 'connecting…'/'loading…' states used elsewhere for the same data. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:2348`** — curToolRole and toolSearch are dead globals meant for the Tools panel's role filter and search query, declared once and never read or written again anywhere in the file. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:3358-3367`** — renderTools()'s search filter lowercases the query and the tool description but not the tool name, so a search term that would only match a tool's name by case is silently missed. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:10855-10874`** — The admin dashboard's VPS system-info and PM2 service rows are concatenated into innerHTML without escaping, inconsistent with the 'Online Users' rows a few lines later which do escape the equivalent fields, creating an avoidable injection path if any backend-reported OS/kernel/service-name string ever contains markup. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:11117-11130`** — The Spectrum waveform visualization's per-color hue offset always evaluates to 0 because parseFloat cannot parse a '0x'-prefixed hex literal, so the selected neon color never actually influences the rendered spectrum colors as intended. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:12815-12825`** — _loadMemoryImpl's only re-entrancy guard is a 4-second time throttle that is completely skipped for forced calls, so a manual 'Refresh memory' click overlapping the 30-second auto-poll (or two quick Refresh clicks) fires concurrent fetches whose responses can resolve out of order and clobber each other's render. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:12910-12914`** — The Memory panel's periodic auto-refresh interval is destroyed the first time the browser tab is hidden and nothing ever restarts it when the tab becomes visible again, so live auto-refresh permanently stops for the rest of the session. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:3633-3675`** — The keyboard-shortcuts help dialog opened by pressing '?' never moves focus into itself and is not wired to any Escape handler, contradicting the dialog's own listed 'Esc: Close modals / panels' shortcut. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:5082-5114`** — The Activity Center feed (#af) is rewritten via innerHTML on every new agent event with no aria-live/role="log" anywhere, so screen-reader users get no notification of new activity, build, or error events as they stream in. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:10564-10571`** — The Profile modal (role="dialog" aria-modal="true") cannot be dismissed with the Escape key and never receives initial keyboard focus, unlike every other modal handled by the app's global key handler. *(Accessibility gap)*
- **`vps/daveai-ui-v6.html:5093-5096`** — The per-event-type emoji lookup in renderActivityCenter is dead: every entry in typeEmoji is an empty string so the computed emoji always falls back to the same default, and the resulting variable is never even used in the rendered card. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:5953`** — _demoIdleTimer is declared and cleared on chat-input focus but is never assigned a real timer anywhere in the file, so that clearTimeout call is a permanent no-op left over from an unfinished 'auto-restore demo after idle' feature. *(Cosmetic / polish)*
- **`vps/daveai-ui-v6.html:10966-10969`** — _dvGetWfGlow is defined but never called anywhere else in the file - dead code. *(Cosmetic / polish)*

### CSS (10)

- **`vps/daveai-ui-v6.html:16-20`** — The patch rule meant to recolor 'down'/unknown site-status indicators to orange never fires because its selector keys off an inline style substring ('#b2bec3') that occurs nowhere else in the 12,920-line file, making it permanently dead code. *(Broken / non-functional)*
- **`vps/assets/daveai-v6.css:2916-2965`** — The desktop 'chat beside canvas' workspace layout (built with CSS Grid) is silently defeated whenever a Tablet/Android/Mobile device-mode preview is simultaneously active, because later rules force #canvas back into a vertical flex column and reset the children's grid placement. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:15`** — The account dropdown's position is force-overridden to a fixed 68px top offset that does not match the topbar's actual height in any of its defined states, so the menu renders visually detached from the avatar button that opens it. *(Degrades quality)*
- **`vps/assets/daveai-v6.css:3943-4238`** — `.demo-btn-play` and `.dev-choice.recommended` are each declared in two separate, non-adjacent rule blocks hundreds of lines apart, splitting one component's styling across the file. *(Degrades quality)*
- **`vps/assets/daveai-v6.css:25`** — The --t3 secondary-text color token (#475569) contrasts at only ~2.65:1 against the app's near-black backgrounds, failing WCAG AA's 4.5:1 minimum for normal text, and it is reused for dozens of small labels/meta/timestamp elements throughout the file. Reused roughly 78 times across labels, timestamps, and meta text throughout the file — a systemic design-token defect, not a one-off typo. *(Accessibility gap)*
- **`vps/assets/daveai-v6.css:2313-2325`** — Icon-only close buttons such as `.rp-close` (22x22px) and `.tm-close` (~18x18px) fall well under the 44x44px minimum the stylesheet itself defines as the standard for interactive controls elsewhere. *(Accessibility gap)*
- **`vps/assets/daveai-v6.css:2327-2332`** — Several dismiss/close controls set `outline: none` on `:focus-visible` with only a faint background or border tint as a substitute, and the Command Palette's own text input has no focus style at all. *(Accessibility gap)*
- **`vps/assets/daveai-v6.css:3996-4003`** — `.demo-meta` text is rendered at 20% white opacity over a near-black background, producing roughly 1.7:1 contrast, i.e. effectively unreadable rather than merely de-emphasized. At ~1.7:1 contrast this text is effectively unreadable, not merely de-emphasized, and it is genuine user-facing status content on the public demo overlay. *(Accessibility gap)*
- **`vps/assets/daveai-v6.css:6727-6895`** — `#tb-clock { display: none !important; }` and `#sb-wrap { display: none !important; }` are each re-declared identically inside multiple nested max-width breakpoints, where the narrower ones are dead code because the widest breakpoint already covers them. *(Cosmetic / polish)*
- **`vps/assets/daveai-v6.css:7238-7241`** — At the <=380px breakpoint, #topbar's height is hardcoded to 36px, but the --topbar-h custom property it otherwise mirrors is never updated for that breakpoint and stays at 40px. *(Cosmetic / polish)*

### Backend (8)

- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:180-210`** — _litellm_call's return value is built from the raw, un-filtered token stream rather than the ReAct-cleaned text actually shown to the user, so anything that persists or re-displays llm()'s return value can reintroduce the THOUGHT:/ACTION:/OBSERVATION:/FINAL: scaffolding the filter exists to hide. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:402-415`** — llm_json's extraction requires the JSON blob to run to the exact end of the model's output, so any trailing prose after a well-formed JSON value (a common LLM habit) makes json.loads raise and silently falls back to {"raw": raw} instead of the parsed object. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:4798-4848`** — The code's own comment claims BrainState/pollBrain replaced the polling race between updateStatusBar, fetchAgents, fetchStats and checkApiHealth, but all four remain independently scheduled and still hit overlapping endpoints, including the very /api/health call pollBrain is supposed to own exclusively. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:5256-5286`** — Opening the Admin 'Logs' tab starts a 5-second setInterval log-polling loop that is never stopped anywhere in the file, so it keeps hitting the backend every 5 seconds for the rest of the page session even after the admin leaves the tab. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:10636-10650`** — _dbFetch() constructs its request options so that a caller-supplied opts.headers would silently replace, rather than merge with, the computed Content-Type/auth headers, because the ...opts spread is placed after the headers key. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:10666-10689`** — _dbSyncUser looks up and creates the Postgres user record keyed on the display name (_currentUser.name) instead of a stable unique id, so two different accounts that end up with the same display name silently collide on one database user record. The collision causes real cross-account data misattribution — one user's chat/session writes can get silently attributed to a different authenticated user's Postgres record whenever display names coincide. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:15`** — VISION is imported from brain_core but never referenced anywhere else in this file, so the vision-model stage described in the module docstring ("heavy-coder / fast-agent / vision") is not actually wired into any function here. *(Cosmetic / polish)*
- **`vps/patches/daveai-production-runtime-20260731/brain_llm.py:48-103`** — _seen_any_final is written in three places on _ReActStreamFilter but never read anywhere in the file, so whatever check it was meant to support (e.g. detecting a model that never produced a FINAL: marker) was never actually implemented. *(Cosmetic / polish)*

### Infra (6)

- **`vps/verify-production-route-truth.cjs:32-57`** — For a status:'live' site whose initial response is a redirect, the script follows the redirect and passes the check on any final 200 response anywhere, so a live site that regresses into being gated behind the SSO login wall (which itself returns 200) is reported as passing instead of failing. *(Broken / non-functional)*
- **`vps/patches/daveai-production-runtime-20260731/nginx/daveai.tech:5-7`** — The comment documenting the API rate limit (10 req/s per IP) does not match the actual configured zone rate (80 req/s), an 8x discrepancy. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/nginx/voice.daveai.tech:48-55`** — The @cors_preflight named location is defined with the correct CORS headers and a 204 response but is never referenced anywhere else in the file, so it can never actually run. *(Degrades quality)*
- **`vps/patches/daveai-production-runtime-20260731/nginx/stories.daveai.tech:119-123`** — The public health endpoint for api.daveai.tech returns a hardcoded static 200 response instead of proxying to and reflecting any real backend, so it can never actually detect an outage. It is the one automated liveness check for `api.daveai.tech`; per the repo's own design doc it should reflect real backend status, so a full backend outage would currently be reported as 100% healthy. *(Degrades quality)*
- **`vps/verify-source-of-truth.py:129-133`** — The exact site count (22) and live/auth split (14/8) are hardcoded here and independently re-hardcoded again in verify-production-route-truth.cjs, so the two 'source of truth' gates can silently disagree if only one file is updated when a site is added, removed, or re-statused. *(Degrades quality)*
- **`vps/verify-source-of-truth.py:144-151`** — Two require() checks index by_domain[...] directly instead of using .get() like the rest of the script, so removing or renaming 'api.daveai.tech' or 'monitor.daveai.tech' in the sites config crashes the verifier with an unhandled KeyError instead of the intended clean SystemExit failure message. *(Degrades quality)*

### Auth & Session (5)

- **`vps/patches/daveai-production-runtime-20260731/nginx/iptv.daveai.tech:110-128`** — Every provider-vault endpoint except the one exact-matched '/providers' path returns an HTML redirect to the SSO login page on session expiry instead of a JSON error, breaking client-side response.json() handling for what are almost certainly XHR/fetch calls. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:10618-10622`** — The Admin Dashboard widget only ever gets started from the page-load DOMContentLoaded handler based on the role captured at that instant, so an admin who authenticates during the session (rather than already holding a valid token when the page loaded) never sees it appear. *(Broken / non-functional)*
- **`vps/daveai-ui-v6.html:2423-2536`** — The legacy /api/admin/login fallback that runs when /api/auth/login fails is gated by a single hardcoded personal email address in client-side JS, so it silently never applies for any other admin account or if that address ever changes. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:10429-10449`** — Saving the profile can report "Profile saved!" implying the server was updated even when no server request was ever made, because serverSaved defaults to true and is only set false on a thrown error, never when the request is simply skipped. *(Degrades quality)*
- **`vps/daveai-ui-v6.html:5155-5157`** — The admin panel's local _authHeaders() duplicates the existing global authHeaders() but always sends an Authorization header (even 'Bearer ' with an empty token when logged out) instead of correctly omitting it like the shared helper does. *(Cosmetic / polish)*

## Rejected Candidates (3)

These 3 candidates did not survive independent re-verification against the live file — included
here for the audit trail, not as open issues.

### R1. `vps/daveai-ui-v6.html:1272-1278` (originally rated Accessibility gap)

**Candidate claim:** The topbar mode badge has a static aria-label ('Current mode') that, per accessible-name computation rules, completely replaces its visible child text for assistive tech, so screen-reader users are never told which mode (Build/Chat/Research/etc.) is actually selected.

**Why it was rejected:** The finding claimed the topbar mode badge and workspace-layout control have a *static* `aria-label` that permanently masks their visible text from screen readers. Verification found `setMode()` and `applyWorkspaceLayout()` both update `aria-label` together with the visible text on every change **and** on initial page load via `DOMContentLoaded`, so the accessible name tracks the real mode/layout by the time the page is interactive — the claimed defect does not occur in the live file.

### R2. `vps/assets/daveai-v6.css:1545-1552` (originally rated Accessibility gap)

**Candidate claim:** The canvas/empty-state hero subtitle text color (#4E6070) contrasts at only ~3.0:1 against its background, failing WCAG AA (4.5:1) for its 13-16px body-text size.

**Why it was rejected:** The finding claimed `.p-sub`'s low-contrast color (#4E6070, ~3.0:1) is the rendered canvas/empty-state hero subtitle. Verification found `.p-sub` and its sibling selectors are dead, orphaned CSS never referenced anywhere in the actual markup (`grep` for the class returns zero hits in the HTML); the element that actually renders in that spot (`.demo-sub`) uses a different color with a different, smaller contrast gap not covered by this finding as written.

### R3. `vps/daveai-sites-config.json:223-233` (originally rated Degrades quality)

**Candidate claim:** The daveai-game entry is marked status 'auth' (a real, deployed, login-gated destination in this schema) even though its own description says the game server is '(coming soon)', and no game.daveai.tech nginx vhost exists anywhere in the repository.

**Why it was rejected:** The finding claimed the `daveai-game` catalog entry's `status: "auth"` contradicts its own “(coming soon)” description and that the site isn't really deployed. Verification found a real production HTTP probe recorded in this repo (`proofs/daveai-prod-audit-20260731/14-catalog-http-audit-v2.json`) showing `game.daveai.tech` live and correctly redirecting to the Authelia login wall, plus an enforced regression test (`verify-source-of-truth.py`) that deliberately requires this domain to be status `auth` — the entry is working as designed, not a defect.

