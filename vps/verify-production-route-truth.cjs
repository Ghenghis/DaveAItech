'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const root = __dirname;
const sitesPath = path.join(root, 'daveai-sites-config.json');
const outputFlag = process.argv.indexOf('--output');
const outputPath = outputFlag >= 0 ? process.argv[outputFlag + 1] : '';
const document = JSON.parse(fs.readFileSync(sitesPath, 'utf8'));
const sites = document.sites || [];

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

async function check(site) {
  const before = Date.now();
  try {
    const response = await fetch(site.url, {
      redirect: 'manual',
      headers: {
        'Cache-Control': 'no-cache',
        'User-Agent': 'DaveAI-Route-Truth/1.0',
      },
      signal: AbortSignal.timeout(12000),
    });
    const location = response.headers.get('location') || '';
    let finalHttpStatus = response.status;
    let finalUrl = response.url;
    if (site.status === 'live' && [301, 302, 303, 307, 308].includes(response.status)) {
      const followed = await fetch(site.url, {
        redirect: 'follow',
        headers: {
          'Cache-Control': 'no-cache',
          'User-Agent': 'DaveAI-Route-Truth/1.0',
        },
        signal: AbortSignal.timeout(12000),
      });
      finalHttpStatus = followed.status;
      finalUrl = followed.url;
    }
    // A 'live' site must not have quietly regressed into being gated behind the
    // Authelia SSO login wall. Following a redirect and finding a 200 is not
    // enough on its own: the login page itself returns 200 when loaded directly,
    // so a 'live' site that now redirects into SSO would otherwise still show
    // finalHttpStatus === 200 and be reported as passing. auth.daveai.tech's own
    // entry is exempted since checking it is expected to land on itself.
    const AUTH_HOST_PREFIX = 'https://auth.daveai.tech/';
    const finalIsLoginWall = site.domain !== 'auth.daveai.tech' && finalUrl.startsWith(AUTH_HOST_PREFIX);
    const livePassed = site.status === 'live' && finalHttpStatus === 200 && !finalIsLoginWall;
    const authPassed = site.status === 'auth'
      && [302, 303, 307, 308].includes(response.status)
      && location.startsWith(AUTH_HOST_PREFIX);
    return {
      domain: site.domain,
      label: site.status,
      url: site.url,
      httpStatus: response.status,
      location: location || null,
      finalHttpStatus,
      finalUrl,
      finalIsLoginWall,
      latencyMs: Date.now() - before,
      passed: livePassed || authPassed,
    };
  } catch (error) {
    return {
      domain: site.domain,
      label: site.status,
      url: site.url,
      httpStatus: 0,
      location: null,
      latencyMs: Date.now() - before,
      passed: false,
      error: error.name === 'TimeoutError' ? 'timeout' : error.message,
    };
  }
}

async function main() {
  // Previously hardcoded an exact site count (22) and live/auth split (14/8) here,
  // independently re-hardcoded in vps/verify-source-of-truth.py, so both had to be
  // updated by hand on every site add/remove/re-status or the two "source of truth"
  // gates could silently disagree. Removed rather than kept as manual-sync mitigation:
  // `counts.live`/`counts.auth` below are just a tally of each site's own *declared*
  // `status` field (see check()'s `label: site.status`) — they say nothing about
  // observed reality, so asserting they equal fixed numbers was really just re-asserting
  // "the config's composition hasn't changed," redundant with (and more brittle than)
  // the actual regression check this script exists for: does each site's *observed* live
  // behavior (passed, from the real HTTP check) match what its config declares it should
  // be. That check needs no site count at all. The one thing worth guarding independently
  // of any count is an empty/broken config silently reporting a trivial "0 failures" pass.
  if (sites.length === 0) throw new Error('No sites found in daveai-sites-config.json — refusing to report a trivial pass');
  if (sites.some((site) => site.status === 'soon')) throw new Error('A soon route remains in the source catalog');
  const results = await Promise.all(sites.map(check));
  const counts = results.reduce((summary, result) => {
    summary[result.label] = (summary[result.label] || 0) + 1;
    return summary;
  }, {});
  const failed = results.filter((result) => !result.passed);
  const proof = {
    schema: 'daveai-route-truth-proof/v1',
    checkedAt: new Date().toISOString(),
    sitesConfigSha256: sha256(sitesPath),
    counts,
    passed: failed.length === 0,
    failed: failed.map((result) => result.domain),
    results,
  };
  const serialized = `${JSON.stringify(proof, null, 2)}\n`;
  if (outputPath) {
    fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
    fs.writeFileSync(outputPath, serialized);
  }
  process.stdout.write(serialized);
  if (!proof.passed) process.exitCode = 1;
}

main().catch((error) => {
  process.stderr.write(`${error.stack}\n`);
  process.exitCode = 1;
});
