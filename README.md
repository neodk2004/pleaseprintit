# PleasePrintit

Kleine Druck-Werkstatt für den eigenen 3D-Drucker: Freunde reichen Druckwünsche ein (Link zu Printables, MakerWorld, Thingiverse oder eine STL-/3MF-Datei), du siehst eine Vorschau und arbeitest die Aufträge sortiert ab.

## Starten

Du brauchst Docker mit Compose.

```sh
git clone <repo-url> pleaseprintit
cd pleaseprintit
cp .env.example .env        # dann ADMIN_PASSWORD und SECRET_KEY ändern
mkdir -p data backups
sudo chown 1000:1000 data backups   # nur Linux: die App läuft im Container als Benutzer 1000
docker compose up -d --build
```

Danach läuft die App unter `http://<dein-rechner>:8080`. Melde dich mit dem Namen **admin** und deinem `ADMIN_PASSWORD` an.

## Erste Schritte als Admin

1. Unter **Einstellungen** dein Druckbett, deine Filamente und das Impressum eintragen.
2. Unter **Nutzer** für jeden Freund eine **Einladung** erstellen und ihm den Link schicken. Ein Link gilt 7 Tage und nur einmal.

## Von außen erreichbar machen

Stell die App hinter einen Reverse Proxy mit HTTPS, z. B. Nginx Proxy Manager, Caddy oder Traefik, und trag die Adresse als `PUBLIC_URL` in die `.env` ein. Ist der Proxy da, kann der Port in `compose.yaml` auf `127.0.0.1:8080:8000` beschränkt werden.

## Daten und Sicherung

- Alle Daten liegen in `./data` (Datenbank, Vorschaubilder, 3D-Dateien).
- Der `backup`-Container legt täglich eine Sicherung in `./backups` ab, die letzten 14 bleiben.
- Sofort sichern: `docker compose run --rm backup python backup.py --once`
- Sicherung prüfen: `docker compose run --rm backup python backup.py --check /backups/<datei>.tar.gz`
- Wiederherstellen: App stoppen, Archiv nach `./data` auspacken, App starten.

## Update

```sh
git pull
docker compose up -d --build
```

## Tests

```sh
pip install -r requirements.txt
python test_app.py && python test_models.py && python test_preview.py
```
