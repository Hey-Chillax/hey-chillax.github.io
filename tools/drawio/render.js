// Render webified diagram SVGs the way the homepage shows them: inline, with the site's Comic Neue ('YZ Hand')
// and the --dg-* colour variables, at the figure's display width, light or dark page. Usage: node render.js job.json
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const FONTS = path.resolve(__dirname, '..', '..', 'assets', 'fonts');
const css = fs.readFileSync(job.css, 'utf8');
const face = (w, f) => `@font-face{font-family:'YZ Hand';font-weight:${w};src:url('file://${FONTS}/${f}') format('woff2');}`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 1200, height: 900 } });
  let n = 0;
  for (const it of job.items) {
    const svg = fs.readFileSync(it.svg, 'utf8');
    const bg = it.theme === 'dark' ? '#111317' : '#ffffff';
    const scheme = it.theme === 'dark' ? 'dark' : 'light';
    await p.emulateMedia({ colorScheme: scheme });
    const html = `<!doctype html><meta charset="utf-8"><style>${face(400, 'ComicNeue-Regular.woff2')}${face(700, 'ComicNeue-Bold.woff2')}
      ${css} html,body{margin:0;background:${bg}} .pad{display:inline-block;padding:14px;background:${bg}}
      .pad svg{display:block;width:${it.width}px;height:auto}</style><div class="pad">${svg}</div>`;
    const tmp = path.join(path.dirname(it.png), '.render.html');
    fs.writeFileSync(tmp, html);
    await p.goto('file://' + tmp);
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150);
    await (await p.$('.pad')).screenshot({ path: it.png });
    fs.unlinkSync(tmp);
    n++;
  }
  await b.close();
  console.log(`rendered ${n} previews`);
})();
