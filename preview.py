"""Sicherer Abruf von Link-Vorschauen (Titel, Seitenname, Bild aus Open-Graph-Daten).

Schutz vor SSRF: Jede Adresse (auch nach Weiterleitungen) wird aufgelöst und nur
abgerufen, wenn ALLE ihre IPs öffentlich sind. Verbunden wird dann genau mit der
geprüften IP, damit ein zweiter DNS-Abruf nicht auf ein internes Gerät umlenken kann.
"""
import codecs
import http.client
import ipaddress
import socket
import ssl
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

TIMEOUT = 5            # Sekunden pro Verbindungsschritt
DEADLINE = 10          # Sekunden gesamt pro Abruf
MAX_REDIRECTS = 5
MAX_HTML = 2_000_000   # Bytes; der <head> steht vorne, Rest wird abgeschnitten
MAX_IMAGE = 5_000_000  # Bytes; größere Bilder werden abgelehnt
UA = "Mozilla/5.0 (compatible; PleasePrintitBot/1.0)"


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


def fetch(url, limit):
    """Gibt (finale_url, content_type, bytes) zurück; liest höchstens limit+1 Bytes."""
    deadline = time.monotonic() + DEADLINE
    for _ in range(MAX_REDIRECTS + 1):
        u = urlsplit(url)
        if u.scheme not in ("http", "https") or not u.hostname:
            raise Blocked("nur http/https erlaubt")
        port = u.port or (443 if u.scheme == "https" else 80)
        conn = (_HTTPS if u.scheme == "https" else _HTTP)(u.hostname, port, public_ip(u.hostname))
        try:
            conn.request("GET", (u.path or "/") + (f"?{u.query}" if u.query else ""),
                         headers={"User-Agent": UA, "Accept": "*/*", "Accept-Language": "de,en;q=0.8"})
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


def preview(url):
    """Liefert {"title", "site", "image": (bytes, ext) | None}. Wirft nie; Fehler stehen in "error"."""
    out = {"title": None, "site": None, "image": None, "error": None}
    try:
        final, ctype, data = fetch(url, MAX_HTML)
        if "html" not in ctype.lower():
            out["error"] = f"keine HTML-Seite ({ctype})"
            return out
        meta = parse(data[:MAX_HTML].decode(_charset(ctype), "replace"), final)
    except ERRORS as e:
        out["error"] = str(e)
        return out
    out["title"], out["site"] = meta["title"], meta["site"]
    if meta["image_url"]:
        try:
            _, _, img = fetch(meta["image_url"], MAX_IMAGE)
            ext = image_ext(img)
            if ext and len(img) <= MAX_IMAGE:
                out["image"] = (img, ext)
            else:
                out["error"] = "Bild zu groß oder unbekanntes Format"
        except ERRORS as e:
            out["error"] = f"Bild: {e}"
    return out
