// Screenshot Plotly specs (from tests/extract_fig_specs.py) at several widths, using the same wide/narrow
// switch as qcai.viz.show. Usage: node tests/render_figs.mjs specs.json outdir [width ...]
import { chromium } from 'playwright';
import fs from 'node:fs';
const [specFile, outDir, ...ws] = process.argv.slice(2);
const widths = ws.length ? ws.map(Number) : [740, 390];
const figs = JSON.parse(fs.readFileSync(specFile, 'utf8'));
const browser = await chromium.launch({ channel: 'msedge' });
for (const w of widths) {
  const page = await browser.newPage({ viewport: { width: w + 40, height: 900 } });
  await page.setContent('<html><body style="margin:20px;background:#fff"><div id="p"></div></body></html>');
  await page.addScriptTag({ url: 'https://cdn.plot.ly/plotly-2.35.2.min.js' });
  for (const f of figs) {
    await page.evaluate(async ({ spec, h }) => { const el = document.getElementById('p'); Plotly.purge(el); el.style.width = '100%';
      const m = (spec.layout.meta || {}).qcai; const cur = m ? (el.clientWidth < m.narrowAt ? m.narrow : m.wide) : null;
      el.style.height = (cur ? cur.height : h) + 'px';
      await Plotly.newPlot(el, spec.data, spec.layout, { responsive: true, displaylogo: false });
      if (cur && cur !== m.wide) await Plotly.relayout(el, cur); }, f);
    await page.waitForTimeout(250);
    await (await page.$('#p')).screenshot({ path: `${outDir}/${f.name}_w${w}.png` });
  }
  await page.close();
}
await browser.close();
console.log('rendered', figs.length * 2);
