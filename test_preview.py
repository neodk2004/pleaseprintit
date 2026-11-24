"""Selbsttest für preview.py: python test_preview.py (kein Netz nötig)."""
from preview import Blocked, fetch, image_ext, parse, public_ip

for bad in ["http://127.0.0.1/", "http://localhost/", "http://192.168.1.222:3666/", "http://10.0.0.1/",
            "http://169.254.169.254/latest/meta-data/", "http://[::1]/", "http://[::ffff:192.168.1.1]/",
            "http://0x7f000001/", "http://100.64.0.1/", "file:///etc/passwd", "ftp://example.com/"]:
    try:
        fetch(bad, 100)
    except Blocked:
        continue
    raise AssertionError(f"nicht blockiert: {bad}")

assert public_ip("8.8.8.8") == "8.8.8.8"

m = parse('<html><head><title> Fallback </title><meta property="og:title" content="Benchy &amp; Co">'
          '<meta property="og:image" content="/img/a.png"><meta property="og:site_name" content="Printables">',
          "https://www.printables.com/model/1")
assert m == {"title": "Benchy & Co", "site": "Printables", "image_url": "https://www.printables.com/img/a.png"}, m
assert parse("<title>Nur Titel</title>", "https://x.de/")["title"] == "Nur Titel"

assert image_ext(b"\x89PNG\r\n\x1a\n...") == "png"
assert image_ext(b"\xff\xd8\xff\xe0") == "jpg"
assert image_ext(b"RIFF\0\0\0\0WEBPVP8") == "webp"
assert image_ext(b"<svg onload=alert(1)>") is None
# Printables über GraphQL (Netz wird ersetzt): Modell-ID aus der URL, Titel und Bild-Adresse aus der Antwort
import preview as P
calls = []
def fake(url, limit, body=None):
    calls.append((url, body))
    return url, "application/json", b'{"data":{"print":{"name":"3DBenchy","images":[{"filePath":"media/prints/3161/a.jpg"}]}}}'
real, P.fetch = P.fetch, fake
r = P.printables("https://www.printables.com/de/model/3161-3d-benchy")
assert r == {"title": "3DBenchy", "site": "Printables", "image_url": "https://media.printables.com/media/prints/3161/a.jpg"}, r
assert calls[0][0] == P.PRINTABLES_API and 'print(id: \\"3161\\")' in calls[0][1]
assert P.printables("https://makerworld.com/en/models/1") is None
P.fetch = real
# Verkleinern: großes PNG → WebP mit höchstens 800 px; kaputte Daten → None (Original bleibt)
import io
from PIL import Image
from preview import shrink
buf = io.BytesIO(); Image.new("RGB", (2000, 1000), "red").save(buf, "PNG")
small, ext = shrink(buf.getvalue())
assert ext == "webp" and image_ext(small) == "webp" and Image.open(io.BytesIO(small)).size == (800, 400)
assert len(small) < len(buf.getvalue())
assert shrink(b"\x89PNG\r\n\x1a\n" + b"\0" * 20) is None
print("OK")
