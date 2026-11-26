"""Push-Nachrichten an die Werkstatt über ntfy (ntfy.sh oder ein eigener Server), nur Standardbibliothek.
Die Werkstatt trägt in den Einstellungen die Adresse ihres Themas ein, z. B. https://ntfy.example.org/druck,
dazu optional einen Zugangstoken (tk_…) oder Benutzer:Passwort. Ohne Adresse ist der Versand abgeschaltet.
Bewusst ohne SSRF-Sperre wie in preview.py: Die Adresse setzt nur die Werkstatt, und ein eigener ntfy-Server
steht oft im Heimnetz."""
import base64
import json
import logging
import re
import threading
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit

log = logging.getLogger("ntfy")
TOPIC_RE = re.compile(r"[-_A-Za-z0-9]{1,64}")   # so erlaubt ntfy Themen-Namen


def split(url):
    """Themen-Adresse → (Server-Adresse mit / am Ende, Thema) oder None, wenn sie nicht passt."""
    try:
        p = urlsplit(url.strip())
        p.port   # wirft ValueError bei kaputtem Port
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.query or p.fragment:
        return None
    base, _sep, topic = p.path.rstrip("/").rpartition("/")
    if not TOPIC_RE.fullmatch(topic):
        return None
    return urlunsplit((p.scheme, p.netloc, base + "/", "", "")), topic


def auth_header(token):
    """Zugangstoken → Bearer, „Benutzer:Passwort“ → Basic (ntfy-Tokens enthalten nie einen Doppelpunkt)."""
    if not token:
        return None
    if ":" in token:
        return "Basic " + base64.b64encode(token.encode()).decode()
    return "Bearer " + token


def request(url, token, msg):
    """Baut die Anfrage. Veröffentlicht als JSON an die Server-Adresse, so sind Umlaute und Emojis im Titel kein Problem
    (in HTTP-Kopfzeilen wären sie es)."""
    server, topic = split(url)
    req = urllib.request.Request(server, data=json.dumps({"topic": topic, **msg}).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "PleasePrintit"})
    if auth := auth_header(token):
        req.add_header("Authorization", auth)
    return req


def send_now(url, token, msg):
    """Sofort verschicken; gibt None oder die Fehlermeldung zurück (ohne Zugangsdaten)."""
    if not split(url):
        return "invalid url"
    try:
        with urllib.request.urlopen(request(url, token, msg), timeout=10) as r:
            r.read(4096)
        log.info("ntfy-Nachricht an %s verschickt", url)
        return None
    except (OSError, ValueError) as e:   # URLError/HTTPError sind OSError
        log.warning("ntfy-Nachricht an %s fehlgeschlagen: %s", url, e)
        # „HTTP Error 403: Forbidden“ bleibt, bei Verbindungsfehlern nur der Grund statt „<urlopen error …>“
        return str(e.reason if isinstance(e, URLError) and not isinstance(e, HTTPError) else e)


def send(url, token, msg):
    """Im Hintergrund verschicken, damit die Seite nicht auf den ntfy-Server wartet."""
    if url:
        threading.Thread(target=send_now, args=(url, token, msg), daemon=True).start()
