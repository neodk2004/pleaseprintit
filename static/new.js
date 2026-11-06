// Neuer Auftrag: 3D-Datei schon im Browser ausmessen und gegen den Druckbereich prüfen; Ablagefeld.
import { fits, fmt, measure, parseBed, parseModel } from './model.js';

const form = document.getElementById('order');
const fileIn = form.elements.model;
const urlIn = form.elements.url;
const check = document.getElementById('check');
const submit = form.querySelector('button[type=submit]');
const bed = parseBed(form.dataset.bed);
const admin = form.dataset.admin === '1';
const MAX = 100 * 1024 * 1024;

function say(text, cls) { check.textContent = text; check.className = 'check ' + (cls || ''); }
function setDims(d) { ['x', 'y', 'z'].forEach((a, i) => { form.elements['dims_' + a].value = d ? d[i].toFixed(2) : ''; }); }

fileIn.addEventListener('change', async () => {
  setDims(null);
  submit.disabled = false;
  say('');
  const file = fileIn.files[0];
  if (!file) return;
  urlIn.value = '';                       // entweder Link oder Datei
  if (file.size > MAX) { say('✗ Die Datei ist größer als 100 MB.', 'bad'); submit.disabled = true; return; }
  say(`${file.name} wird ausgemessen …`);
  try {
    const kind = file.name.toLowerCase().endsWith('.3mf') ? '3mf' : 'stl';
    const d = measure(parseModel(await file.arrayBuffer(), kind));
    setDims(d);
    if (!bed.some((b) => b > 0)) return say(`Maße: ${fmt(d)} mm`, 'ok');
    if (fits(d, bed)) return say(`✓ Maße: ${fmt(d)} mm – passt aufs Druckbett`, 'ok');
    say(`✗ Maße: ${fmt(d)} mm – zu groß für den Druckbereich (${fmt(bed)} mm)` +
        (admin ? ' – als Werkstatt kannst du trotzdem anlegen.' : '. Bitte verkleinern oder teilen.'), 'bad');
    if (!admin) submit.disabled = true;
  } catch (err) {
    console.error(err);
    say('Die Datei konnte nicht gelesen werden. Ist es eine echte STL- oder 3MF-Datei?', 'bad');
  }
});

urlIn.addEventListener('input', () => {
  if (urlIn.value && fileIn.value) { fileIn.value = ''; setDims(null); say(''); submit.disabled = false; }
});

// Ablagefeld hervorheben, solange eine Datei darübergezogen wird (das Ablegen selbst übernimmt das Datei-Feld)
const drop = fileIn.closest('.drop');
for (const [ev, on] of [['dragenter', true], ['dragleave', false], ['drop', false]]) {
  fileIn.addEventListener(ev, () => drop.classList.toggle('over', on));
}
