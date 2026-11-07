// Renderiza scenes.html quadro a quadro (30 fps) e envia ao ffmpeg por pipe.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
(async () => {
  const T = JSON.parse(fs.readFileSync('timing.json')); const FPS = 30, N = Math.ceil(T.total * FPS);
  const ff = spawn('ffmpeg', ['-y','-v','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-',
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','video_mudo.mp4'], { stdio: ['pipe','inherit','inherit'] });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + process.cwd() + '/scenes.html'); await p.evaluate(t => setTiming(t), T);
  for (let f = 0; f < N; f++) {
    await p.evaluate(t => render(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 300 === 0) console.log(`quadro ${f}/${N}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('ok');
})();
