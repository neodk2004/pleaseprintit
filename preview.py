"""Sicherer Abruf von Link-Vorschauen (Titel, Seitenname, Bild aus Open-Graph-Daten).

Schutz vor SSRF: Jede Adresse (auch nach Weiterleitungen) wird aufgelöst und nur
abgerufen, wenn ALLE ihre IPs öffentlich sind. Verbunden wird dann genau mit der
geprüften IP, damit ein zweiter DNS-Abruf nicht auf ein internes Gerät umlenken kann.
"""
import base64
import codecs
import http.client
import io
import ipaddress
import json
import re
import socket
import ssl
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from PIL import Image

Image.MAX_IMAGE_PIXELS = 50_000_000   # Schutz vor Dekompressionsbomben (Pillow bricht darüber ab)

TIMEOUT = 5            # Sekunden pro Verbindungsschritt
DEADLINE = 10          # Sekunden gesamt pro Abruf
MAX_REDIRECTS = 5
MAX_HTML = 2_000_000   # Bytes; der <head> steht vorne, Rest wird abgeschnitten
MAX_IMAGE = 5_000_000  # Bytes; größere Uploads werden abgelehnt
MAX_FETCHED = 15_000_000  # Bytes; Vorschaubilder von Seiten (Printables liefert Originale um 5 MB)
UA = "PleasePrintit-LinkPreview/1.0 (private Druckwunsch-Verwaltung; ruft nur Titel und Vorschaubild eines eingereichten Links ab)"


class Blocked(Exception):
    pass


def public_ip(host):
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError):
        raise Blocked(f"unbekannter Host {host}")
    ips = []
    for *_, sockaddr in infos:
        ip = ipaddress.ip_address(sockaddr[0].split("%")[0])
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global or ip.is_multicast:
            raise Blocked(f"interne Adresse {ip}")
        ips.append(str(ip))
    return ips[0]


class _HTTP(http.client.HTTPConnection):
    def __init__(self, host, port, ip):
        super().__init__(host, port, timeout=TIMEOUT)
        self.ip = ip

    def connect(self):
        self.sock = socket.create_connection((self.ip, self.port), TIMEOUT)


class _HTTPS(http.client.HTTPSConnection):
    def __init__(self, host, port, ip):
        super().__init__(host, port, timeout=TIMEOUT, context=ssl.create_default_context())
        self.ip = ip

    def connect(self):
        sock = socket.create_connection((self.ip, self.port), TIMEOUT)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def fetch(url, limit, body=None, extra=None):
    """Gibt (finale_url, content_type, bytes) zurück; liest höchstens limit+1 Bytes.
    Mit body (JSON-Text) wird gepostet; sonst GET. extra: zusätzliche Header, nur für den ersten Host
    (nach einer Weiterleitung auf einen anderen Host wird z. B. ein Token nicht mitgeschickt)."""
    first_host = urlsplit(url).hostname
    deadline = time.monotonic() + DEADLINE
    for _ in range(MAX_REDIRECTS + 1):
        u = urlsplit(url)
        if u.scheme not in ("http", "https") or not u.hostname:
            raise Blocked("nur http/https erlaubt")
        port = u.port or (443 if u.scheme == "https" else 80)
        conn = (_HTTPS if u.scheme == "https" else _HTTP)(u.hostname, port, public_ip(u.hostname))
        try:
            headers = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "de,en;q=0.8"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            if extra and u.hostname == first_host:
                headers.update(extra)
            conn.request("POST" if body is not None else "GET", (u.path or "/") + (f"?{u.query}" if u.query else ""),
                         body=body.encode() if body is not None else None, headers=headers)
            r = conn.getresponse()
            if r.status in (301, 302, 303, 307, 308) and r.getheader("Location"):
                url = urljoin(url, r.getheader("Location"))
                continue
            if r.status != 200:
                raise Blocked(f"HTTP {r.status}")
            data = b""
            while len(data) <= limit:
                if time.monotonic() > deadline:
                    raise Blocked("Zeitlimit überschritten")
                chunk = r.read(65536)
                if not chunk:
                    break
                data += chunk
            return url, r.getheader("Content-Type", ""), data
        finally:
            conn.close()
    raise Blocked("zu viele Weiterleitungen")


class _Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.title, self._in_title = {}, "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            if key and a.get("content") and key not in self.meta:
                self.meta[key] = a["content"]
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def parse(html, base):
    p = _Meta()
    p.feed(html)
    m = p.meta
    img = m.get("og:image") or m.get("og:image:url") or m.get("twitter:image")
    return {
        "title": (m.get("og:title") or m.get("twitter:title") or p.title).strip()[:200] or None,
        "site": (m.get("og:site_name") or "").strip()[:100] or None,
        "image_url": urljoin(base, img.strip()) if img else None,
    }


def image_ext(data):
    """Erkennt Bildtyp an den ersten Bytes. SVG absichtlich nicht (kann Skripte enthalten)."""
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    for magic, ext in ((b"\xff\xd8\xff", "jpg"), (b"\x89PNG\r\n\x1a\n", "png"), (b"GIF8", "gif")):
        if data.startswith(magic):
            return ext
    return None


def shrink(data, size=800):
    """Bild auf höchstens size Pixel Kantenlänge verkleinern und als WebP speichern.
    → (bytes, "webp") oder None, wenn das Bild nicht lesbar ist (Aufrufer behält dann das Original).
    Bei GIF zählt nur das erste Bild."""
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.thumbnail((size, size))
            out = io.BytesIO()
            im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB").save(out, "WEBP", quality=80)
            return out.getvalue(), "webp"
    except (OSError, ValueError, Image.DecompressionBombError):
        return None


def _charset(ctype):
    for part in ctype.split(";")[1:]:
        k, _, v = part.strip().partition("=")
        if k.lower() == "charset":
            try:
                return codecs.lookup(v.strip('"')).name
            except LookupError:
                pass
    return "utf-8"


ERRORS = (Blocked, OSError, ValueError, http.client.HTTPException)

PRINTABLES_URL = re.compile(r"^https?://(?:www\.)?printables\.com/(?:[a-z]{2}/)?model/(\d+)", re.I)
PRINTABLES_API = "https://api.printables.com/graphql/"
PRINTABLES_MEDIA = "https://media.printables.com/"


def printables(url):
    """Titel und Bild über die GraphQL-Schnittstelle von Printables (die Webseite selbst sperrt Skripte).
    → Meta-Dict wie parse(), oder None, wenn die URL kein Printables-Modell ist.
    # ponytail: inoffizielle Schnittstelle; ändert Printables sie, greift der normale Abruf bzw. das eigene Bild."""
    m = PRINTABLES_URL.match(url)
    if not m:
        return None
    query = '{ print(id: "%s") { name images { filePath } } }' % m.group(1)
    _, _, data = fetch(PRINTABLES_API, 200_000, json.dumps({"query": query}))
    p = (json.loads(data).get("data") or {}).get("print") or {}
    path = (p.get("images") or [{}])[0].get("filePath")
    return {"title": (p.get("name") or "").strip()[:200] or None, "site": "Printables",
            "image_url": urljoin(PRINTABLES_MEDIA, path) if path else None}


THINGIVERSE_URL = re.compile(r"^https?://(?:www\.)?thingiverse\.com/thing:(\d+)", re.I)


def thingiverse(url, creds):
    """Titel und Bild über die offizielle Thingiverse-API. Nur aktiv, wenn creds["THINGIVERSE_TOKEN"] gesetzt ist
    (die Webseite sperrt Skripte). → Meta-Dict wie parse(), oder None."""
    m, token = THINGIVERSE_URL.match(url), creds.get("THINGIVERSE_TOKEN")
    if not m or not token:
        return None
    _, _, data = fetch(f"https://api.thingiverse.com/things/{m.group(1)}", 500_000,
                       extra={"Authorization": f"Bearer {token}"})
    t = json.loads(data)
    image = t.get("thumbnail") or (t.get("default_image") or {}).get("url")
    return {"title": (t.get("name") or "").strip()[:200] or None, "site": "Thingiverse",
            "image_url": image if isinstance(image, str) and image.startswith("https://") else None}


CULTS_URL = re.compile(r"^https?://(?:www\.)?cults3d\.com/(?:[a-z]{2}(?:-[a-z]{2})?/)?3d-model/[^/?#]+/([\w-]+)", re.I)


def cults3d(url, creds):
    """Titel und Bild über die offizielle Cults3D-GraphQL-API (HTTP Basic mit Nickname und API-Key).
    Nur aktiv, wenn creds CULTS3D_USER und CULTS3D_KEY enthält. → Meta-Dict wie parse(), oder None."""
    m, user, key = CULTS_URL.match(url), creds.get("CULTS3D_USER"), creds.get("CULTS3D_KEY")
    if not (m and user and key):
        return None
    auth = base64.b64encode(f"{user}:{key}".encode()).decode()
    body = json.dumps({"query": "query($s: String!) { creation(slug: $s) { name(locale: EN) illustrationImageUrl } }",
                       "variables": {"s": m.group(1)}})
    _, _, data = fetch("https://cults3d.com/graphql", 200_000, body, {"Authorization": f"Basic {auth}"})
    c = (json.loads(data).get("data") or {}).get("creation") or {}
    image = c.get("illustrationImageUrl")
    return {"title": (c.get("name") or "").strip()[:200] or None, "site": "Cults3D",
            "image_url": image if isinstance(image, str) and image.startswith("https://") else None}


def preview(url, creds=None):
    """Liefert {"title", "site", "image": (bytes, ext) | None}. Wirft nie; Fehler stehen in "error".
    creds: Zugangsdaten für Thingiverse und Cults3D (optional, sonst bleibt es beim Abruf der Webseite)."""
    creds = creds or {}
    out = {"title": None, "site": None, "image": None, "error": None}
    try:
        meta = None
        try:
            meta = printables(url) or thingiverse(url, creds) or cults3d(url, creds)
        except ERRORS as e:
            out["error"] = f"Schnittstelle: {e}"
        if not meta or not meta["title"]:
            final, ctype, data = fetch(url, MAX_HTML)
            if "html" not in ctype.lower():
                out["error"] = f"keine HTML-Seite ({ctype})"
                return out
            meta = parse(data[:MAX_HTML].decode(_charset(ctype), "replace"), final)
            out["error"] = None
    except ERRORS as e:
        out["error"] = str(e)
        return out
    out["title"], out["site"] = meta["title"], meta["site"]
    if meta["image_url"]:
        try:
            _, _, img = fetch(meta["image_url"], MAX_FETCHED)
            ext = image_ext(img)
            if ext and len(img) <= MAX_FETCHED:
                out["image"] = (img, ext)
            else:
                out["error"] = "Bild zu groß oder unbekanntes Format"
        except ERRORS as e:
            out["error"] = f"Bild: {e}"
    return out
