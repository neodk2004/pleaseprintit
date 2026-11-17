# Änderungen

🇬🇧 [English version](CHANGELOG.en.md)

Alle wichtigen Änderungen an PleasePrintit. Versionen folgen [Semantic Versioning](https://semver.org/lang/de/), das fertige Image gibt es unter `ghcr.io/neodk2004/pleaseprintit`.

## [Unreleased]

### Neu
- **Mail an die Werkstatt bei neuem Druckwunsch:** Adresse in Einstellungen → Werkstatt eintragen. Leer = keine Mails.
- **Rückfragen am Auftrag:** Freund und Werkstatt schreiben sich direkt am Auftrag, die jeweils andere Seite bekommt eine Mail. Schluss mit „Welche Größe?“ im Chat.
- **Interne Notiz:** ein Textfeld am Auftrag, das nur die Werkstatt sieht, z. B. für Druckeinstellungen.
- **Platz in der Warteschlange:** Freunde sehen „Platz 3 in der Warteschlange“. Geplantes zählt vor Neuem.
- **Nochmal drucken:** Gedruckte Aufträge lassen sich mit einem Klick erneut bestellen. Datei, Bild und Filament werden übernommen.
- **Foto vom fertigen Druck:** Die Werkstatt lädt ein Foto hoch. Der Freund sieht es im Auftrag und bekommt es als Anhang der Mail „Gedruckt“.
- **Mails pausieren:** Freunde (Profil) und Werkstatt (Einstellungen) können Mails abschalten, ohne die Adresse zu löschen.

### Behoben
- gunicorn 27 meldete beim Start `Control server error: Read-only file system`. Die nicht benötigte Steuer-Schnittstelle ist jetzt abgeschaltet (`--no-control-socket`).

### Sicherheit
- gunicorn 26.2.0 → 27.0.0 (strengere Prüfung von HTTP-Anfragen).

## [1.2.0] – 2026-11-09

### Neu
- **„In Slicer öffnen“:** Knöpfe im Auftrag öffnen die 3D-Datei direkt in OrcaSlicer, Bambu Studio oder Creality Print am PC. Welche Knöpfe erscheinen, wählst du in Einstellungen → Werkstatt. Der Slicer holt die Datei über einen signierten Link, der eine Stunde gilt.

## [1.1.0] – 2026-11-07

### Neu
- **Archiv mit Suche:** Gedruckte und abgelehnte Aufträge wandern nach einer einstellbaren Frist (Standard 14 Tage, 0 = nur per Knopf) oder per Knopf ins Archiv, auch mehrere auf einmal. Suche nach Titel, Datei, Freund und Zeitraum. Freunde merken davon nichts.
- **Statistik:** Aufträge, Gramm und Materialkosten pro Monat, beliebte Filamente und Farben, Wartezeit und Ablehnungsgründe für die Werkstatt. Jeder Freund sieht seine eigenen Zahlen im Profil.
- **Trinkgeld-Knopf:** Eigener Link (PayPal.me, Ko-fi …) erscheint bei gedruckten Aufträgen. Die App selbst verarbeitet kein Geld.
- **STEP-Dateien** aus CAD-Programmen mit 3D-Vorschau, Maßen und Volumen, direkt im Browser gelesen.

### Geändert
- Einstellungen in vier Tabs: Drucker, Filamente, Werkstatt, Rechtliches.
- Neue Filamente aus einer festen Sortenliste (14 Sorten) mit vorausgefüllter Dichte statt Freitext.

### Behoben
- Abgelehnte Aufträge mit Begründung ließen sich in der Werkstatt nicht öffnen (Fehler 500).

### Sicherheit
- Der STEP-Leser (occt-import-js 0.0.23, LGPL-2.1) läuft abgeschottet in einem Web Worker. Nur dort ist `eval` erlaubt, alle Seiten bleiben ohne.

## [1.0.0] – 2026-11-07

Erste Version zum Selbsthosten.

### Funktionen
- **Aufträge per Link oder Datei:** Link zu Printables, MakerWorld oder Thingiverse (Titel und Vorschaubild werden geholt) oder eigene STL- bzw. 3MF-Datei.
- **3D-Vorschau im Browser** mit Maßen und Prüfung, ob das Modell aufs Druckbett passt.
- **Filamente und Farben** aus deinem Bestand, auf Wunsch „Zufällig“. Mit Preis pro kg gibt es eine Schätzung der Materialkosten.
- **„Für dich gedruckt“:** Teile, Gewicht und Materialkosten pro Freund im Profil und in der Freundesliste.
- **Klarer Status:** eingereicht → geplant → gedruckt, oder abgelehnt mit Grund. Optional Benachrichtigung per E-Mail.
- **Nur auf Einladung:** Einladungslinks gelten 7 Tage und einmal. Konten lassen sich sperren, „Passwort vergessen“ per E-Mail.
- **Faire Grenzen:** höchstens 10 offene Aufträge und 500 MB 3D-Dateien pro Person.
- **Deutsch, Englisch, Französisch** für die ganze App, Mails immer in der Sprache des Empfängers.
- **Handyfreundlich:** auf dem Startbildschirm installierbar (PWA), helles und dunkles Design.
- **Impressum und Datenschutz** eingebaut, für Adress-Sammler unlesbar.
- **Läuft fast überall:** fertiges Image für x86 und ARM64 (auch Raspberry Pi 4/5), SQLite statt Datenbankserver, ca. 50 MB RAM.
- **Tägliche Sicherung** mit Prüfwerkzeug, die letzten 14 bleiben erhalten.
- **Sicher von Haus aus:** SSRF-Schutz beim Laden von Vorschauen, CSP- und HSTS-Header, Bremse gegen Passwort-Raten, Container ohne Zusatzrechte mit schreibgeschütztem Dateisystem.

### Rund ums Projekt
- Installation mit Docker Compose oder Dockhand, Anleitung auf Deutsch und Englisch.
- Tests, Compose-Prüfung und Docker-Probestart per GitHub Actions, Dependabot für Abhängigkeiten.
- MIT-Lizenz, `SECURITY.md`, Issue-Vorlagen und `AGENTS.md`.

[Unreleased]: https://github.com/neodk2004/pleaseprintit/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/neodk2004/pleaseprintit/releases/tag/v1.0.0
