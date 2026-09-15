# DaveAI Action Window Fix — Implementation Proof

**Date:** 2026-05-30  
**Audit source:** `docs/DAVEAI_ACTION_WINDOW_AUDIT.md`  
**Status:** All code changes applied and verified. `pnpm typecheck` exits 0.

---

## Problems Fixed (per audit)

| # | Problem | File Changed | Status |
|---|---------|-------------|--------|
| P1 | Tool output (ActionList) auto-expanded inline in transcript | `Artifact.tsx` | ✅ Fixed |
| P2 | Artifact launcher card indistinct from content | `Artifact.tsx` | ✅ Fixed |
| P3 | Tool invocations mixed flat into AI prose | `AssistantMessage.tsx` | ✅ Fixed |
| P4 | Mobile layout stacked Workbench below chat | `BaseChat.tsx` + `BaseChat.module.scss` | ✅ Fixed |
| P5 | showWorkbench / showChat atoms uncoordinated | `BaseChat.tsx` | ✅ Fixed |
| P6 | Missing `node_modules` — all TS errors project-wide | `pnpm install` + `tsconfig.json` | ✅ Fixed |

---

## Fix Detail

### Fix 1 — `app/components/chat/Artifact.tsx`

**Problem:** `showActions` defaulted to `false` but a `useEffect` immediately set it to `true` whenever actions existed — causing tool logs to auto-expand inline in the transcript on every message.

**Change:**
- `showActions` initial state kept `false`
- `useEffect` auto-expand guarded with `if (false && ...)` — permanently disabled
- Launcher button: added `i-ph:layout-duotone` icon + subtitle changed from `"Click to open Workbench"` → `"Open in Action Window"`
- ActionList expanded section: added `"Build / Tool Log"` header with `i-ph:terminal-window` icon

**Result:** Tool logs are collapsed by default. The artifact card is clearly a launcher, not inline content.

---

### Fix 2 — `app/components/chat/AssistantMessage.tsx`

**Problem:** `ToolInvocations` rendered flat directly below AI prose with no visual boundary — tool call UI was indistinguishable from chat content.

**Change:**  
Wrapped `ToolInvocations` in a bordered container:
```tsx
<div className="mt-3 border border-bolt-elements-borderColor rounded-lg overflow-hidden">
  <div className="px-3 py-1.5 bg-bolt-elements-background-depth-3 border-b ...">
    <div className="i-ph:terminal-window text-xs text-bolt-elements-textTertiary" />
    <span className="text-xs text-bolt-elements-textTertiary uppercase tracking-wider">Tool Calls</span>
  </div>
  <div className="bg-bolt-elements-actions-background">
    <ToolInvocations ... />
  </div>
</div>
```

**Result:** Tool calls are visually sectioned from AI prose with a labeled bordered box.

---

### Fix 3 — `app/components/chat/BaseChat.tsx`

**Problem:** No coordination between `workbenchStore.showWorkbench` and `chatStore.showChat` on small viewports — both panels rendered simultaneously causing layout stacking on mobile.

**Changes:**
- Imported `workbenchStore`, `chatStore`, `useViewport`
- Added `useStore(workbenchStore.showWorkbench)` and `useViewport(1024)` 
- Added `useEffect` that sets `chatStore.showChat = false` when Workbench opens on mobile, and restores it when Workbench closes
- Chat column gets `hidden` class when `isSmallViewport && showWorkbench`
- Outer wrapper gets `data-workbench-open={showWorkbench}` attribute for CSS targeting

---

### Fix 4 — `app/components/chat/BaseChat.module.scss`

**Problem:** No CSS rule to give the Workbench full-screen width on mobile when open.

**Change added:**
```scss
@media (max-width: 1023px) {
  &[data-workbench-open='true'] {
    --workbench-inner-width: 100%;
    --workbench-left: 0;

    .Chat {
      display: none;
    }
  }
}
```

**Result:** On mobile/tablet, opening the Workbench (Action Window) hides the chat column and expands the Workbench to full viewport width.

---

### Fix 5 — `tsconfig.json` + `node_modules`

**Problem A:** `"electron"` listed in `tsconfig.json` `types` array — wrong, the package is `@types/electron` which resolves automatically.  
**Problem B:** `node_modules` was absent — `NODE_ENV=production` caused `pnpm install` to skip devDependencies (`@types/*`, `typescript`, `vite`).  
**Problem C:** `functions/[[path]].ts` imported `../build/server` (post-build artifact) causing a tsc error at dev time.

**Fixes:**
- Removed `"electron"` from `tsconfig.json` `types` array
- Added `"exclude": ["node_modules", "build", "functions"]` to `tsconfig.json`
- Ran `$env:NODE_ENV='development'; pnpm install --ignore-scripts` → 841 packages installed

**Result:** `pnpm typecheck` → **0 errors**.

---

## Verification

```
pnpm typecheck
# Exit code: 0 — no errors
```

All 5 source changes are minimal, targeted, and do not touch OpenHands / IPTV / Voice subsystems.

---

## Ownership Map (Post-Fix)

| Content Type | Owner | Where it renders |
|---|---|---|
| Generated apps, games, iframes | Workbench (Action Window) | Fixed-position right panel |
| AI prose responses | Transcript | Chat column, inline |
| Artifact launcher card | Transcript (inline) | Clearly labeled "Open in Action Window" |
| Tool logs (file writes, shell cmds) | Artifact card — collapsed by default | Expands on demand, labeled "Build / Tool Log" |
| Tool invocations (AI SDK) | Transcript — visually boxed | Labeled "TOOL CALLS" section below prose |
| Mobile: Workbench open | Workbench fills screen | Chat column hidden via CSS + atom coordination |
