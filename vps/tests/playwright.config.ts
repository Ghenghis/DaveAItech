import { defineConfig } from '@playwright/test';

// Minimal config for DaveAI.tech's real (input-driven, not just "does it load") gameplay
// tests. Runs against production directly, same approach vps/production-e2e-runner.cjs
// already uses for its smoke checks — there is no local dev server for these games, they
// are static pages served from the live VPS.
export default defineConfig({
  testDir: '.',
  timeout: 30_000,
  retries: 1,
  reporter: [['list']],
  use: {
    baseURL: 'https://daveai.tech',
    headless: true,
  },
});
