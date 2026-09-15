import { test, expect } from '@playwright/test';

// Real, input-driven gameplay test for Dave's Siege TD — the second game (after
// Asteroids) to get one, per DAVEAI_DEEP_AUDIT_ROADMAP_20260915.md's Phase 3 ask ("at
// least one real input-driven test per game beyond Asteroids before calling any of them
// 'working'"). This does not just check the page loads (production-e2e-runner.cjs
// already does that for all games) — it plays through name entry, the campaign/stage
// picker, into a real stage, places a real tower via simulated clicks, and asserts the
// game's own gold counter actually decreased by that tower's exact cost. That specific,
// exact-amount change is what makes this a real gameplay assertion rather than a
// coincidental DOM mutation: $50 off is only explained by the Basic tower's placement.
//
// Every selector and coordinate here was verified against the live page before writing
// this file (see the session transcript for 2026-09-15) — not guessed. If this test
// starts failing, that most likely means the game's UI genuinely changed, not that the
// test is wrong; re-verify against the live page before assuming otherwise.

test('Dave\'s Siege TD: name entry -> stage select -> place a tower -> gold decreases', async ({ page }) => {
  await page.goto('/games/daves-siege-td/index.html');

  // ── Name entry screen ──
  const nameInput = page.getByPlaceholder('Player Name');
  await expect(nameInput).toBeVisible();
  await nameInput.fill('PlaywrightTest');
  await page.getByRole('button', { name: 'Start Game' }).click();

  // ── Main menu — confirms the name-entry -> menu transition is real, not stuck ──
  const playCampaign = page.getByRole('button', { name: /Play Campaign/i });
  await expect(playCampaign).toBeVisible({ timeout: 10_000 });
  await playCampaign.click();

  // ── Stage select — Stage 1 "Green Fields" is unlocked by default ──
  const stage1 = page.getByText('Green Fields', { exact: true });
  await expect(stage1).toBeVisible({ timeout: 10_000 });
  await stage1.click();

  // ── In-game: gameCanvas + the #gold counter must exist before we try to play ──
  const canvas = page.locator('#gameCanvas');
  await expect(canvas).toBeVisible({ timeout: 10_000 });
  const goldEl = page.locator('#gold');
  await expect(goldEl).toBeVisible();
  const startingGold = Number((await goldEl.textContent())?.trim());
  expect(startingGold).toBe(200); // documented starting gold for a fresh Stage 1 run

  // ── Real input: select the Basic ($50) tower via its real accessible button, then
  // click a buildable tile on the canvas itself ──
  // The tower-shop buttons are real DOM elements (not canvas-drawn), so a normal
  // role-based locator is used — robust to viewport size. The grid tiles ARE canvas-
  // drawn, so that click is computed as a percentage of the canvas's own bounding box
  // (12% across, 8% down from its top-left corner lands on a buildable tile in the top
  // row) rather than a raw pixel coordinate, so this doesn't break if the page renders at
  // a different viewport size than whatever this was last verified at. Verified working
  // against the live page before writing this file — see the session transcript for
  // 2026-09-15.
  await page.getByRole('button', { name: /Basic.*\$50/i }).click();
  const box = (await canvas.boundingBox())!;
  await page.mouse.click(box.x + 0.12 * box.width, box.y + 0.08 * box.height);
  await page.waitForTimeout(500); // let the canvas game loop process the placement

  // ── Assert a real, specific, cause-and-effect state change ──
  const goldAfter = Number((await goldEl.textContent())?.trim());
  expect(goldAfter).toBe(startingGold - 50); // exact Basic-tower cost, not just "changed"
});
