// Gemeinsam für 3D-Ansicht und Upload-Prüfung: Modell aus Bytes laden, ausmessen, mit Druckbereich vergleichen.
import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { ThreeMFLoader } from 'three/addons/loaders/3MFLoader.js';

const MATERIAL = new THREE.MeshStandardMaterial({ color: 0xf07a2a, roughness: 0.55 }); // Filament-Orange

export function parseModel(buffer, kind) {
  if (kind === 'stl') {
    const geo = new STLLoader().parse(buffer);
    geo.computeVertexNormals();
    return new THREE.Mesh(geo, MATERIAL);
  }
  // ponytail: 3MF-Einheit wird als mm angenommen (Standard); "inch"-Dateien zeigen falsche Maße
  const group = new ThreeMFLoader().parse(buffer);
  // Ohne Farbangabe liefert der Loader Weiß – auf hellem Grund unsichtbar
  group.traverse((o) => {
    if (o.isMesh && o.material.color?.getHex() === 0xffffff) o.material = MATERIAL;
  });
  return group;
}

/** Maße [x, y, z] in mm, in den Koordinaten der Datei (3D-Druck: Z ist oben). */
export function measure(object) {
  const s = new THREE.Box3().setFromObject(object).getSize(new THREE.Vector3());
  return [s.x, s.y, s.z];
}

/** Wie models.fits() in Python: Drehen erlaubt (sortiert vergleichen); 0 = keine Grenze. */
export function fits(dims, bed) {
  if (!bed.every((b) => b > 0)) return dims.every((d, i) => !bed[i] || d <= bed[i]);
  const a = [...dims].sort((x, y) => x - y), b = [...bed].sort((x, y) => x - y);
  return a.every((d, i) => d <= b[i] + 0.01);
}

// Texte in der gewählten Sprache: base.html legt die nötigen Übersetzungen als JSON ab (#i18n)
const T = JSON.parse(document.getElementById('i18n')?.textContent || '{}');
export const t = (s, vars = {}) => (T[s] || s).replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m));
const LOCALE = { de: 'de-DE', en: 'en-GB', fr: 'fr-FR' }[document.documentElement.lang] || 'de-DE';
export const mm = (v) => v.toLocaleString(LOCALE, { maximumFractionDigits: 1 });
export const fmt = (d) => d.map(mm).join(' × ');
export const parseBed = (s) => (s || '0,0,0').split(',').map(Number);
