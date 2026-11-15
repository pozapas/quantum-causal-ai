// Full-page screenshot of built pages.  Run from book/ after a build:
//   node tests/page_shot.mjs OUTDIR WIDTH levels/level-3/l3-01/ [other/path/ ...]   (no leading slash: Git Bash rewrites it)
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const [OUT, W, ...paths] = process.argv.slice(2);
const HTML = path.resolve('_build/html'), BASE = '/quantum-causal-ai';
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.mp4': 'video/mp4', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let f = path.join(HTML, u.slice(BASE.length));
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  const t = TYPES[path.extname(f)];
  res.writeHead(200, t ? { 'content-type': t } : {});
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(8812, r));
const b = await chromium.launch({ channel: 'msedge' });
const p = await b.newPage({ viewport: { width: Number(W), height: 1000 } });
const errs = [];
p.on('pageerror', e => errs.push(String(e)));
for (const raw of paths) {
  const u = "/" + raw.replace(/^\/+/, "");
  await p.goto(`http://localhost:8812${BASE}${u}`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(2500);
  const name = u.replace(/\//g, '_').replace(/^_|_$/g, '') || 'home';
  await p.screenshot({ path: `${OUT}/${name}_w${W}.png`, fullPage: true });
  const info = await p.evaluate(() => ({ h: document.body.scrollHeight, plots: document.querySelectorAll('.main-svg').length,
    videos: document.querySelectorAll('video').length, mermaid: document.querySelectorAll('svg[id^="mermaid"], .mermaid svg').length,
    proofs: document.querySelectorAll('.proof, [class*="prf"]').length, katex: document.querySelectorAll('.katex').length }));
  console.log(u, JSON.stringify(info));
}
console.log('page errors', errs.length, errs.slice(0, 3).join(' | '));
await b.close();
server.close();
