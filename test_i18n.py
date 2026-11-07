"""Selbsttest für die Sprachen: python test_i18n.py
Prüft, dass jeder Text aus _()/t() übersetzt ist, Platzhalter stimmen und die Sprachwahl überall greift."""
import glob
import os
import re
import sqlite3
import tempfile

tmp = tempfile.mkdtemp()
os.environ.update(SECRET_KEY="test", ADMIN_PASSWORD="adminpw", DB_PATH=os.path.join(tmp, "app.db"))
import app as A  # noqa: E402
import i18n  # noqa: E402

here = os.path.dirname(os.path.abspath(__file__))
CALL = r"""\b{f}\(\s*(['"])((?:(?!\1).)+)\1"""

# 1. Jeder Text im Code steht im Katalog
used = set()
for f in glob.glob(os.path.join(here, "templates", "*")) + [os.path.join(here, "app.py")]:
    used |= {m.group(2) for m in re.finditer(CALL.format(f="_"), open(f, encoding="utf-8").read())}
js = set()
for f in glob.glob(os.path.join(here, "static", "*.js")):
    js |= {m.group(2) for m in re.finditer(CALL.format(f="t"), open(f, encoding="utf-8").read())}
dynamic = {s.capitalize() for s in A.STATUSES} | {"Impressum", "Datenschutz", "Random"} \
    | set(A.REASONS) | set(A.REASONS.values()) | {name for _k, name, _r in A.IMPRESSUM}
missing = sorted((used | js | dynamic) - set(i18n.T))
assert not missing, f"Ohne Übersetzung: {missing}"
assert js <= set(i18n.JS_KEYS), f"In JS_KEYS fehlen: {sorted(js - set(i18n.JS_KEYS))}"

# 2. Platzhalter gleich, keine leeren Übersetzungen
ph = re.compile(r"\{\w+\}")
for de, row in i18n.T.items():
    assert len(row) == len(i18n.LANGS) - 1 and all(row), de
    for tr in row:
        assert sorted(ph.findall(tr)) == sorted(ph.findall(de)), (de, tr)

# 3. Sprachwahl: Browser, Umschalter, Konto, Mail
c = A.app.test_client()
assert "Anmelden" in c.get("/").data.decode()
assert "Sign in" in c.get("/", headers={"Accept-Language": "en-US,en;q=0.9"}).data.decode()
r = c.post("/lang", data={"lang": "fr", "next": "/"})
assert r.status_code == 302 and "lang=fr" in r.headers["Set-Cookie"]
page = c.get("/").data.decode()
assert "Se connecter" in page and '<html lang="fr">' in page
assert c.post("/lang", data={"lang": "xx", "next": "//boese.example"}).headers["Location"] == "/", "fremdes Ziel"

admin = A.app.test_client()
admin.post("/login", data={"name": "admin", "password": "adminpw"})
admin.post("/users/invite")
con = sqlite3.connect(A.DB)
tok = con.execute("SELECT token FROM invites WHERE used_by IS NULL").fetchone()[0]
lea = A.app.test_client()
lea.post("/lang", data={"lang": "en", "next": "/"})
assert lea.post(f"/invite/{tok}", data={"name": "lea", "password": "leapasswort"}).status_code == 302
assert con.execute("SELECT lang FROM users WHERE name = 'lea'").fetchone()[0] == "en", "Sprache bei Anmeldung"
lea.post("/lang", data={"lang": "fr", "next": "/me"})
assert con.execute("SELECT lang FROM users WHERE name = 'lea'").fetchone()[0] == "fr", "Umschalter speichert im Konto"
fresh = A.app.test_client()   # neues Gerät ohne Cookie: Konto gewinnt
fresh.post("/login", data={"name": "lea", "password": "leapasswort"})
assert "Imprimé pour toi" in fresh.get("/me").data.decode()
r = lea.post("/orders", data={"url": "http://127.0.0.1/x"})
page = lea.get(r.headers["Location"]).data.decode()
assert "Demande" in page and "Envoyé" in page

# Mail in der Sprache des Empfängers, auch wenn die Werkstatt Deutsch spricht
with A.app.test_request_context("/"):
    A.g.lang = "de"
    with A.db() as db:
        e = db.execute("SELECT * FROM links ORDER BY id DESC").fetchone()
        msg = A.status_mail(db, e, "lea@example.org", "fr")
    assert "Nouveau" in msg["Subject"] and "Statut: Nouveau" in msg.get_body(("plain",)).get_content()
    assert "Ta demande d’impression est bien arrivée." in msg.get_body(("html",)).get_content()
    assert A.g.lang == "de", "Sprache nach der Mail zurückgesetzt"
    assert A.money(8.4) == "8,40 €"
    A.g.lang = "en"
    assert A.money(8.4) == "€8.40" and A.dec("12,5 × 3") == "12.5 × 3"
print("OK")
