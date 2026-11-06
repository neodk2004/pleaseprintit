"""Selbsttest für Konten, Rechte, Status und Limits: python test_app.py (im App-Container)."""
import io
import os
import sqlite3
import struct
import tempfile

tmp = tempfile.mkdtemp()
os.environ.update(SECRET_KEY="test", ADMIN_PASSWORD="adminpw", DB_PATH=os.path.join(tmp, "app.db"))
import app as A  # noqa: E402

STL = b"\0" * 80 + struct.pack("<I", 1) + struct.pack("<12fH", *[0.0] * 12, 0)


def client():
    return A.app.test_client()


def login(c, name, pw):
    return c.post("/login", data={"name": name, "password": pw})


def token():
    return sqlite3.connect(A.DB).execute(
        "SELECT token FROM invites WHERE used_by IS NULL ORDER BY rowid DESC").fetchone()[0]


admin = client()
assert login(admin, "admin", "falsch").status_code == 401
assert login(admin, "admin", "adminpw").status_code == 302

# Ohne Konto: nichts erreichbar, Einladung nur mit gültigem Token
anon = client()
for path in ("/img/1.png", "/models/1/file"):
    assert anon.get(path).status_code == 403, path
for path in ("/new", "/entry/1", "/users"):   # Seiten → Login mit Rücksprung
    r = anon.get(path)
    assert r.status_code == 302 and "next=" in r.headers["Location"], path
assert anon.post("/orders").status_code == 403
assert anon.get("/invite/gibtsnicht").status_code == 404

# Zwei Freunde per Einladung
admin.post("/users/invite")
t = token()
anna, ben = client(), client()
assert anna.post(f"/invite/{t}", data={"name": "admin", "password": "12345678"}).status_code == 400
assert anna.post(f"/invite/{t}", data={"name": "anna", "password": "kurz"}).status_code == 400
assert anna.post(f"/invite/{t}", data={"name": "anna", "password": "annapasswort"}).status_code == 302
assert ben.post(f"/invite/{t}", data={"name": "ben", "password": "benpasswort"}).status_code == 404, "Einladung doppelt nutzbar"
admin.post("/users/invite")
assert ben.post(f"/invite/{token()}", data={"name": "ANNA", "password": "benpasswort"}).status_code == 400, "Name doppelt"
assert ben.post(f"/invite/{token()}", data={"name": "ben", "password": "benpasswort"}).status_code == 302

# Passwort gehasht gespeichert
pw = sqlite3.connect(A.DB).execute("SELECT pw FROM users WHERE name = 'anna'").fetchone()[0]
assert "annapasswort" not in pw and pw.startswith("scrypt:")
assert login(client(), "anna", "annapasswort").status_code == 302
# Rücksprung nach dem Login (Link aus der Status-Mail), aber nie auf fremde Seiten
nx = client()
assert nx.post("/login", data={"name": "anna", "password": "annapasswort", "next": "/entry/7"}).headers["Location"].endswith("/entry/7")
for bad in ("//evil.example", "https://evil.example", "/\\evil.example"):
    loc = client().post("/login", data={"name": "anna", "password": "annapasswort", "next": bad}).headers["Location"]
    assert "evil" not in loc, bad
assert 'name="next" value="/entry/7"' in client().get("/?next=/entry/7").data.decode()

# Anna lädt hoch; Ben sieht davon nichts
r = anna.post("/orders", data={"model": (io.BytesIO(STL), "teil.stl")}, content_type="multipart/form-data")
assert r.status_code == 302
anna_id = int(r.headers["Location"].rsplit("/", 1)[1])
anna.post(f"/links/{anna_id}/image", data={"image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\0" * 20), "v.png")},
          content_type="multipart/form-data")
assert anna.get(f"/entry/{anna_id}").status_code == 200
assert anna.get(f"/models/{anna_id}/file").status_code == 200
assert anna.get(f"/img/{anna_id}.png").status_code == 200
for path in (f"/entry/{anna_id}", f"/models/{anna_id}/file", f"/img/{anna_id}.png"):
    assert ben.get(path).status_code == 404, path
assert b"teil" not in ben.get("/").data
assert ben.post(f"/links/{anna_id}/image", data={"image": (io.BytesIO(b"\x89PNG\r\n\x1a\n"), "x.png")},
                content_type="multipart/form-data").status_code == 404

# Nur die Werkstatt: Download, Status, Freunde verwalten
assert anna.get(f"/models/{anna_id}/file?download=1").status_code == 403
assert anna.post(f"/entry/{anna_id}/status", data={"status": "gedruckt"}).status_code == 403
assert anna.get("/users").status_code == 403
assert admin.get(f"/models/{anna_id}/file?download=1").status_code == 200
assert admin.post(f"/entry/{anna_id}/status", data={"status": "kaputt"}).status_code == 400
assert admin.post(f"/entry/{anna_id}/status", data={"status": "geplant"}).status_code == 302
assert b"geplant" in anna.get(f"/entry/{anna_id}").data

# Filter in der Werkstatt
home = admin.get("/?status=geplant&kind=file&q=teil").data.decode()
assert "teil" in home and "anna" in home
assert "teil" not in admin.get("/?status=gedruckt").data.decode()
assert "teil" not in admin.get("/?kind=link").data.decode()

# Limit offener Aufträge
A.MAX_OPEN = 2
assert ben.post("/orders", data={"url": "http://127.0.0.1/a"}).status_code == 302  # Vorschau blockiert, Auftrag ok
assert ben.post("/orders", data={"url": "http://127.0.0.1/b"}).status_code == 302
assert ben.post("/orders", data={"url": "http://127.0.0.1/c"}).status_code == 400
assert admin.post("/orders", data={"url": "http://127.0.0.1/d"}).status_code == 302  # Werkstatt ohne Limit
A.MAX_OPEN = 10

# Speicherlimit
A.MAX_STORAGE = len(STL) + 10
assert anna.post("/orders", data={"model": (io.BytesIO(STL), "zwei.stl")},
                 content_type="multipart/form-data").status_code == 400
assert len(os.listdir(A.MODELS)) == 1, "abgelehnte Datei nicht gelöscht"

# Gesperrter Freund ist sofort draußen
anna_uid = sqlite3.connect(A.DB).execute("SELECT id FROM users WHERE name = 'anna'").fetchone()[0]
admin.post(f"/users/{anna_uid}/toggle")
assert anna.get("/new").status_code == 302   # gesperrt → zurück zum Login
assert login(client(), "anna", "annapasswort").status_code == 401

# Bremse gegen Passwort-Raten (gilt pro IP, auch für das richtige Passwort danach)
A.FAILS.clear()
c = client()
for _ in range(A.MAX_FAILS):
    assert login(c, "admin", "falsch").status_code == 401
assert login(c, "admin", "adminpw").status_code == 429
other = A.app.test_client()
assert other.post("/login", data={"name": "admin", "password": "adminpw"},
                  environ_base={"REMOTE_ADDR": "203.0.113.9"}).status_code == 302, "andere IP gesperrt"
A.FAILS.clear()

# Schutz-Header; Importmap trägt die passende Nonce
r = admin.get(f"/entry/{anna_id}")
csp = r.headers["Content-Security-Policy"]
nonce = csp.split("'nonce-")[1].split("'")[0]
assert f'nonce="{nonce}"' in r.data.decode() and "frame-ancestors 'none'" in csp
assert "Strict-Transport-Security" not in r.headers   # lokal ohne HTTPS kein HSTS
A.app.config["SESSION_COOKIE_SECURE"] = True
assert "max-age" in admin.get("/").headers["Strict-Transport-Security"]
A.app.config["SESSION_COOKIE_SECURE"] = False

# --- Filamente, Farben, Druckbereich --------------------------------------
A.MAX_STORAGE, A.MAX_OPEN = 500 * 1024 * 1024, 100
con = sqlite3.connect(A.DB)
assert ben.get("/settings").status_code == 403
assert ben.post("/settings/filaments", data={"name": "PLA"}).status_code == 403
admin.post("/settings/filaments", data={"name": "PLA"})
admin.post("/settings/filaments", data={"name": "pla"})          # doppelt (Groß/Klein egal) → ignoriert
fid = con.execute("SELECT id FROM filaments WHERE name = 'PLA'").fetchone()[0]
assert con.execute("SELECT COUNT(*) FROM filaments").fetchone()[0] == 1
assert admin.post(f"/settings/filaments/{fid}/colors", data={"name": "Rot", "hex": "red"}).status_code == 400
assert admin.post(f"/settings/filaments/{fid}/colors", data={"name": "Random", "hex": "#000000"}).status_code == 400
assert admin.post(f"/settings/filaments/{fid}/colors", data={"name": "Rot", "hex": "#FF0000"}).status_code == 302
cid = con.execute("SELECT id FROM colors WHERE name = 'Rot'").fetchone()[0]
page = ben.get("/new").data.decode()
assert f'value="r:{fid}"' in page and f'value="c:{cid}"' in page and "Random" in page

# Auswahl ist Pflicht, sobald Filamente existieren
assert ben.post("/orders", data={"url": "http://127.0.0.1/x"}).status_code == 400
assert ben.post("/orders", data={"url": "http://127.0.0.1/x", "choice": "c:999"}).status_code == 400
r = ben.post("/orders", data={"url": "http://127.0.0.1/rot", "choice": f"c:{cid}"})
rot_id = int(r.headers["Location"].rsplit("/", 1)[1])
r = ben.post("/orders", data={"url": "http://127.0.0.1/zufall", "choice": f"r:{fid}"})
zufall_id = int(r.headers["Location"].rsplit("/", 1)[1])
assert con.execute("SELECT filament, color, color_hex FROM links WHERE id = ?", (rot_id,)).fetchone() == ("PLA", "Rot", "#ff0000")
assert con.execute("SELECT color, color_hex FROM links WHERE id = ?", (zufall_id,)).fetchone() == ("Random", None)
# Entweder Link oder Datei
assert ben.post("/orders", data={"choice": f"r:{fid}"}).status_code == 400
assert ben.post("/orders", data={"url": "http://127.0.0.1/y", "choice": f"r:{fid}",
                                 "model": (io.BytesIO(STL), "a.stl")}, content_type="multipart/form-data").status_code == 400

# Farbe löschen: alter Auftrag behält seine Angabe
admin.post(f"/settings/colors/{cid}/delete")
assert b"Rot" in admin.get(f"/entry/{rot_id}").data
admin.post(f"/settings/filaments/{fid}/delete")
assert con.execute("SELECT COUNT(*) FROM colors").fetchone()[0] == 0

# Druckbereich: Freund wird bei zu großen Maßen abgewiesen, Drehen zählt, Werkstatt darf trotzdem
assert ben.post("/settings/bed", data={"bed_x": "256"}).status_code == 403
assert admin.post("/settings/bed", data={"bed_x": "abc"}).status_code == 400
admin.post("/settings/bed", data={"bed_x": "256", "bed_y": "256,5", "bed_z": "200"})
assert A.bed(sqlite3.connect(A.DB)) == (256.0, 256.5, 200.0)
big = {"url": "http://127.0.0.1/big", "dims_x": "100", "dims_y": "50", "dims_z": "250"}  # 250 hoch > 200, liegend ok
assert ben.post("/orders", data=big).status_code == 302, "gedreht passt es"
big.update(dims_x="300", dims_y="300")
assert ben.post("/orders", data=big).status_code == 400
assert admin.post("/orders", data=big).status_code == 302
assert con.execute("SELECT dims FROM links ORDER BY id DESC").fetchone()[0] == "300 × 300 × 250"
# --- Datei nachträglich hinterlegen, Ablehnungsgrund, Kosten ---------------
CUBE = b"\0" * 80 + struct.pack("<I", 12) + b"".join(struct.pack("<12fH", 0, 0, 0, *a, *b, *c, 0) for a, b, c in [
    ((0, 0, 0), (10, 10, 0), (10, 0, 0)), ((0, 0, 0), (0, 10, 0), (10, 10, 0)), ((0, 0, 10), (10, 0, 10), (10, 10, 10)),
    ((0, 0, 10), (10, 10, 10), (0, 10, 10)), ((0, 0, 0), (10, 0, 0), (10, 0, 10)), ((0, 0, 0), (10, 0, 10), (0, 0, 10)),
    ((10, 0, 0), (10, 10, 0), (10, 10, 10)), ((10, 0, 0), (10, 10, 10), (10, 0, 10)),
    ((10, 10, 0), (0, 10, 0), (0, 10, 10)), ((10, 10, 0), (0, 10, 10), (10, 10, 10)),
    ((0, 10, 0), (0, 0, 0), (0, 0, 10)), ((0, 10, 0), (0, 0, 10), (0, 10, 10))])
admin.post("/settings/filaments", data={"name": "PETG"})
pid = con.execute("SELECT id FROM filaments WHERE name = 'PETG'").fetchone()[0]
assert ben.post(f"/settings/filaments/{pid}/price", data={"price_kg": "20"}).status_code == 403
assert admin.post(f"/settings/filaments/{pid}/price", data={"price_kg": "abc"}).status_code == 400
admin.post(f"/settings/filaments/{pid}/price", data={"price_kg": "20", "density": "1,27"})
assert con.execute("SELECT price_kg, density FROM filaments WHERE id = ?", (pid,)).fetchone() == (20, 1.27)
admin.post("/settings/bed", data={"fill": "100"})
assert A.bed(sqlite3.connect(A.DB)) == (256.0, 256.5, 200.0), "Materialanteil löscht Druckbereich"
r = ben.post("/orders", data={"url": "http://127.0.0.1/wuerfel", "choice": f"r:{pid}"})
w_id = int(r.headers["Location"].rsplit("/", 1)[1])
cube = lambda: {"model": (io.BytesIO(CUBE), "wuerfel.stl")}  # noqa: E731
assert ben.post(f"/entry/{w_id}/model", data=cube(), content_type="multipart/form-data").status_code == 403
assert admin.post(f"/entry/{w_id}/model", data={"model": (io.BytesIO(b"kein stl"), "x.stl")},
                  content_type="multipart/form-data").status_code == 400
assert admin.post(f"/entry/{w_id}/model", data=cube(), content_type="multipart/form-data").status_code == 302
page = ben.get(f"/entry/{w_id}").data.decode()
assert "1 g" in page and "0,03 €" in page and "127.0.0.1/wuerfel" in page   # 1 cm³ × 1,27 × 100 % × 20 €/kg
old = con.execute("SELECT file FROM links WHERE id = ?", (w_id,)).fetchone()[0]
admin.post(f"/entry/{w_id}/model", data=cube(), content_type="multipart/form-data")
assert not os.path.exists(os.path.join(A.MODELS, old)), "alte Datei nicht gelöscht"

admin.post(f"/entry/{w_id}/status", data={"status": "abgelehnt", "reason": "Zu komplex"})
page = ben.get(f"/entry/{w_id}").data.decode()
assert A.REASONS["Zu komplex"].split(" – ")[0] in page, "Freund liest den ausformulierten Satz"
# Ein-Klick-Ablehnung: Status aus der Adresse, Vorlage gewinnt vor Freitext
admin.post(f"/entry/{w_id}/status", data={"status": "geplant"})
admin.post(f"/entry/{w_id}/status?status=abgelehnt", data={"reason": "Modell fehlerhaft", "free": "egal"})
assert con.execute("SELECT status, reason FROM links WHERE id = ?", (w_id,)).fetchone() == ("abgelehnt", "Modell fehlerhaft")
admin.post(f"/entry/{w_id}/status?status=abgelehnt", data={"reason": "", "free": "Ruf mich kurz an"})
assert con.execute("SELECT reason FROM links WHERE id = ?", (w_id,)).fetchone()[0] == "Ruf mich kurz an"
assert "Ruf mich kurz an" in ben.get(f"/entry/{w_id}").data.decode(), "Freitext unverändert"
assert ben.post(f"/entry/{w_id}/status?status=abgelehnt", data={"reason": "Zu komplex"}).status_code == 403
admin.post(f"/entry/{w_id}/status", data={"status": "abgelehnt", "reason": "Zu komplex"})
admin.post(f"/entry/{w_id}/status", data={"status": "geplant", "reason": "Zu komplex"})
assert con.execute("SELECT reason FROM links WHERE id = ?", (w_id,)).fetchone()[0] is None
# --- Ablauf, Profil-E-Mail, Status-Mails ------------------------------------
flow = [s for s, in con.execute("SELECT status FROM status_log WHERE link_id = ? ORDER BY rowid", (w_id,))]
assert flow == ["neu", "abgelehnt", "geplant", "abgelehnt", "geplant"], flow
admin.post(f"/entry/{w_id}/status", data={"status": "geplant"})   # unverändert → kein neuer Eintrag
assert con.execute("SELECT COUNT(*) FROM status_log WHERE link_id = ?", (w_id,)).fetchone()[0] == 5
page = ben.get(f"/entry/{w_id}").data.decode()
assert "Eingereicht" in page and "Gedruckt" in page

assert admin.get("/me").status_code == 302, "Werkstatt hat kein Profil"
assert ben.get("/me").status_code == 200
assert ben.post("/me", data={"email": "kein-mail"}).status_code == 400
assert ben.post("/me", data={"email": "ben@example.org"}).status_code == 200
assert con.execute("SELECT email FROM users WHERE name = 'ben'").fetchone()[0] == "ben@example.org"

sent = []
A.mail.send = A.mail.send_now = lambda m: sent.append(m)   # statt Hintergrund-Versand mitschreiben
admin.post(f"/entry/{w_id}/status", data={"status": "gedruckt"})
assert not sent, "ohne SMTP_HOST darf nichts verschickt werden"
os.environ["SMTP_HOST"] = "smtp.example.org"
assert ben.post("/me/test").status_code == 200 and len(sent) == 1
admin.post(f"/entry/{w_id}/status", data={"status": "abgelehnt", "reason": "Zu komplex"})
m = sent[-1]
assert m["To"] == "ben@example.org" and "Abgelehnt" in m["Subject"] and "\n" not in m["Subject"]
html = m.get_body(("html",)).get_content()
friendly = A.REASONS["Zu komplex"].split(" – ")[0]
assert friendly in html and "cid:" in html and "/entry/" in html
assert friendly in m.get_body(("plain",)).get_content()
ben.post("/me", data={"email": ""})
admin.post(f"/entry/{w_id}/status", data={"status": "neu"})
assert len(sent) == 2, "nach Löschen der Adresse keine Mails mehr"
del os.environ["SMTP_HOST"]
# --- Stückzahl und Neu-Einreichen mit anderem Filament ----------------------
admin.post("/settings/bed", data={"bed_x": "", "bed_y": "", "bed_z": ""})
r = ben.post("/orders", data={"model": (io.BytesIO(CUBE), "drei.stl"), "choice": f"r:{pid}", "qty": "3"},
             content_type="multipart/form-data")
q_id = int(r.headers["Location"].rsplit("/", 1)[1])
page = ben.get(f"/entry/{q_id}").data.decode()
assert "3 Stück" in page and "≈ 4 g" in page and "0,08 €" in page, "3 × 1,27 g × 20 €/kg"
for bad, want in (("0", 1), ("999", A.MAX_QTY), ("abc", 1)):
    r = ben.post("/orders", data={"url": "http://127.0.0.1/q", "choice": f"r:{pid}", "qty": bad})
    assert con.execute("SELECT qty FROM links ORDER BY id DESC").fetchone()[0] == want, bad

f_before = set(os.listdir(A.MODELS))
assert ben.post(f"/entry/{q_id}/resubmit", data={"choice": f"r:{pid}"}).status_code == 400, "nur bei Filament-Grund"
admin.post(f"/entry/{q_id}/status?status=abgelehnt", data={"reason": "Filament nicht vorrätig"})
assert "Mit anderem Filament neu einreichen" in ben.get(f"/entry/{q_id}").data.decode()
assert anna.post(f"/entry/{q_id}/resubmit", data={"choice": f"r:{pid}"}).status_code in (403, 404), "fremd"
assert ben.post(f"/entry/{q_id}/resubmit", data={"choice": "c:999"}).status_code == 400
r = ben.post(f"/entry/{q_id}/resubmit", data={"choice": f"r:{pid}", "qty": "2"})
n_id = int(r.headers["Location"].rsplit("/", 1)[1])
old, new = (con.execute("SELECT * FROM links WHERE id = ?", (i,)).fetchone() for i in (q_id, n_id))
assert n_id > q_id and new[0] == n_id
row = lambda i: dict(zip([c[1] for c in con.execute("PRAGMA table_info(links)")], con.execute("SELECT * FROM links WHERE id = ?", (i,)).fetchone()))  # noqa: E731
o, n = row(q_id), row(n_id)
assert o["successor"] == n_id and o["file"] is None and o["size"] == 0
assert n["file"] and n["status"] == "neu" and n["qty"] == 2 and n["user_id"] == o["user_id"] and n["volume"] == o["volume"]
assert set(os.listdir(A.MODELS)) == f_before, "Datei verschoben, nicht kopiert"
assert ben.get(f"/models/{n_id}/file").status_code == 200
assert ben.post(f"/entry/{q_id}/resubmit", data={"choice": f"r:{pid}"}).status_code == 400, "nur einmal"
assert f"#{n_id:04d}" in ben.get(f"/entry/{q_id}").data.decode()
# --- Impressum / Datenschutz: öffentlich lesbar, nur Werkstatt schreibt, Impressum verschleiert ---
import base64, json  # noqa: E401,E402
anon = client()
assert anon.get("/impressum").status_code == 200 and anon.get("/datenschutz").status_code == 200
assert anon.get("/agb").status_code in (403, 404)
assert 'href="/impressum"' in anon.get("/").data.decode(), "Link auf der Anmeldeseite"
assert 'name="robots" content="noindex' in anon.get("/").data.decode()
assert "Disallow: /" in anon.get("/robots.txt").data.decode()
assert ben.post("/settings/legal", data={"imp_name": "x"}).status_code == 403
assert admin.post("/settings/legal", data={"imp_name": "Max Muster", "imp_email": "kaputt"}).status_code == 400
admin.post("/settings/legal", data={"imp_name": "Max Muster", "imp_street": "Musterweg 1", "imp_city": "12345 Musterstadt",
                                    "imp_email": "max@example.de", "imp_phone": "",
                                    "datenschutz": A.DATENSCHUTZ_TEMPLATE})
page = anon.get("/impressum").data.decode()
for secret in ("Max Muster", "Musterweg", "max@example.de", "@example"):
    assert secret not in page, f"{secret} steht lesbar im HTML"
blob = page.split('data-blob="')[1].split('"')[0]
assert json.loads(base64.b64decode(blob[::-1]))["imp_name"] == "Max Muster", "Browser kann es zusammensetzen"
assert A.text_setting(sqlite3.connect(A.DB), "datenschutz") == "", "unveränderte Vorlage wird nicht veröffentlicht"
admin.post("/settings/legal", data={"imp_name": "Max Muster", "datenschutz": "Eigener Text <b>"})
assert "Eigener Text &lt;b&gt;" in anon.get("/datenschutz").data.decode()
assert 'href="/datenschutz"' in admin.get("/new").data.decode(), "Link in der Fußzeile"
# --- Kurze Einladungscodes ----------------------------------------------------
A.FAILS.clear()
admin.post("/users/invite")
t = token()
assert len(t) == 5 and set(t) <= set(A.INVITE_ALPHABET), t
assert client().get(f"/invite/{t.upper()}").status_code == 200, "Groß/Klein egal"
A.FAILS.clear()
guess = client()
for _ in range(A.MAX_FAILS):
    assert guess.get("/invite/zzzzz").status_code == 404
assert guess.get(f"/invite/{t}").status_code == 429, "Raten wird gebremst"
A.FAILS.clear()
# --- Passwort vergessen ------------------------------------------------------
A.FAILS.clear()
assert 'href="/forgot"' in client().get("/").data.decode()
assert client().get("/forgot").status_code == 200
uid = con.execute("SELECT id FROM users WHERE name = 'ben'").fetchone()[0]
con.execute("UPDATE users SET email = 'ben@example.org' WHERE id = ?", (uid,)); con.commit()
os.environ["SMTP_HOST"] = "smtp.example.org"
sent.clear()
same = {client().post("/forgot", data={"who": w}).data.decode().count("ok-msg") for w in ("ben", "niemand", "anna")}
assert same == {1}, "gleiche Antwort, egal ob es das Konto gibt"
assert len(sent) == 1 and sent[0]["To"] == "ben@example.org", "nur Ben (aktiv + Adresse) bekommt Mail"
link = sent[0].get_body(("plain",)).get_content().split("/reset/")[1].split()[0]
assert len(link) == 5
r = client().get(f"/reset/{link}"); assert r.status_code == 200 and "ben" in r.data.decode()
assert client().post(f"/reset/{link}", data={"password": "kurz"}).status_code == 400
fresh = client()
assert fresh.post(f"/reset/{link}", data={"password": "neuespasswort"}).status_code == 302
assert fresh.get("/me").status_code == 200, "danach angemeldet"
assert login(client(), "ben", "neuespasswort").status_code == 302
assert client().get(f"/reset/{link}").status_code == 404, "Link nur einmal"
# Werkstatt erzeugt Link für Freund ohne Mail
A.FAILS.clear()
assert ben.post(f"/users/{uid}/reset").status_code == 403
admin.post(f"/users/{uid}/reset")
assert "/reset/" in admin.get("/users").data.decode()
tok = con.execute("SELECT token FROM resets WHERE used = 0").fetchone()[0]
con.execute("UPDATE resets SET created = datetime('now', '-25 hours') WHERE token = ?", (tok,)); con.commit()
assert client().get(f"/reset/{tok}").status_code == 404, "nach 24 Stunden abgelaufen"
del os.environ["SMTP_HOST"]
A.FAILS.clear()
benpw = "neuespasswort"
print("OK")
