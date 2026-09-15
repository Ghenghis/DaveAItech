# DaveAI.tech Contract Kit — 2026-09-15

## 0. What this is

This is the operational layer that sits on top of `docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`.
The roadmap doc is the **authority on phase scope** — it defines six phases (0 through 5) based on
a live, multi-agent audit of daveai.tech, and nothing in this kit adds, removes, renames, or
reorders those phases. What the roadmap doc does not fully specify is *how* an agent picking up
one phase's work should behave so that quality and honesty stay consistent no matter which tool
does the work — Devin, Kilocode, Codex, a future Claude session, or a human. That's what this kit
adds: one JSON **contract** per phase, plus an index, plus this explanation of the rules every
contract shares.

This kit exists because of a documented, real failure mode, not a hypothetical one. The roadmap
doc records that a fix already shipped to production (replacing a broken "Checkers Crowning Draft"
game page) was never reflected back into this repository — so redeploying the repo's own catalog
file as-is would have silently undone a real fix. That happened because there was no shared
discipline around scope, evidence, and honest status reporting across whoever touched the code.
This kit is the fix for that gap at the process level, the same way Phase 0 is the fix for it at
the data level.

## 1. Files in this kit

| File | Purpose |
| --- | --- |
| `docs/DAVEAI_CONTRACT_KIT_20260915.md` | This document — how to use the kit, and the rules every contract shares. |
| `docs/contracts/CT-INDEX.json` | Machine-readable index of all six contracts: id, title, phase, status, dependency order. Start here to find which contract applies. |
| `docs/contracts/CT-000-stop-the-bleeding.json` | Phase 0 — repo/production drift fixes + the unauthenticated admin panel. |
| `docs/contracts/CT-001-chat-completion.json` | Phase 1 — line-by-line audit/fix pass on the real chat stack. |
| `docs/contracts/CT-002-menu-nav-polish.json` | Phase 2 — topbar/sidebar/settings polish + accessibility pass. |
| `docs/contracts/CT-003-games-catalog-consolidation.json` | Phase 3 — collapse the five-places-at-once catalog into one source. |
| `docs/contracts/CT-004-wildcard-extensibility.json` | Phase 4 — wire up the "other" category as the external-site launcher. |
| `docs/contracts/CT-005-strategic-decisions.json` | Phase 5 — standing decision register, not an implementation contract. |

Each `CT-0XX-*.json` file is designed to be **self-contained**: reading that one file plus the
exact scope files it names should be enough to start real work safely, without needing this
overview, the roadmap doc, or any other contract open at the same time — though reading the
roadmap doc first is still required by every contract's own `steps` list, because a contract is a
work order derived from the roadmap, not a replacement for reading it.

As of 2026-09-15, **all six contracts are `not_started`**. No phase-0/1 work has begun. Nothing in
this kit should be read as authorization to start — see §7 on the standing go/no-go gate.

## 2. How to use this kit (for any agent, cold)

1. Read `docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` in full. It is the authority on *what* needs
   doing and *why*; this kit only governs *how*.
2. Open `docs/contracts/CT-INDEX.json`. Find the contract matching the work you've been asked to
   do, and check its `depends_on` list — if an earlier contract isn't done, stop and say so rather
   than starting out of order (see §6 on why this matters for this specific codebase).
3. Read that one `CT-0XX-*.json` file in full — every field, not just `scope` and `steps`.
4. Read exactly the files named in its `scope.files` — nothing more, nothing less, unless your own
   investigation during the work turns up a genuine need to look further (in which case, expand
   your *reading*, not your *editing*, and say so in your report).
5. Do the work described in `steps`, respecting `protected_paths` absolutely.
6. Collect every item in `required_evidence` as you go — not retroactively from memory afterward.
7. Before writing a single word of a completion report, check every line of `definition_of_done`
   against the evidence you actually collected. A checklist item is only checked if you can point
   at the evidence for it.
8. Write your completion report following `reporting_requirements`, using the `status_discipline`
   labeling (verified vs. reported) on every factual claim, and never using a phrase from
   `forbidden_claim_patterns` without the exact proof command + output quoted immediately next to
   it.
9. Only then may the contract's `status` move off `not_started` — and only with the evidence
   attached under `evidence_location`.

## 3. Standing rules — apply to every contract, regardless of phase

These come directly from the table at the bottom of `docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md`
("Contract kit (per-phase, for whichever agent picks up the work)"). Every `CT-0XX-*.json` file
encodes all five as concrete, phase-specific fields — this section explains the rule behind each
field so it isn't followed as boilerplate.

### 3.1 Scope: exact, not vague

> "Exact file(s)/line ranges, stated explicitly — not 'the chat,' `vps/daveai-ui-v6.html` lines X–Y"

Every contract's `scope.files` array names concrete paths. Where a line range has already been
independently verified (via a direct read or grep during this kit's preparation), it's stated with
the exact numbers and how it was confirmed. Where the deep-audit workflow hasn't pinned a range
down yet, the contract says so explicitly:

> "line range pending deep-audit workflow completion — see docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md"

**Never replace that sentence with an invented line range.** If you narrow it down yourself while
working, record the real range you found and how you found it (grep output, direct read) — that
becomes part of your evidence, not a free-standing assertion.

### 3.2 Protected paths: nothing outside scope, silently

> "Nothing outside scope touched without saying so"

Every contract's `protected_paths` array names the files/sections reserved for *other* contracts —
usually because another phase owns them, or because they're confirmed to be unrelated to
daveai.tech entirely (`app/`, this repo's stock bolt.diy chat app, is protected in every single
contract for this reason). If your work under one contract genuinely requires touching a protected
path, that is a stop-and-flag moment, not a judgment call to make silently — say so explicitly in
your report, with a reason, rather than expanding scope quietly.

### 3.3 Required evidence: exact command + output, not narrative

> "Exact command + output for any 'fixed' claim (a proof script, a curl, a screenshot) — not
> narrative confidence"

Every contract's `required_evidence` array is a literal list of what must exist before a claim can
be made — a specific curl against a specific health endpoint, a before/after diff, a screen-reader
transcript, a forced-failure reproduction. "I reviewed the code and it looks correct" is never
sufficient on its own. This project already has a working example of the evidence discipline this
kit expects: `proofs/daveai-prod-audit-20260731/` contains dozens of dated screenshots and JSON
proof artifacts from a prior audit pass (before/after auth-gate screenshots, catalog HTTP audits,
per-game smoke-test JSON, health-endpoint captures). Follow that pattern — a timestamped
`proofs/<phase-slug>-<YYYYMMDD>/` directory per contract, named in that contract's
`evidence_location` field.

### 3.4 Forbidden claims: no absolute language without proof attached

> "No '100% complete,' 'everything works,' 'production-ready,' 'no bugs remain' without the proof
> line right next to it"

Every contract carries the identical `forbidden_claim_patterns` array, written as regex-friendly
strings so tooling can grep a completion report for them automatically:

```json
[
  "100%\\s*complete",
  "everything\\s+(is\\s+)?(fixed|working)",
  "no\\s+bugs?\\s+remain",
  "release-ready",
  "production-ready",
  "perfect"
]
```

This is not about banning confidence — it's about banning *unearned* confidence on a codebase this
size (`vps/daveai-ui-v6.html` alone is 12,920 hand-written lines with no build pipeline and no CI
gate on production deploys). A 133-candidate-finding audit with a majority independently confirmed
real, and the rest still pending re-verification, is not a codebase where "everything works" is
ever a safe sentence without an itemized list of exactly what was checked sitting right next to it.

### 3.5 Definition of done: checked off before, not after, declaring done

> "Stated per-phase before starting, checked off with evidence, not assumed"

Every contract's `definition_of_done` is a checklist of unchecked `[ ]` items. The discipline is
directional: read the checklist *before* starting work (so you know what "done" actually requires
for this phase), and check items off only *after* you have the evidence for them — never mark a
box because the work is finished in your judgment; mark it because a specific piece of evidence
listed in `required_evidence` now exists to back it.

### 3.6 The verified/reported distinction

Every contract also carries an identical `status_discipline` block, because it underlies all five
rules above:

- **verified** — you personally read the code, ran the command, or fetched the live response
  yourself, and can quote the exact evidence.
- **reported** — a document or another agent's proof artifact says so, and you have not
  independently re-checked it today.
- **Rule:** never upgrade a "reported" fact to a "verified" claim without re-checking it yourself.

Label every factual claim in your completion report as one or the other. This kit's own
preparation followed this same rule — see §5 below for exactly what was independently verified
while writing these contracts versus what remains only reported.

## 4. The three findings called out for explicit severity escalation

The roadmap doc's own findings sections (§4.1–§4.4) predate a follow-up section-by-section bug
audit of the live production source. That follow-up audit's independent verifiers flagged three
specific findings as **understated** in severity relative to how the original audit categorized
them. Rather than inventing a seventh, standalone security/accessibility contract — which would
contradict the roadmap doc's explicit six-phase structure — each finding was placed as an explicit,
named `known_findings` entry inside the phase contract that already owns the relevant file section,
so it cannot be missed or silently deprioritized by whoever picks up that phase:

| Finding | Severity | Contract | Status as of 2026-09-15 |
| --- | --- | --- | --- |
| **F-P1-01** — the AI-generated content preview iframe sets `sandbox="allow-scripts allow-same-origin allow-forms allow-popups"`. Combining `allow-scripts` with `allow-same-origin` is a well-known sandbox escape — the very risk a comment directly above the element already names, while the attribute value contradicts the comment's own claim of using `allow-scripts` alone. | critical (security) | `CT-001` (Phase 1, chat completion) | Verified directly at `vps/daveai-ui-v6.html:1808-1812` during this kit's preparation. Not yet fixed. |
| **F-P0-05** — an unauthenticated admin panel leaks internal infrastructure details, including the raw VPS IP and internal service ports, with no role or auth check. | critical (security) | `CT-000` (Phase 0, stop the bleeding) | Confirmed real by the follow-up audit. This kit's preparation independently corroborated a related lead (an `/api/admin/login` nginx route with no matching handler in this repo's copy of `brain_llm.py`) but did not reproduce the leak itself — the exact panel URL and mechanism still need to be located directly on the live VPS. Not yet fixed. |
| **F-P2-01 / F-P2-02** — the primary sign-in form, and the entire Settings modal (~23 toggles), lack accessible names for screen readers. Independent verifiers flagged this as a **WCAG Level A failure that blocks screen-reader users from the app entirely** — not a minor polish gap. | high (accessibility, escalated) | `CT-002` (Phase 2, menu/nav polish) | Confirmed by the follow-up audit; corroborated by a direct grep during this kit's preparation showing bare, unlabeled `<input type="checkbox">` settings toggles starting at `vps/daveai-ui-v6.html:267`. Not yet fixed. |

Why these three landed where they did, rather than in a dedicated contract: `F-P1-01` is chat-surface
markup that CT-001 already owns line-by-line; `F-P0-05` is an urgent, narrowly-scoped lockdown that
fits Phase 0's own "stop the bleeding, do first" character better than waiting behind Phases 1-3;
and `F-P2-01`/`F-P2-02` are exactly the accessibility pass Phase 2 already commits to doing, on the
same file section it already owns. Splitting them into a seventh contract would have meant either
duplicating file ownership across two contracts touching the same lines, or asking one team to wait
on another for no structural reason. Each contract's `known_findings` entry for these three carries
its own severity, confirmation status, and exact evidence — treat those entries as binding scope,
not optional nice-to-haves, precisely because independent verifiers escalated them.

## 5. What was — and wasn't — independently re-verified while building this kit

In keeping with the status-discipline rule this kit imposes on everyone else, here is what this
kit's own preparation actually checked directly on 2026-09-15, versus what it carried forward as
"reported" from the roadmap doc or the owner-provided follow-up audit summary:

**Verified directly** (read the file or ran the command): every source file's total line count
(`vps/daveai-ui-v6.html` = 12,920; `vps/daveai-project-catalog.json` = 61; `brain_llm.py` = 430;
`vps/daveai-sites-config.json` = 257; `vps/production-e2e-runner.cjs` = 262;
`vps/DAVEAI_SOURCE_OF_TRUTH.md` = 62); the iframe sandbox attribute at
`vps/daveai-ui-v6.html:1808-1812`; the `data-cat="other"` filter button at line 1461;
`PROJECT_CATALOG_HOST_STATUS` at line 9124 and `seedProjects()` at line 9338 (called at 9559 and
10087); the two Checkers catalog entries at lines 39 and 43 of the project catalog; the hardcoded
`== 55` assertions at `vps/verify-source-of-truth.py:155` and `:157`; the `/api/admin/login` nginx
route around line 209-212 of the production nginx config; the confirmed absence of any
case-insensitive `admin` match anywhere in this repo's copy of `brain_llm.py`; and the settings
checkboxes beginning at `vps/daveai-ui-v6.html:267`. `vps/DAVEAI_SOURCE_OF_TRUTH.md` was read in
full and independently confirms the false byte-identical invariant the roadmap doc describes
(line 17: "`daveai-ui-v6.html` must remain byte-for-byte identical to the copy in the Agent Brain
runtime bundle").

**Carried forward as reported, not independently re-verified**: the exact 64-line production diff
figure; the three-way SHA-256 mismatch; the precise mechanism and URL of the admin-panel leak
itself (F-P0-05); the full 133/confirmed/pending finding counts (re-check
`docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` directly for the current number, since it may have
moved since this kit was written); the `seedProjects()` ID-mismatch claim; and the daveai-v7
functionality-gap reconciliation (F-P1-02) beyond what `docs/DAVEAI_ARCHITECTURE_MAP_20260915.md`
§6.2 already documents.

Whoever picks up a contract should re-verify anything they rely on rather than trusting this
section indefinitely — "verified on 2026-09-15" ages out the moment another contract lands changes
on the same file.

## 6. Why phase order matters here specifically

`vps/daveai-ui-v6.html` is one 12,920-line hand-written file with **no build pipeline** — changes
are installed by hand-running shell scripts straight onto the production VPS. Four of the six
contracts (`CT-000`, `CT-001`, `CT-002`, `CT-003`) all touch this same physical file, in different,
supposedly non-overlapping sections. `CT-004` touches it too, plus whatever catalog file `CT-003`
produces. This creates a real hazard that doesn't exist in a normal multi-module codebase: a line
number verified accurate today can go stale the moment an earlier contract's changes are merged.

That is why every contract in this kit states explicit `depends_on` relationships
(`CT-INDEX.json` repeats them for quick lookup), and why several contracts' `cross_phase_notes`
say, in effect, "confirm the earlier contract actually landed before you trust your own line
numbers." Follow that literally. Do not start `CT-001` against a copy of `vps/daveai-ui-v6.html`
that `CT-000` hasn't yet synced to production, and do not start `CT-002` while `CT-001`'s changes to
the same file are still uncommitted.

`CT-005` is the one exception to strict sequencing — it's a standing decision register (see
`docs/contracts/CT-005-strategic-decisions.json`), not an implementation contract, and some of its
five questions (`Q1`-`Q5`) are relevant before Phase 0 starts, others only once Phase 3/4 land. Treat
it as a document to re-open at multiple points, not a phase to run once at the end.

## 7. The standing go/no-go gate

Producing this contract kit is preparatory work — it is **not**, by itself, the owner's
authorization to begin editing `vps/daveai-ui-v6.html`, `brain_llm.py`, or anything else in scope.
`CT-005`'s `Q3-pace` item exists specifically to make this explicit: an agent picking up `CT-000` or
`CT-001` must confirm an actual, dated start signal from the owner is on record before treating any
work as authorized, rather than inferring permission from the existence of this kit. As of
2026-09-15, no such signal is on record and every contract's `status` is `not_started` accordingly.

## 8. Structural lineage (attribution, not content)

This kit's per-phase JSON-contract shape — one file per unit of work, each carrying required
evidence, protected paths, and an explicit definition of done, indexed by a top-level manifest — is
modeled structurally on `S:\Github\DAVE-AI-HARNESSED-CONTRACT-KIT-v1.0.0\04_PHASE_PACKS\` (its
`contract-index.json`, its `CT-0XX-*.json` files, and `06_SCHEMAS/contract.schema.json`). That kit
is a mobile/Android-focused framework unrelated to DaveAI.tech in content — nothing about agent
routing, chat SSE, catalogs, or accessibility comes from it. Only the shape (index + per-phase
contract files + required gates/evidence/definition-of-done fields) was reused, then redesigned
around what this project actually is: a hand-deployed, single-file web product with a real,
already-documented drift and evidence trail of its own (`proofs/daveai-prod-audit-20260731/`) to
build on, rather than the reference kit's own field names or subject matter.

## 9. What this kit deliberately does not do

- It does not invent a seventh phase, a security-only contract, or any structure beyond the six
  phases `docs/DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md` already defines.
- It does not mark any contract `in_progress` or `done` — every contract and the index itself are
  `not_started` as of this writing, because no phase-0/1 work has started yet.
- It does not fabricate line ranges the deep-audit workflow hasn't produced yet. Where a contract
  says "line range pending deep-audit workflow completion," that sentence is the accurate current
  state, not a placeholder to quietly fill in with a guess.
- It does not replace the roadmap doc. If the roadmap doc is updated (for example, once the
  133-finding audit's pending 50 items are resolved, or once the full findings ledger is written
  up), the contracts in `docs/contracts/` should be revisited against the new version — this kit is
  a snapshot of the roadmap doc as it stood on 2026-09-15, not a living fork of it.
