// STEP lesen: occt-import-js (OpenCascade als WebAssembly, static/occt/) läuft abgeschottet in einem Web Worker.
// Die Bibliothek braucht eval; das erlaubt app.py nur für static/occt/, also nur im Worker, nie auf der Seite.
const WORKER = new URL('occt/occt-import-js-worker.js', import.meta.url);

/** Dreiecksnetze der STEP-Datei in mm: [{ attributes: { position, normal }, index }, …] */
export function readStep(buffer) {
  return new Promise((ok, fail) => {
    const w = new Worker(WORKER);
    w.onmessage = (ev) => {
      w.terminate();
      const r = ev.data;
      if (r && r.success && r.meshes.length) ok(r.meshes);
      else fail(new Error('STEP nicht lesbar'));
    };
    w.onerror = (ev) => { w.terminate(); fail(new Error(ev.message || 'STEP-Worker')); };
    const data = new Uint8Array(buffer);
    w.postMessage({ format: 'step', buffer: data, params: { linearUnit: 'millimeter' } }, [data.buffer]);
  });
}

/** Volumen in cm³ wie models.volume_cm3 in Python: Summe der Tetraeder (Ursprung, Dreieck). */
export function volumeCm3(meshes) {
  let t = 0;
  for (const m of meshes) {
    const p = m.attributes.position.array;
    const ix = m.index.array;
    for (let i = 0; i < ix.length; i += 3) {
      const a = ix[i] * 3, b = ix[i + 1] * 3, c = ix[i + 2] * 3;
      t += p[a] * (p[b + 1] * p[c + 2] - p[b + 2] * p[c + 1])
         - p[a + 1] * (p[b] * p[c + 2] - p[b + 2] * p[c])
         + p[a + 2] * (p[b] * p[c + 1] - p[b + 1] * p[c]);
    }
  }
  return Math.abs(t) / 6 / 1000;
}
