const byId = id => document.getElementById(id);
const stage = byId('stage');
const canvas = byId('galaxy');
const poster = byId('poster');
const play = byId('play');
const stop = byId('stop');
const code = byId('code');
const language = byId('language');
const status = byId('status');
let galaxy;
let sketch;
let pythonRequest;
let filename = '';

code.value = `const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
canvas.width = 780;
canvas.height = 480;

function draw(time) {
  ctx.fillStyle = '#080611';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (let i = 0; i < 500; i++) {
    const angle = i * 2.39996 + time * 0.00025;
    const radius = Math.sqrt(i) * 9;
    const x = 390 + Math.cos(angle) * radius;
    const y = 240 + Math.sin(angle) * radius;
    ctx.fillStyle = 'hsl(' + (260 + i % 110) + ' 90% 72%)';
    ctx.fillRect(x, y, 2, 2);
  }
  requestAnimationFrame(draw);
}

requestAnimationFrame(draw);`;

try {
  galaxy = createGalaxy(canvas);
} catch {
  play.disabled = true;
  status.textContent = 'Canvas is unavailable. The still preview is shown.';
}

play.addEventListener('click', () => {
  if (galaxy.playing) {
    galaxy.pause();
    play.textContent = 'Resume galaxy';
    return;
  }
  poster.hidden = true;
  canvas.hidden = false;
  galaxy.play();
  play.textContent = 'Pause galaxy';
});

function removeSketch() {
  sketch?.remove();
  sketch = undefined;
  pythonRequest = undefined;
}

function displayGalaxy() {
  removeSketch();
  byId('piece').textContent = 'Spiral Galaxy';
  byId('format').textContent = 'Canvas';
  poster.hidden = false;
  canvas.hidden = true;
  play.textContent = 'Play galaxy';
  play.hidden = false;
  stop.hidden = true;
  status.textContent = galaxy ? '' : 'Canvas is unavailable.';
}

stop.addEventListener('click', displayGalaxy);

byId('run').addEventListener('click', () => {
  if (!code.value.trim()) {
    status.textContent = 'Add some sketch source first.';
    code.focus();
    return;
  }
  removeSketch();
  galaxy?.pause();
  canvas.hidden = true;
  poster.hidden = true;
  play.hidden = true;
  stop.hidden = false;
  byId('piece').textContent = 'Your sketch';
  byId('format').textContent = language.options[language.selectedIndex].text;
  status.textContent = '';

  if (language.value === 'py') {
    status.textContent = 'Loading Python and Pygame…';
    pythonRequest = {
      source: code.value,
      filename: filename.endsWith('.py') ? filename : 'sketch.py'
    };
    sketch = document.createElement('iframe');
    sketch.title = 'Python sketch preview';
    sketch.setAttribute('sandbox', 'allow-scripts');
    sketch.srcdoc = pythonFramePage();
    stage.append(sketch);
    return;
  }

  const source = JSON.stringify(code.value).replaceAll('<', '\\u003c');
  const errorHook = `<script>
    const report = message => parent.postMessage({type:'sketch-error', message}, '*');
    addEventListener('error', event => report(event.message || 'A resource could not load.'));
    addEventListener('unhandledrejection', event => report(String(event.reason)));
  </script>`;
  const policy = `<meta charset="utf-8"><meta http-equiv="Content-Security-Policy"
    content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';
    img-src data: blob:; media-src data: blob:; font-src data:; connect-src 'none';
    base-uri 'none'; form-action 'none'">`;
  const canvasPage = `<style>
    html,body{margin:0;height:100%;background:#03030b}
    canvas{width:100%;height:100%;object-fit:contain}
  </style><canvas></canvas><script>
    const script = document.createElement('script');
    script.textContent = ${source};
    document.body.appendChild(script);
  </script>`;
  sketch = document.createElement('iframe');
  sketch.title = 'Sketch preview';
  sketch.setAttribute('sandbox', 'allow-scripts');
  sketch.srcdoc = policy + errorHook + (language.value === 'html' ? code.value : canvasPage);
  stage.append(sketch);
});

window.addEventListener('message', async event => {
  if (!sketch || event.source !== sketch.contentWindow) return;
  if (['sketch-error', 'sketch-status', 'sketch-output'].includes(event.data?.type)) {
    status.textContent = String(event.data.message).slice(0, 500);
  }
  if (event.data?.type === 'python-ready' && pythonRequest) {
    const frame = sketch;
    const request = pythonRequest;
    pythonRequest = undefined;
    try {
      const response = await fetch('python-loop.py');
      if (!response.ok) throw new Error('Adapter unavailable');
      const adapter = await response.text();
      if (sketch === frame) {
        frame.contentWindow.postMessage({type: 'run-python', ...request, adapter}, '*');
      }
    } catch {
      if (sketch === frame) status.textContent = 'The Python adapter could not load.';
    }
  }
});

byId('backroom').addEventListener('click', async () => {
  try {
    const response = await fetch('backroom.py');
    if (!response.ok) throw new Error('Source unavailable');
    code.value = await response.text();
    language.value = 'py';
    filename = 'backroom.py';
    status.textContent = 'Backrooms loaded. Select Run sketch to preview it.';
  } catch {
    status.textContent = 'Backrooms source could not load.';
  }
});

byId('file').addEventListener('change', async event => {
  const input = event.currentTarget;
  const [file] = input.files;
  input.value = '';
  if (!file) return;
  const extension = file.name.split('.').at(-1).toLowerCase();
  if (!['py', 'js', 'html', 'htm'].includes(extension)) {
    status.textContent = 'Choose a .py, .js, or .html file.';
    return;
  }
  try {
    code.value = await file.text();
    filename = file.name;
    language.value = extension === 'htm' ? 'html' : extension;
    status.textContent = 'File loaded. Select Run sketch to preview it.';
  } catch {
    status.textContent = 'The file could not be read.';
  }
});

byId('download').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([code.value], {type: 'text/plain;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'sketch.' + language.value;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

const expand = byId('expand');
expand.hidden = !document.fullscreenEnabled;
expand.addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await stage.requestFullscreen();
  } catch {
    status.textContent = 'Full screen is unavailable in this browser.';
  }
});
