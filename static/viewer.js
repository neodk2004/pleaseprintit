import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { fits, fmt, measure, parseBed, parseModel } from './model.js';

const box = document.getElementById('viewer');
const dims = document.getElementById('dims');
const { src, kind, thumb } = box.dataset;
const bed = parseBed(box.dataset.bed);

// Transparenter Hintergrund: das Druckbett-Raster aus dem CSS scheint durch; Vorschaubilder passen zu Hell und Dunkel
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setClearColor(0x000000, 0);
renderer.setPixelRatio(window.devicePixelRatio);
box.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xffffff, 0x888888, 2));
const camera = new THREE.PerspectiveCamera(40, 16 / 9, 0.1, 100000);
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(1, 2, 3);
camera.add(sun);
scene.add(camera);

const controls = new OrbitControls(camera, renderer.domElement);
const render = () => renderer.render(scene, camera);
controls.addEventListener('change', render);

new ResizeObserver(() => {
  renderer.setSize(box.clientWidth, box.clientHeight);
  camera.aspect = box.clientWidth / box.clientHeight;
  camera.updateProjectionMatrix();
  render();
}).observe(box);

function show(object) {
  const size = measure(object);
  const limited = bed.some((b) => b > 0);
  dims.textContent = `Maße: ${fmt(size)} mm (B × T × H)`;
  if (limited) {
    const ok = fits(size, bed);
    const tag = document.createElement('span');
    tag.className = ok ? 'fit ok' : 'fit bad';
    tag.textContent = ok ? '✓ passt aufs Druckbett' : `✗ größer als Druckbereich (${fmt(bed)} mm)`;
    dims.append(' ', tag);
  }

  object.rotation.x = -Math.PI / 2; // Z-oben (Drucker) → Y-oben (three.js)
  const wrap = new THREE.Group();
  wrap.add(object);
  const center = new THREE.Box3().setFromObject(wrap).getCenter(new THREE.Vector3());
  object.position.sub(center);
  scene.add(wrap);

  const r = Math.max(...size) || 1;
  camera.position.set(r * 1.2, r * 0.9, r * 1.6);
  controls.target.set(0, 0, 0);
  controls.update();
  render();

  if (thumb) {
    renderer.domElement.toBlob((blob) => {
      const fd = new FormData();
      fd.append('image', blob, 'vorschau.png');
      fetch(thumb, { method: 'POST', body: fd });
    }, 'image/png');
  }
}

fetch(src)
  .then((r) => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
  .then((buf) => show(parseModel(buf, kind)))
  .catch((err) => { dims.textContent = 'Modell konnte nicht angezeigt werden.'; console.error(err); });
