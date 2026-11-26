const pythonRuntime = 'https://cdn.jsdelivr.net/pyodide/v0.29.4/full/';

async function startPythonFrame(indexURL) {
  function report(type, message) {
    parent.postMessage({type, message}, '*');
  }

  async function receiveSketch(event) {
    if (event.source !== parent || event.data?.type !== 'run-python') return;
    window.removeEventListener('message', receiveSketch);
    const {source, filename, adapter} = event.data;
    try {
      const runtime = await loadPyodide({
        indexURL,
        stdout: text => report('sketch-output', text),
        stderr: text => console.warn(text)
      });
      runtime._api._skip_unwind_fatal_error = true;
      runtime.canvas.setCanvas2D(document.getElementById('canvas'));
      await runtime.loadPackage(['numpy', 'pygame-ce']);
      runtime.globals.set('sketch_source', source);
      runtime.globals.set('sketch_filename', filename);
      const launch = document.getElementById('launch-python');
      launch.disabled = false;
      launch.textContent = 'Start Python sketch';
      report('sketch-status', 'Click Start Python sketch to play and enable audio.');
      launch.addEventListener('click', async () => {
        launch.hidden = true;
        document.getElementById('canvas').focus();
        report('sketch-status', '');
        try {
          await runtime.runPythonAsync(adapter + '\nawait run_sketch(sketch_source, sketch_filename)');
          report('sketch-status', 'Python sketch ended.');
        } catch (error) {
          report('sketch-error', String(error).trim().split('\n').at(-1));
        }
      }, {once: true});
    } catch (error) {
      report('sketch-error', 'Python could not start. ' + error.message);
    }
  }
  window.addEventListener('message', receiveSketch);
  report('python-ready', '');
}

function pythonFramePage() {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none';
    script-src 'unsafe-inline' 'unsafe-eval' ${pythonRuntime}; connect-src ${pythonRuntime};
    style-src 'unsafe-inline'; img-src data: blob:; media-src data: blob:;
    worker-src blob:; base-uri 'none'; form-action 'none'">
    <style>
      html,body{margin:0;height:100%;background:#03030b;color:#f4f2ff}
      body{display:grid;place-items:center;overflow:hidden}
      canvas{display:block;max-width:100%;max-height:100%;object-fit:contain}
      button{position:absolute;padding:.75rem 1rem;background:#c9b4ff;color:#191226;
      border:0;border-radius:.5rem;font:600 1rem system-ui}
      button:disabled{opacity:.7}
    </style>
    <script src="${pythonRuntime}pyodide.js" crossorigin="anonymous"></script>
    </head><body><canvas id="canvas" tabindex="0" aria-label="Python sketch canvas"></canvas>
    <button type="button" id="launch-python" disabled>Loading Python and Pygame…</button>
    <script>(${startPythonFrame})(${JSON.stringify(pythonRuntime)});</script></body></html>`;
}
