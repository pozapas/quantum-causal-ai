// Check the lab figures on the real built pages: figure widths, the wide/narrow switch in
// qcai.viz.show, and resizing across the breakpoint.  Run from book/ after a build:
//   node tests/real_figs.mjs OUTDIR
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const HTML = path.resolve('_build/html'), BASE = '/quantum-causal-ai', OUT = process.argv[2];
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let f = path.join(HTML, u.slice(BASE.length));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  const t = TYPES[path.extname(f)];
  res.writeHead(200, t ? { 'content-type': t } : {});
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(8811, r));
const b = await chromium.launch({ channel: 'msedge' });
const labs = ['chance', 'bayes', 'causal-inference', 'interference'];
const errs = [];
for (const vw of [1280, 900, 390]) {
  const p = await b.newPage({ viewport: { width: vw, height: 1000 } });
  p.on('pageerror', e => errs.push(String(e)));
  for (const lab of labs) {
    await p.goto(`http://localhost:8811${BASE}/labs/${lab}/`, { waitUntil: 'networkidle' });
    await p.waitForFunction(() => [...document.querySelectorAll('div[id^="qcai-"]')].every(e => e.querySelector('.main-svg')),
      null, { timeout: 30000 });
    await p.waitForTimeout(800);
    const els = await p.$$('div[id^="qcai-"]');
    const info = [];
    for (const [i, el] of els.entries()) {
      info.push(await el.evaluate(e => ({ w: e.clientWidth, h: e.clientHeight, lh: e.layout.height,
        legend: e.layout.legend ? e.layout.legend.orientation : null })));
      await el.scrollIntoViewIfNeeded();
      if (OUT) await el.screenshot({ path: `${OUT}/real_${lab}_${i}_v${vw}.png` });
    }
    console.log(vw, lab, JSON.stringify(info));
  }
  await p.close();
}
const p = await b.newPage({ viewport: { width: 1280, height: 1000 } });
p.on('pageerror', e => errs.push(String(e)));
await p.goto(`http://localhost:8811${BASE}/labs/interference/`, { waitUntil: 'networkidle' });
await p.waitForTimeout(2000);
const hs = () => p.evaluate(() => [...document.querySelectorAll('div[id^="qcai-"]')].map(e =>
  [e.clientWidth, e.clientHeight, (e.layout.yaxis.domain || []).map(v => +v.toFixed(2)).join('-')]));
console.log('resize 1280', JSON.stringify(await hs())); if (OUT) await (await p.$('div[id^="qcai-"]')).screenshot({ path: OUT + '/resize_' + Date.now() + '.png' });
await p.setViewportSize({ width: 390, height: 1000 }); await p.waitForTimeout(1500);
console.log('resize  390', JSON.stringify(await hs()));
await p.setViewportSize({ width: 1280, height: 1000 }); await p.waitForTimeout(1500);
console.log('resize 1280', JSON.stringify(await hs())); if (OUT) await (await p.$('div[id^="qcai-"]')).screenshot({ path: OUT + '/resize_' + Date.now() + '.png' });
console.log('page errors', errs.length, errs.slice(0, 3).join(' | '));
await b.close();
server.close();
