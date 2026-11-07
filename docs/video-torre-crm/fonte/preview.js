const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const T = JSON.parse(fs.readFileSync('timing.json'));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + process.cwd() + '/scenes.html'); await p.evaluate(t => setTiming(t), T);
  for (const [i, sc] of T.scenes.entries()) {
    const t = sc.start + sc.dur - 1.0;
    await p.evaluate(t => render(t), t);
    await p.screenshot({ path: `prev_${i}.jpg`, type: 'jpeg', quality: 70 });
  }
  await b.close();
})();
