// Bild aus der Zwischenablage (Strg+V) ins Bildfeld der Seite einsetzen; das Formular prüft Typ und Größe wie sonst.
document.addEventListener('paste', (ev) => {
  const file = [...(ev.clipboardData?.files || [])].find((f) => f.type.startsWith('image/'));
  const input = document.querySelector('input[type=file][name=image]');
  if (!file || !input) return;
  const dt = new DataTransfer();
  dt.items.add(file);
  input.files = dt.files;
  input.closest('details')?.setAttribute('open', '');
  input.dispatchEvent(new Event('change', { bubbles: true }));
  ev.preventDefault();
});
