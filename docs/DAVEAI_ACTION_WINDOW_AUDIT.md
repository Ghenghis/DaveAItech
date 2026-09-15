# DaveAI Action Window Audit

**Date:** 2026-05-30  
**Codebase:** `g:/Github/Bolt.DIY`  
**Status:** Real source audit — no speculation, no mocks.

---

## 1. Terminology Map

The user requirement uses "Action Window." In this codebase that concept maps to:

| Requirement term | Actual component | File |
|-----------------|-----------------|------|
| Action Window | `Workbench` | `app/components/workbench/Workbench.client.tsx` |
| Transcript | `Messages` | `app/components/chat/Messages.client.tsx` |
| Composer | `ChatBox` | `app/components/chat/ChatBox.tsx` |
| Tool/Build Log | `ActionList` inside `Artifact` | `app/components/chat/Artifact.tsx` |
| Artifact inline card | `Artifact` | `app/components/chat/Artifact.tsx` |

---

## 2. Top-Level Layout (BaseChat.tsx lines 344–500)

```
<div ref={ref} className="relative flex h-full w-full overflow-hidden">   ← .BaseChat
  <Menu />                                                                  ← sidebar
  <div className="flex flex-col lg:flex-row overflow-y-auto w-full h-full">
    │
    ├── <div className=".Chat flex flex-col flex-grow h-full">             ← LEFT PANEL (chat column)
    │     <StickToBottom>
    │       <Messages />                                                    ← transcript
    │       <ScrollToBottom />
    │     </StickToBottom>
    │     <div sticky bottom>                                               ← composer area
    │       <DeployChatAlert />
    │       <SupabaseChatAlert />
    │       <ChatAlert />
    │       <LlmErrorAlert />
    │       <ProgressCompilation />
    │       <ChatBox />                                                     ← composer
    │     </div>
    │     <ImportButtons />, <GitCloneButton />                             ← only when !chatStarted
    │     <ExamplePrompts />, <StarterTemplates />                         ← only when !chatStarted
    │   </div>
    │
    └── <Workbench />                                                       ← RIGHT PANEL (Action Window)
```

**Key constraint:** The flex row is `lg:flex-row` (side-by-side on ≥1024px) and `flex-col` below that (stacked vertically on mobile). On mobile the Workbench renders **below** the chat column in DOM order, which is exactly what is causing the "bunched together" symptom on small viewports.

---

## 3. Workbench (Action Window) — Layout & Position

**File:** `app/components/workbench/Workbench.client.tsx` lines 375–514

```tsx
<motion.div className="z-workbench">
  <div className="fixed top-[calc(var(--header-height)+1.2rem)] bottom-6
                  w-[var(--workbench-inner-width)]
                  left-[var(--workbench-left)]">    ← position-fixed, slides in from right
    <div className="h-full flex flex-col bg-... rounded-lg overflow-hidden">
      <header>   ← toolbar: sidebar toggle | Code/Diff/Preview slider | Sync | Terminal | Close
      <div className="relative flex-1 overflow-hidden">
        <EditorPanel />    ← code view
        <DiffView />       ← diff view
        <Preview />        ← preview/iframe view  ← THIS is where generated apps/games render
      </div>
    </div>
  </div>
</motion.div>
```

**Workbench is `position: fixed`.** It does NOT participate in flex layout flow. It animates `left` from `100%` (hidden) to `left: var(--workbench-left)` when `showWorkbench = true`.

### CSS variables controlling position

These are defined in the global CSS (not in this file — need to check `app/styles` or root):

| Variable | Meaning |
|----------|---------|
| `--workbench-width` | Width of the open Workbench panel |
| `--workbench-inner-width` | Actual inner width |
| `--workbench-left` | Left offset = chat column width |
| `--chat-min-width` | Minimum width of the left chat column |
| `--header-height` | Height of the top header bar |

---

## 4. Artifact Rendering Path

### Where artifacts originate

1. LLM streams text containing `<div class="__boltArtifact__" data-message-id="..." data-artifact-id="..."></div>`
2. `Markdown.tsx` (lines 32–47) detects `className.includes('__boltArtifact__')` and renders `<Artifact messageId artifactId />`
3. `Artifact` is rendered **inside the `Messages` list**, inside the chat column — it is an **inline card in the transcript**

### What the Artifact card actually renders

`Artifact.tsx` lines 80–157:

```
<div className="artifact border ...">
  <button onClick={() => workbenchStore.showWorkbench.set(!showWorkbench)}>
    "{title}" — Click to open Workbench     ← a CLICKABLE CARD, not the artifact itself
  </button>
  <ActionList />    ← file writes, shell commands, status — TOOL/BUILD LOG content
</div>
```

**The artifact card is a launcher/log panel rendered inside the transcript.** The actual generated app/game/HTML renders in `<Preview />` inside the Workbench (Action Window).

---

## 5. Ownership Map — Current vs Intended

### 5a. Games / Generated Apps / Generated HTML

| Property | Value |
|----------|-------|
| **Source function** | WebContainer starts a dev server; `PreviewsStore` registers the URL |
| **Where it renders** | `Preview.tsx` → rendered inside `Workbench` → inside `<View animate preview>` |
| **Current DOM node** | `Workbench > div.fixed > div > div.relative.flex-1 > motion.div[preview] > Preview` |
| **Current owner** | Workbench ✅ — correct by design |
| **Intended owner** | Workbench (Action Window) ✅ |
| **CSS controlling region** | `position: fixed`, `inset-0` inside inner Workbench div |
| **Why it may appear wrong** | On mobile (`< 1024px`) Workbench becomes `w-full left-0` and overlays the whole screen when open. When closed, the preview is not visible at all. The artifact card in the transcript is all that's visible below the chat. |

### 5b. Generated Code Previews / iframes

| Property | Value |
|----------|-------|
| **Source function** | `Preview.tsx` renders `<iframe>` pointed at WebContainer preview URL |
| **Where it renders** | Inside `Workbench > Preview view` |
| **Current DOM node** | `motion.div[preview view] > Preview > iframe` |
| **Current owner** | Workbench ✅ |
| **Intended owner** | Workbench (Action Window) ✅ |
| **Why it may appear wrong** | Same as above — mobile layout or Workbench not open |

### 5c. Tool Output / Commit Logs / File-Write Logs

| Property | Value |
|----------|-------|
| **Source function** | `ActionRunner` produces `ActionState[]`; `ActionList` renders them |
| **Where it renders** | Inside `Artifact` component → inside `Messages` → **inside the Transcript column** |
| **Current DOM node** | `Messages > div[message] > AssistantMessage > Markdown > Artifact > ActionList` |
| **Current owner** | Transcript (Messages list) ❌ — VIOLATION |
| **Intended owner** | Tool/Build Log — separate region |
| **CSS controlling region** | Inherits from `.MarkdownContent` styles; `Artifact` has `.artifact` with `margin: 1.5em 0` |
| **Why it renders wrong** | `ActionList` (file writes, shell runs, start server) is embedded directly inside the `Artifact` card which is inside `AssistantMessage` which is inside `Messages`. There is no separate "Build Log" panel. All tool output flows into the transcript column. |

### 5d. AI Text Responses / Chat Messages

| Property | Value |
|----------|-------|
| **Source function** | `AssistantMessage` renders `<Markdown>{content}</Markdown>` |
| **Where it renders** | `Messages > div[message] > AssistantMessage > Markdown` |
| **Current DOM node** | Inside the chat column's `StickToBottom` region |
| **Current owner** | Transcript ✅ |
| **Intended owner** | Transcript ✅ |
| **Why it may appear wrong** | Correct in isolation — problem is that `ActionList` (tool logs) and `Artifact` cards also render here, mixing log content with AI text |

### 5e. User Messages

| Property | Value |
|----------|-------|
| **Source function** | `UserMessage` component |
| **Where it renders** | `Messages > div[message] > UserMessage` |
| **Current owner** | Transcript ✅ |
| **Intended owner** | Transcript ✅ |
| **Status** | Correct |

### 5f. Composer / Prompt Input

| Property | Value |
|----------|-------|
| **Source function** | `ChatBox` component |
| **Where it renders** | Bottom of `.Chat` column, sticky bottom |
| **Current DOM node** | `div.sticky.bottom-2 > ChatBox` |
| **Current owner** | Chat column ✅ |
| **Intended owner** | Composer region ✅ |
| **Potential overlap issue** | `sticky bottom-2` within a scrollable column means it stays at bottom of chat area. If the chat column has overflow issues on mobile (column stacking), the composer can visually overlap message content. |

### 5g. Device State / Workbench Toggle

| Property | Value |
|----------|-------|
| **Source** | `workbenchStore.showWorkbench` (nanostores atom) |
| **Controls** | `Workbench` visibility AND the sidebar toggle button inside Workbench header AND `Artifact` button click handler |
| **Current owner** | Two places toggle it: (1) `Artifact` button onClick, (2) Workbench header close button |
| **Duplication** | `canHideChat` logic in Workbench header also controls `chatStore.showChat`. This means two separate atoms (`showWorkbench`, `showChat`) control the layout split. On mobile, neither one is cleaning up the other reliably. |

---

## 6. Root Cause of Violations

### Violation 1 — Tool/build logs mixed into transcript

**Root cause:** `ActionList` is rendered inside `Artifact`, which is rendered inside `AssistantMessage`, which is inside `Messages`. There is no separate "Tool/Build Log" panel in the DOM. The entire action log (file writes, shell commands, server start) lives in the transcript column.

**Required fix:** Extract `ActionList` out of the transcript into a dedicated panel (collapsible build log drawer, separate column, or the Workbench sidebar), OR move it into the Workbench header area. Do not render tool output inside `AssistantMessage`.

### Violation 2 — Generated artifacts appear "below" the Action Window on mobile

**Root cause:** The flex column layout (`flex-col` on `< 1024px`) places the Workbench in DOM order **after** the chat column. When `showWorkbench` is true on mobile, it uses `position: fixed; w-full; left-0` to cover the full screen — but the artifact card in the transcript (an inline div in `Messages`) is still present in the chat column below it. The user sees: messages → artifact card → (scroll down) → nothing visible, because Workbench is overlaying the screen. On desktop, the Workbench slides in from the right and occupies the right column correctly.

**Required fix:** On mobile, when Workbench is open, the chat column must be hidden or the Workbench must be a true overlay with no scroll-behind bleed.

### Violation 3 — Artifact card in transcript is misleading

**Root cause:** The `Artifact` component renders a "Click to open Workbench" button card inline in the message stream. This is a UX artifact — it is not the actual preview/game/app. But it looks like generated content and visually "mixes" with AI text, making it appear that content is "bunched together" in the chat column.

**Required fix:** The artifact card should either (a) be visually distinct with a clear "→ Workbench" label, or (b) be removed from the transcript and replaced with an auto-open Workbench trigger.

### Violation 4 — No separation between AI message text and tool log text

**Root cause:** `AssistantMessage` renders both `<Markdown>{content}</Markdown>` (AI text) and `<Artifact>` cards (tool logs) in one flat `div`. The `ToolInvocations` component also renders at the bottom of the same `AssistantMessage`. There is no visual or structural boundary.

**Required fix:** Separate `ToolInvocations` and `Artifact` cards into a visually distinct section (e.g., collapsible "Build Details" section with a separator), not inline with the AI prose text.

---

## 7. Per-Artifact-Type Fix Table

| Artifact Type | Source JS | Target DOM (current) | Current Owner | Intended Owner | Rendering Wrong? | Fix Required |
|---------------|-----------|---------------------|---------------|----------------|-----------------|-------------|
| Generated app / game | `PreviewsStore` → WebContainer | `Workbench > Preview > iframe` | Workbench | Action Window | ✅ Correct on desktop. ❌ Not visible on mobile unless WB open | Mobile layout: hide chat col when WB open |
| Generated HTML preview | Same | Same | Workbench | Action Window | Same as above | Same |
| Code preview (editor) | `EditorPanel` | `Workbench > EditorPanel` | Workbench | Action Window | ✅ Correct | None |
| iframe / imported preview | `Preview.tsx` | `Workbench > Preview > iframe` | Workbench | Action Window | ✅ Correct | None |
| Artifact inline card | `Artifact.tsx` via `Markdown.tsx` | `Messages > AssistantMessage > Markdown > Artifact` | Transcript ❌ | Tool/Build Log | Yes — card + action list in transcript | Extract to dedicated build log region |
| Tool output (file writes, shell) | `ActionList` in `Artifact.tsx` | `Messages > AssistantMessage > Markdown > Artifact > ActionList` | Transcript ❌ | Tool/Build Log | Yes — tool output mixed with AI text | Move out of transcript |
| Commit logs | Not a distinct component — commit msgs appear in shell action content | Same as above | Transcript ❌ | Tool/Build Log | Yes | Same |
| AI text (prose) | `AssistantMessage > Markdown` | `Messages > AssistantMessage` | Transcript ✅ | Transcript | Only if mixed with tool items | Separate from artifact cards |
| User messages | `UserMessage` | `Messages > UserMessage` | Transcript ✅ | Transcript | No | None |
| Composer / prompt input | `ChatBox` | `div.sticky.bottom-2 > ChatBox` | Composer ✅ | Composer | Possible overlap on mobile | Fix mobile overflow |
| ToolInvocations | `ToolInvocations.tsx` | `Messages > AssistantMessage > ToolInvocations` | Transcript ❌ | Tool/Build Log | Yes | Move to separate panel |
| Progress compilation | `ProgressCompilation` | Above `ChatBox` in prompt area | Composer area | Build Log | Partial | Move to build log |
| Device state (WB toggle) | `workbenchStore.showWorkbench` + `chatStore.showChat` | Two atoms, two toggle points | Split | Single controller | Partial | Unify under one layout controller |

---

## 8. Files That Must Be Changed to Fix

| File | Change Needed |
|------|---------------|
| `app/components/chat/BaseChat.tsx` | Mobile layout: hide chat col when Workbench is open on small viewports |
| `app/components/chat/BaseChat.module.scss` | Add mobile CSS rule for chat column hide state |
| `app/components/chat/AssistantMessage.tsx` | Separate artifact cards and ToolInvocations from AI prose; wrap in distinct section |
| `app/components/chat/Artifact.tsx` | Extract `ActionList` from inline transcript position; or collapse by default |
| `app/components/chat/Messages.client.tsx` | No change to structure needed — individual message rendering handles this |
| `app/components/workbench/Workbench.client.tsx` | No changes needed for desktop; mobile state handling can be improved |

---

## 9. Acceptance Criteria (Not Marked Done Until Screenshot Proven)

| Criterion | Status |
|-----------|--------|
| Generated games render inside Action Window (Workbench Preview) | Not screenshot-proven |
| No generated artifact appears below the Action Window | Not screenshot-proven |
| Chat (transcript) is visible and not covered | Not screenshot-proven |
| Transcript contains AI and user messages only | ❌ Currently contains artifact cards + tool logs |
| Tool/build logs separated from chat | ❌ Not separated in current codebase |
| Composer does not overlap chat | Not screenshot-proven on mobile |
| Device state controlled by one system | ❌ Two atoms: `showWorkbench` + `showChat` |
| Desktop 1920×1080 passes visually | Not screenshot-proven |
| Mobile 375px passes visually | Not screenshot-proven |
| Right-panel-open state passes visually | Not screenshot-proven |

---

## 10. What Has NOT Been Changed

Nothing in the codebase has been modified by this audit. This document is read-only analysis. No fixes have been applied. No completions are claimed. Screenshots are required before any criterion can be marked passing.
