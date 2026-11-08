// C7 browser check. Serves book/_build/html at /quantum-causal-ai/ and crawls every page
// with headless Edge (Playwright channel msedge). Prints one JSON line as the last line.
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const here = path.dirname(fileURLToPath(import.meta.url));
const HTML = path.resolve(here, '..', '_build', 'html');
const SHOTS = path.resolve(here, '..', 'evidence', 'screenshots');
const BASE = '/quantum-causal-ai';
const PORT = 8799;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.xml': 'application/xml',
  '.txt': 'text/plain', '.ipynb': 'application/json', '.md': 'text/markdown', '.woff2': 'font/woff2', '.inv': 'application/octet-stream' };

fs.mkdirSync(SHOTS, { recursive: true });
const server = http.createServer((req, res) => {
  let u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (!u.startsWith(BASE)) { res.writeHead(404); return res.end('outside base'); }
  let f = path.join(HTML, u.slice(BASE.length));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end('nf'); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
const LIVE = process.env.LIVE_ORIGIN || '';  // e.g. https://pozapas.github.io : crawl the deployed site
if (!LIVE) await new Promise(r => server.listen(PORT, r));

function pages(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory() && e.name !== 'build') out.push(...pages(path.join(dir, e.name), rel + '/' + e.name));
    else if (e.name === 'index.html') out.push(rel + '/');
  }
  return out;
}
const list = pages(HTML).sort();
const errors = [];
const links = new Set();
const stats = { pages: list.length, plotlyPlaceholders: 0, plotlyDrawn: 0, mobileChecked: 0, axe: {} };

const browser = await chromium.launch({ channel: 'msedge' });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const origin = LIVE || `http://localhost:${PORT}`;

async function visit(page, url) {
  const pageErrors = [], bad = [];
  const onErr = e => pageErrors.push(e.message);
  const onResp = r => { if (r.url().startsWith(origin) && r.status() >= 400) bad.push(`${r.status()} ${r.url()}`); };
  page.on('pageerror', onErr); page.on('response', onResp);
  await page.goto(origin + BASE + url, { waitUntil: 'networkidle', timeout: 90000 });
  for (let y = 0; y < 30; y++) {           // scroll so lazy outputs mount
    const done = await page.evaluate(() => { window.scrollBy(0, 1200); return window.innerHeight + window.scrollY >= document.body.scrollHeight - 2; });
    await page.waitForTimeout(150);
    if (done) break;
  }
  await page.waitForTimeout(800);
  // wait up to 15 s for every plotly placeholder to draw
  let st;
  for (let i = 0; i < 30; i++) {
    st = await page.evaluate(() => {
      const ph = [...document.querySelectorAll('div[id^="qcai-"]')];
      return { ph: ph.length, drawn: ph.filter(d => d.querySelector('.main-svg')).length,
               loading: (document.querySelector('article')?.innerText.match(/Loading\.\.\./g) || []).length };
    });
    if (st.drawn === st.ph && st.loading === 0) break;
    await page.waitForTimeout(500);
  }
  const hrefs = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.href));
  hrefs.filter(h => h.startsWith(origin)).forEach(h => links.add(h.split('#')[0]));
  page.off('pageerror', onErr); page.off('response', onResp);
  return { pageErrors, bad, ...st };
}

const page = await ctx.newPage();
for (const url of list) {
  try {
    const r = await visit(page, url);
    stats.plotlyPlaceholders += r.ph; stats.plotlyDrawn += r.drawn;
    r.pageErrors.forEach(e => errors.push(`${url}: page error: ${e.slice(0, 160)}`));
    r.bad.forEach(e => errors.push(`${url}: ${e}`));
    if (r.drawn !== r.ph) errors.push(`${url}: plotly drawn ${r.drawn}/${r.ph}`);
    if (r.loading) errors.push(`${url}: ${r.loading} outputs stuck on Loading...`);
  } catch (e) { errors.push(`${url}: ${e.message.split('\n')[0]}`); }
}

// Widgets: learning map and placement dialog must work
try {
  const wp = await ctx.newPage();
  await wp.goto(origin + BASE + '/start/roadmap/', { waitUntil: 'networkidle' }); await wp.waitForTimeout(1500);
  const nodes = await wp.locator('[data-qcai-widget="map"] g.node[tabindex="0"]').count();
  stats.mapNodes = nodes;
  if (nodes !== 80) errors.push(`learning map shows ${nodes}/80 focusable lessons`);
  await wp.locator('g.node[data-node="L5-05"]').focus(); await wp.keyboard.press('Enter'); await wp.waitForTimeout(300);
  const panel = await wp.locator('[data-qcai-widget="map"] .qw-panel').innerText();
  if (!panel.includes('L5-05')) errors.push('learning map: keyboard selection did not update the panel');
  const href = await wp.locator('[data-qcai-widget="map"] .qw-panel a.go').getAttribute('href');
  const r = await wp.request.get(new URL(href, wp.url()).href);
  if (r.status() >= 400) errors.push(`learning map: lesson link ${href} -> ${r.status()}`);
  await wp.click('[data-qcai-widget="map"] [data-act="expand"]'); await wp.waitForTimeout(400);
  const wide = await wp.locator('.qw-full .qw-scroll > svg.wide').count();
  const vb0 = await wp.locator('.qw-full .qw-scroll > svg').getAttribute('viewBox');
  await wp.click('.qw-full [data-z="in"]'); await wp.waitForTimeout(150);
  const vb1 = await wp.locator('.qw-full .qw-scroll > svg').getAttribute('viewBox');
  await wp.keyboard.press('Escape'); await wp.waitForTimeout(250);
  const closed = (await wp.locator('.qw-full').count()) === 0 && (await wp.locator('[data-qcai-widget="map"] g.node').count()) === 80;
  if (wide !== 1 || vb0 === vb1 || !closed) errors.push(`learning map full-screen viewer: wide=${wide} zoomed=${vb0 !== vb1} closedIntact=${closed}`);
  const fresh = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const hp = await fresh.newPage();
  await hp.goto(origin + BASE + '/', { waitUntil: 'networkidle' }); await hp.waitForTimeout(1500);
  const opened = await hp.locator('[data-qcai-widget="placement"] .qp-veil.open').count();
  if (opened !== 1) errors.push('placement dialog did not open on first visit');
  await hp.click('[data-who="1"]');
  for (const k of [1, 0, 2]) { await hp.click(`.qp-body [data-k="${k}"]`); await hp.waitForTimeout(120); }
  await hp.click('.qp-body [data-k="0"]'); await hp.waitForTimeout(300);   // wrong answer on the matrix question -> Level 3
  const res = await hp.locator('.qp-body h2').innerText();
  stats.placementResult = res;
  if (!res.startsWith('Level 3')) errors.push(`placement scoring: expected Level 3, got "${res}"`);
  const start = await hp.locator('.qp-body a.qp-btn').first().getAttribute('href');
  const r2 = await hp.request.get(new URL(start, hp.url()).href);
  if (r2.status() >= 400) errors.push(`placement: start link ${start} -> ${r2.status()}`);
  await hp.keyboard.press('Escape'); await hp.waitForTimeout(200);
  if (await hp.locator('.qp-veil.open').count()) errors.push('placement dialog did not close on Escape');
  await hp.reload({ waitUntil: 'networkidle' }); await hp.waitForTimeout(1200);
  if (await hp.locator('.qp-veil.open').count()) errors.push('placement dialog reopened after it was dismissed');
  await fresh.close(); await wp.close();
} catch (e) { errors.push(`widget check: ${e.message.split('\n')[0]}`); }

// Every internal link must stay under the base path and resolve
stats.internalLinks = links.size;
for (const h of links) {
  if (!new URL(h).pathname.startsWith(BASE + '/') && new URL(h).pathname !== BASE) {
    if (!LIVE) errors.push(`link outside base path: ${h}`);  // live: same host, other site pages (checked by verify_links.py)
    continue; }
  const r = await page.request.get(h);
  if (r.status() >= 400) errors.push(`broken internal link ${r.status()}: ${h}`);
}

// Mobile overflow + screenshots on a sample
const sample = list.filter(u => u === '/' || /level-0\/$|l0-01|l5-05|l7-10|labs\/$|labs\/chance|qubit-bloch|entanglement-bell|quantum-switch|quantum-causal-inference|roadmap|watch-listen|glossary|bibliography/.test(u));
const mctx = await browser.newContext({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const mpage = await mctx.newPage();
for (const url of sample) {
  try {
    await visit(mpage, url);
    const ov = await mpage.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    stats.mobileChecked++;
    if (ov > 1) errors.push(`${url}: horizontal overflow ${ov}px at 375px`);
  } catch (e) { errors.push(`${url} (mobile): ${e.message.split('\n')[0]}`); }
}
for (const [name, url, p] of [['home-desktop', '/', page], ['lesson-desktop', '/levels/level-5/l5-05/', page],
  ['lab-desktop', '/labs/qubit-bloch/', page], ['home-mobile', '/', mpage], ['lesson-mobile', '/levels/level-5/l5-05/', mpage]]) {
  if (!list.includes(url)) continue;
  await visit(p, url); await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(SHOTS, `${name}.png`), fullPage: false });
}

// axe-core on three pages
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js', { paths: [path.resolve(here, '..', '..')] }), 'utf8');
for (const url of ['/', '/levels/level-5/l5-05/', '/labs/entanglement-bell/'].filter(u => list.includes(u))) {
  await visit(page, url);
  await page.addScriptTag({ content: axeSrc });
  const res = await page.evaluate(async () => (await window.axe.run(document, { resultTypes: ['violations'] })).violations
    .filter(v => v.impact === 'serious' || v.impact === 'critical').map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, target: v.nodes[0]?.target?.join(' ') })));
  stats.axe[url] = res.length;
  res.forEach(v => errors.push(`${url}: axe ${v.impact} ${v.id} x${v.n} (${v.target})`));
}

await browser.close(); if (!LIVE) server.close();
console.log(JSON.stringify({ ...stats, errors }));
