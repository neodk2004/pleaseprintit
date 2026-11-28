# Änderungen

🇬🇧 [English version](CHANGELOG.en.md)

Alle wichtigen Änderungen an PleasePrintit. Versionen folgen [Semantic Versioning](https://semver.org/lang/de/), das fertige Image gibt es unter `ghcr.io/neodk2004/pleaseprintit`.

## [Unreleased]

## [1.7.2] – 2026-11-28

### Neu
- **Titel nachträglich ändern:** Im Auftrag gibt es die Karte „Titel ändern“ (Freunde bei ihren eigenen Aufträgen, die Werkstatt bei allen). Praktisch, wenn die Vorschau nicht klappt, etwa bei MakerWorld. Idee von maume86 (#17), danke!
- **Bild aus der Zwischenablage:** Ein kopiertes Bild lässt sich mit Strg+V direkt einfügen, beim neuen Auftrag und bei „Vorschaubild ersetzen“. Das Bild muss nicht erst als Datei gespeichert werden. Typ und Größe (bis 5 MB) prüft der Server wie bisher.
- **GitHub-Link im Fuß:** Die Werkstatt sieht unten einen kurzen Weg zum Projekt auf GitHub. Freunde sehen ihn nicht.

### Geändert
- „Titel ändern“ und „Vorschaubild ersetzen“ stehen jetzt gleich unter den Auftragsdaten, man muss nicht mehr scrollen.

## [1.7.1] – 2026-11-27

### Geändert
- **Einstellungen übersichtlicher:** Der volle Tab „Werkstatt“ ist in drei Tabs geteilt: „Werkstatt“ (Archiv, Währung, Limit, Vorab zahlen, Trinkgeld), „Benachrichtigungen“ (Mail, ntfy) und „Vorschau & Slicer“. Speichern führt in den jeweils richtigen Tab zurück.

## [1.7.0] – 2026-11-27

### Neu
- **Push-Nachrichten über ntfy:** Bei neuen Druckwünschen und Rückfragen bekommt die Werkstatt auf Wunsch eine Push-Nachricht aufs Handy, über ntfy.sh oder den eigenen ntfy-Server (auch im Heimnetz). Einrichten unter Einstellungen → Werkstatt → Push-Nachricht über ntfy: Adresse des Themas, optional Zugangstoken oder Benutzer:Passwort (verschlüsselt gespeichert, `NTFY_TOKEN` in der `.env` hat Vorrang), Knopf für eine Testnachricht, pausierbar. Funktioniert auch ohne Mailversand. Keine neue Abhängigkeit. Idee und Grundstock von GhostService (PR #18), danke!

## [1.6.2] – 2026-11-24

### Neu
- **Vorschau für Thingiverse und Cults3D:** Mit einem eigenen, kostenlosen Zugang (Thingiverse-App-Token, Cults3D-Nickname mit API-Schlüssel) holt die App Titel und Bild über deren offizielle Schnittstellen. Ohne Zugang bleibt alles wie bisher. Eine kurze Anleitung steht im README.
- **Zugänge in den Einstellungen:** Unter Einstellungen → Werkstatt → Link-Vorschau trägst du die Zugänge direkt in der Weboberfläche ein, ohne Docker-Kenntnisse. Sie werden **verschlüsselt** gespeichert (abgeleitet aus `SECRET_KEY`) und nie wieder angezeigt. Variablen in der `.env` (`THINGIVERSE_TOKEN`, `CULTS3D_USER`, `CULTS3D_KEY`) haben weiter Vorrang. Neue Abhängigkeit: `cryptography`.

## [1.6.1] – 2026-11-24

### Behoben
- **Vorschau bei Printables-Links:** Printables sperrt den Abruf der Webseite. Titel und Bild kommen jetzt über dessen Schnittstelle, die Vorschau funktioniert wieder.
- **MakerWorld:** Die Seite sperrt den automatischen Abruf weiterhin. Beim Einreichen lässt sich jetzt **ein eigenes Bild** hochladen (aufklappbar unter dem Link), der Titel kommt aus dem Titelfeld. Der automatische Abruf folgt, sobald er möglich ist.

### Geändert
- **Bilder klein als WebP:** Vorschaubilder werden auf höchstens 800 Pixel verkleinert und als WebP gespeichert (statt Originale von mehreren MB). Neue Abhängigkeit: Pillow.
- Der Abruf meldet sich mit einem eigenen, ehrlichen Namen (`PleasePrintit-LinkPreview`).
- Aufräumarbeiten im Code (Zahlen-Eingaben, Geld-Anzeige).

## [1.6.0] – 2026-11-22

### Neu
- **Währung einstellbar:** In Einstellungen → Werkstatt wählst du die Währung (EUR, USD, GBP, CHF, CAD, AUD, SEK, NOK, DKK, PLN, CZK). Euro zeigt weiter „€“, alle anderen ihr Kürzel, z. B. „12,50 USD“. Es wird nichts umgerechnet.
- **Status-Bereich aufgeräumt:** Die Werkstatt sieht nur noch den **nächsten Schritt** (Annehmen → Gedruckt → Unterwegs → Zugestellt). Das Feld für die Sendungsnummer erscheint nur, wenn es gebraucht wird. „Ablehnen“ ist aufklappbar. Die freie Auswahl aller Status gibt es weiter als „Status frei ändern (Korrektur)“.

Danke an @dexxfm für beide Ideen.

## [1.5.1] – 2026-11-22

### Behoben
- **Klare Fehlermeldungen:** Fehler erscheinen jetzt als normale Seite der App mit verständlichem Text und einem Knopf zurück zur Übersicht, nicht mehr als rohes „Bad Request“. Neu verständlich sind unter anderem ungültige Zahlen bei Preis, Guthaben und Aufschlag sowie eine abgelaufene Sitzung.
- **Preis aushandeln:** Hat der Freund ein Angebot nicht beantwortet (oder gar keine Mail), kommt die Werkstatt jetzt weiter: Mit **„Als abgemacht eintragen“** hält sie eine mündliche Einigung fest. Vorher blieb der Auftrag bei „Der Preis ist noch nicht abgemacht“ hängen.

## [1.5.0] – 2026-11-22

### Neu
- **Versand:** Nach „Gedruckt“ gibt es die Schritte **Unterwegs** und **Zugestellt**, mit Status-Mail an den Freund. Beim Setzen auf „Unterwegs“ trägst du eine **Sendungsnummer oder einen Verfolgungs-Link** ein. Sie steht in der Mail und im Auftrag, ein Link wird klickbar. Wer abholt, sieht weiter nur die bisherigen Schritte.
- **Preis aushandeln:** Die Werkstatt schickt ein Angebot, der Freund nimmt an oder macht einen Gegenvorschlag, die Werkstatt nimmt ihn an oder schickt ein neues Angebot. Bis der Preis abgemacht ist, wird nicht geplant, gedruckt oder abgebucht. Beide Seiten bekommen eine Mail.
- **Limit offener Aufträge einstellbar:** In Einstellungen → Werkstatt legst du fest, wie viele Aufträge ein Freund gleichzeitig offen haben darf. Der Standard ist jetzt **50** statt 10.
- **Status-Mails im neuen Design:** Die Ablauf-Leiste in den Mails zeigt Sechsecke mit dem Filament-Faden wie in der App, auch mit den Versand-Schritten.

Danke an @dexxfm für die Ideen zu Versand und Preisabsprache.

## [1.4.0] – 2026-11-21

### Neu
- **Vorab zahlen (optional):** In Einstellungen → Werkstatt wählst du den Modus: aus, **Haken pro Auftrag** oder **Guthaben-Konto**. Eingeschaltet wird es pro Freund auf der Freunde-Seite. Der Preis ist Filamentkosten plus ein Aufschlag in Prozent (Startwert 30 %) für Strom, Verschleiß und Ausschuss; ohne Volumen oder Preis pro kg legst du ihn am Auftrag selbst fest.
  - Ohne Zahlung lässt sich ein Auftrag nicht auf „Geplant“ setzen.
  - Beim Guthaben bucht die App beim Einreichen ab, sobald es reicht, und bucht abgelehnte Aufträge zurück. Freunde sehen Kontostand und Verlauf im Profil.
  - Das Geld läuft außerhalb der App (bar, PayPal), sie rechnet und merkt sich nur den Stand.
- **Neue Ablauf-Leiste:** Sechsecke mit einem Filament-Faden, der von Schritt zu Schritt dicker wird. Die Schritte erscheinen nacheinander mit Animation.
- **Animierte Icons:** Alle Icons bewegen sich beim Überfahren von Knöpfen, Links und Tabs. Mit „Bewegung reduzieren“ im System bleibt alles ruhig.

### Sicherheit
- Bei STEP-Dateien kommt das Volumen vom Browser des Freundes. Der Preis wird daraus nie berechnet, die Werkstatt legt ihn fest.

## [1.3.0] – 2026-11-17

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

[Unreleased]: https://github.com/neodk2004/pleaseprintit/compare/v1.7.2...HEAD
[1.7.2]: https://github.com/neodk2004/pleaseprintit/compare/v1.7.1...v1.7.2
[1.7.1]: https://github.com/neodk2004/pleaseprintit/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.6.2...v1.7.0
[1.6.2]: https://github.com/neodk2004/pleaseprintit/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/neodk2004/pleaseprintit/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/neodk2004/pleaseprintit/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/neodk2004/pleaseprintit/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/neodk2004/pleaseprintit/releases/tag/v1.0.0
