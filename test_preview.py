"""Selbsttest für preview.py: python test_preview.py (kein Netz nötig)."""
from preview import Blocked, fetch, image_ext, parse, public_ip

for bad in ["http://127.0.0.1/", "http://localhost/", "http://192.168.0.10:3666/", "http://10.0.0.1/",
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
print("OK")
