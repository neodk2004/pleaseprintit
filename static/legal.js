// Impressum erst im Browser zusammensetzen: Im HTML steht nur ein verdrehter Base64-Text (siehe scramble() in app.py).
// Adress- und Mail-Sammler, die kein JavaScript ausführen, finden so weder Name noch Anschrift noch E-Mail.
const box = document.getElementById('imp');
if (box && box.dataset.blob) {
  const bytes = Uint8Array.from(atob(box.dataset.blob.split('').reverse().join('')), (c) => c.charCodeAt(0));
  const d = JSON.parse(new TextDecoder().decode(bytes));
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text) e.textContent = text; if (cls) e.className = cls; return e; };
  const block = (title, lines) => {
    const s = el('section');
    s.append(el('h3', title));
    for (const l of lines.filter(Boolean)) s.append(typeof l === 'string' ? el('p', l) : l);
    return s;
  };
  const mail = el('p');
  if (d.imp_email) {
    const a = el('a', d.imp_email);
    a.href = 'mailto:' + d.imp_email;
    mail.append('E-Mail: ', a);
  }
  box.replaceChildren(
    block('Angaben gemäß § 5 DDG', [d.imp_name, d.imp_street, d.imp_city]),
    block('Kontakt', [d.imp_email && mail, d.imp_phone && 'Telefon: ' + d.imp_phone]),
    block('Verantwortlich für den Inhalt', [d.imp_name + ', Anschrift wie oben']),
    el('p', 'Privates, nicht-kommerzielles Angebot für einen geschlossenen Freundeskreis.', 'muted'),
  );
}
