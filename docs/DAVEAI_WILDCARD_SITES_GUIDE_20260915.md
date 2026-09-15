# Adding Your Other Sites to DaveAI.tech — How It Actually Works (2026-09-15)

This is the piece the user asked for early in this project: a way to add sites you run
elsewhere — sites DaveAI didn't build, that you don't necessarily control — into the same
launcher UI as everything else on daveai.tech.

**Status: the mechanism already exists in the live code.** This doc explains how to use it
and exactly what it does under the hood, verified by reading the actual functions involved
(`saveNewProject`, `shouldUseLaunchCard`, `shouldLaunchExternally`, `loadProject` in
`vps/daveai-ui-v6.html`) — not assumed from the roadmap description. **It has not been
tested live in an authenticated browser session** — see "What hasn't been verified" below.

## How to add a site, as a user

1. Open the side panel's **Projects** tab.
2. Click the **Other** category button (alongside Web / Apps / Games).
3. Click **+ Add project**.
4. Type a name and the site's URL (`https://...`), click **Add**.

That's it. The new entry appears under **Other**, saved both to your browser and (if
you're signed in) to the DaveAI server, so it follows you across devices.

## What happens when you click it

- If the URL is on a **different domain** than daveai.tech (true for basically every
  "other site" you'd add), clicking the project opens it in a **new browser tab** —
  `window.open(url, '_blank', 'noopener,noreferrer')`. It does **not** get embedded in an
  iframe inside DaveAI. This is deliberate: framing a site you don't control risks it
  refusing to load (many sites block being iframed) and is generally not something to do
  to a site whose security posture you haven't reviewed.
- The Action Window (DaveAI's central preview panel) also gets a launch-card shortcut to
  the same URL, as a fallback in case your browser's pop-up blocker stopped the new tab.
- Only DaveAI's own, explicitly-vetted pages (the ones in `daveai-project-catalog.json`
  marked `"embed": true` — things like the Studio page, the arcade games, the historical
  landing-page variant) get embedded inline. A project you add yourself never does, because
  new projects never set `embed` at all, and the code only embeds when `embed === true`
  exactly — anything else (`undefined`, `false`, a typo) is treated as "don't embed."

## Why this is safe by default

- **No iframe for sites you don't control.** Covered above — the code checks the actual
  origin of the URL, not a flag you'd have to remember to set correctly.
- **`noopener,noreferrer` on external launches.** The opened site can't get a JavaScript
  reference back to the DaveAI tab that opened it (protects against a class of attack
  called reverse tabnabbing), and DaveAI doesn't leak its own URL as a referrer header to
  the site you're opening.
- **No way to force iframe-embedding from the add-project form.** The simple name+URL form
  doesn't expose an `embed` toggle at all. If you genuinely want one of your own sites
  embedded inline (not just launched in a new tab), that needs a manual catalog entry with
  `"embed": true` — see below — not something to flip on casually, since it only makes
  sense for a site you're confident won't refuse to be framed and whose content you trust
  completely inside the DaveAI shell.

## If you want a site added to the *permanent* catalog instead

The "Add project" form creates a **personal, local-to-you** entry (your browser + your
account). If you want a site to show up for the catalog/launcher more broadly — the way
Hermes3D or HermesTV do — that's a different, manual step: add an entry to
`vps/daveai-project-catalog.json` directly, following the existing format:

```json
{ "id": "srv-your-site-id", "name": "Your Site Name", "url": "https://your-site.example.com/",
  "cat": "other", "status": "live", "description": "What this site is." }
```

Leave `embed` unset (or explicitly `false`) unless you've specifically verified the site
renders fine inside an iframe and you want that. This file is fetched live by the running
page (`SERVER_PROJECT_CATALOG_URL` in `vps/daveai-ui-v6.html`), so a change here reaches
every visitor, not just your own browser — deploy it deliberately, the same way as any
other production change to `vps/daveai-ui-v6.html`'s companion files.

## What hasn't been verified

This doc describes what the code does, confirmed by reading it end to end. It does **not**
confirm what actually happens when you click through it live — that needs an authenticated
browser session, which wasn't done as part of writing this. Before relying on this for
something important, do the walkthrough above yourself once and confirm:

1. A project you add under "Other" actually appears there (not silently miscategorized).
2. Clicking it opens a new tab, not an iframe, for a URL you don't control.
3. It's still there after refreshing the page (confirms local persistence worked) and,
   if signed in, still there after signing in from a different browser (confirms server
   sync worked).

If any of those don't hold, that's a real bug in a mechanism this doc currently describes
as working — please say so rather than assuming this doc is right over what you actually see.
