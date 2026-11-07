import base64
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from collections import Counter
from datetime import date, datetime
from urllib.parse import urlparse

from flask import Flask, abort, g, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

import i18n
import mail
from models import MAX_MODEL, embedded_thumbnail, fits, model_kind, volume_cm3
from preview import MAX_IMAGE, image_ext, preview

app = Flask(__name__)
# Hinter dem Nginx Proxy Manager: echte Besucher-IP und https aus den Weiterleitungs-Headern übernehmen
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.secret_key = os.environ["SECRET_KEY"]
PUBLIC_URL = os.environ.get("PUBLIC_URL", "").rstrip("/")   # z. B. https://druck.example.de
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  SESSION_COOKIE_SECURE=PUBLIC_URL.startswith("https://"),
                  PERMANENT_SESSION_LIFETIME=30 * 24 * 3600,
                  MAX_CONTENT_LENGTH=MAX_MODEL + 1_000_000)
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
DB = os.environ.get("DB_PATH", "/data/app.db")
IMAGES = os.path.join(os.path.dirname(DB), "images")
MODELS = os.path.join(os.path.dirname(DB), "models")
os.makedirs(IMAGES, exist_ok=True)
os.makedirs(MODELS, exist_ok=True)

STATUSES = ("neu", "geplant", "gedruckt", "abgelehnt")
MAX_OPEN = 10                      # offene Aufträge (neu/geplant) pro Freund
MAX_STORAGE = 500 * 1024 * 1024    # Speicher für 3D-Dateien pro Freund
INVITE_DAYS = 7
INVITE_LEN = 5
INVITE_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"   # ohne Verwechsler 0/o, 1/l/i
NAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            pw TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, created TEXT);
        CREATE TABLE IF NOT EXISTS invites (token TEXT PRIMARY KEY, created TEXT DEFAULT CURRENT_TIMESTAMP,
            used_by INTEGER);
        CREATE TABLE IF NOT EXISTS resets (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL,
            created TEXT DEFAULT CURRENT_TIMESTAMP, used INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS status_log (link_id INTEGER NOT NULL, status TEXT NOT NULL, at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS filaments (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE);
        CREATE TABLE IF NOT EXISTS colors (id INTEGER PRIMARY KEY, name TEXT NOT NULL, hex TEXT NOT NULL,
            filament_id INTEGER NOT NULL REFERENCES filaments(id) ON DELETE CASCADE);
    """)
    con.execute("PRAGMA foreign_keys = ON")
    if "email" not in {r["name"] for r in con.execute("PRAGMA table_info(users)")}:
        con.execute("ALTER TABLE users ADD COLUMN email TEXT")   # freiwillig, für Status-Mails
    if "lang" not in {r["name"] for r in con.execute("PRAGMA table_info(users)")}:
        con.execute("ALTER TABLE users ADD COLUMN lang TEXT")    # de/en/fr: Oberfläche und Status-Mails
    fcols = {r["name"] for r in con.execute("PRAGMA table_info(filaments)")}
    for col in ("density", "price_kg"):   # g/cm³ und €/kg für die Kostenschätzung
        if col not in fcols:
            con.execute(f"ALTER TABLE filaments ADD COLUMN {col} REAL")
    cols = {r["name"] for r in con.execute("PRAGMA table_info(links)")}
    # Jede Zeile in links ist ein Auftrag; id = Auftragsnummer. url = '' bei Dateien.
    # user_id NULL = vom Administrator selbst angelegt.
    # filament/color/color_hex: Auswahl als Text mitgespeichert, damit sie nach Löschen der Farbe erhalten bleibt.
    # archived: Zeitpunkt der Archivierung; NULL = in der Warteschlange; '' = von Hand zurückgeholt (bleibt draußen).
    for col, typ in (("site", "TEXT"), ("image", "TEXT"), ("file", "TEXT"), ("file_name", "TEXT"),
                     ("created", "TEXT"), ("user_id", "INTEGER"), ("status", "TEXT NOT NULL DEFAULT 'neu'"),
                     ("size", "INTEGER NOT NULL DEFAULT 0"), ("filament", "TEXT"), ("color", "TEXT"),
                     ("color_hex", "TEXT"), ("dims", "TEXT"), ("reason", "TEXT"), ("volume", "REAL"),
                     ("qty", "INTEGER NOT NULL DEFAULT 1"), ("successor", "INTEGER"), ("archived", "TEXT")):
        if col not in cols:
            con.execute(f"ALTER TABLE links ADD COLUMN {col} {typ}")
    return con


def now(con):
    return con.execute("SELECT strftime('%d.%m.%Y %H:%M', 'now', 'localtime')").fetchone()[0]


ARCHIVE_DAYS = 14   # Standard: gedruckte und abgelehnte Aufträge nach 14 Tagen ins Archiv


def iso(col):
    """SQL: 'TT.MM.JJJJ HH:MM' (so speichert now() Zeitpunkte) → 'JJJJ-MM-TT', damit SQLite Daten vergleichen kann."""
    return f"substr({col}, 7, 4) || '-' || substr({col}, 4, 2) || '-' || substr({col}, 1, 2)"


def auto_archive(con):
    """Erledigte Aufträge (gedruckt/abgelehnt) wandern nach der Frist ins Archiv; 0 Tage = nur per Knopf.
    ponytail: läuft beim Aufruf der Warteschlange statt per Zeitplan, für einen Freundeskreis schnell genug."""
    if days := int(setting(con, "archive_days", ARCHIVE_DAYS)):
        con.execute(f"UPDATE links SET archived = ? WHERE archived IS NULL AND status IN ('gedruckt', 'abgelehnt') "
                    f"AND (SELECT MAX({iso('at')}) FROM status_log WHERE link_id = links.id) "
                    "<= date('now', 'localtime', ?)", (now(con), f"-{days} days"))


def insert(con, **fields):
    fields["created"] = now(con)
    fields["user_id"] = None if g.admin else g.user["id"]
    cur = con.execute(f"INSERT INTO links ({', '.join(fields)}) VALUES ({', '.join('?' * len(fields))})",
                      tuple(fields.values()))
    log_status(con, cur.lastrowid, "neu")
    return cur.lastrowid


def log_status(con, link_id, status):
    con.execute("INSERT INTO status_log (link_id, status, at) VALUES (?, ?, ?)", (link_id, status, now(con)))


def flow(con, e):
    """Ablauf-Leiste: [(Name, Zeitpunkt, 'done'|'stop'|'off'), …]."""
    at = dict(con.execute("SELECT status, at FROM status_log WHERE link_id = ? ORDER BY rowid", (e["id"],)).fetchall())
    s = e["status"]
    steps = [(_("Eingereicht"), at.get("neu") or e["created"], "done")]
    if s == "abgelehnt":
        if "geplant" in at:
            steps.append((_("Geplant"), at["geplant"], "done"))
        return steps + [(_("Abgelehnt"), at.get("abgelehnt"), "stop")]
    steps.append((_("Geplant"), at.get("geplant"), "done" if s in ("geplant", "gedruckt") else "off"))
    return steps + [(_("Gedruckt"), at.get("gedruckt"), "done" if s == "gedruckt" else "off")]


def get_entry(con, link_id):
    """Auftrag laden; Freunde bekommen nur ihre eigenen (fremde sehen aus wie nicht vorhanden)."""
    row = con.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
    if not row or (not g.admin and row["user_id"] != g.user["id"]):
        abort(404)
    return row


def save_image(con, link_id, data, ext):
    old = get_entry(con, link_id)["image"]
    name = f"{link_id}.{ext}"
    with open(os.path.join(IMAGES, name), "wb") as f:
        f.write(data)
    if old and old != name:
        os.remove(os.path.join(IMAGES, old))
    con.execute("UPDATE links SET image = ? WHERE id = ?", (name, link_id))


RANDOM = "Random"   # pro Filament: Farbe nach Wahl der Werkstatt
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def text_setting(con, key):
    v = con.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return v[0] if v and v[0] else ""


def setting(con, key, default=0.0):
    return float(text_setting(con, key) or default)


def put_setting(con, key, value):
    con.execute("INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))


# Filament-Sorten zur Auswahl (kein Freitext) mit typischer Dichte in g/cm³ als Startwert für die Kostenschätzung
FILAMENT_TYPES = {"PLA": 1.24, "PLA+": 1.24, "PLA Silk": 1.24, "PLA Matt": 1.24, "PLA-CF": 1.29, "PETG": 1.27,
                  "PETG-CF": 1.30, "ABS": 1.04, "ASA": 1.07, "TPU": 1.21, "PA (Nylon)": 1.14, "PC": 1.20,
                  "HIPS": 1.04, "PVA": 1.23}
FILL = 50   # Standard: Druckteil wiegt etwa die Hälfte eines Vollkörpers (Wände + Füllung)


def estimate(con, e):
    """(Gramm, Euro oder None) für alle Stück aus Volumen, Filament-Dichte, Materialanteil und Preis;
    None ohne Volumen. ponytail: grobe Schätzung ohne Slicer; Stützen und Druckzeit fehlen."""
    if not e["volume"]:
        return None
    f = con.execute("SELECT density, price_kg FROM filaments WHERE name = ?", (e["filament"] or "",)).fetchone()
    grams = (e["volume"] * ((f and f["density"]) or 1.24) * setting(con, "fill", FILL) / 100   # 1,24 = PLA
             * (e["qty"] or 1))
    return grams, grams * f["price_kg"] / 1000 if f and f["price_kg"] else None


def printed(con, user_id):
    """(Stück, Gramm, Euro oder None) aller gedruckten Aufträge einer Person – für „Für dich gedruckt“."""
    n, grams, eur = 0, 0.0, None
    for e in con.execute("SELECT * FROM links WHERE user_id = ? AND status = 'gedruckt'", (user_id,)).fetchall():
        n += e["qty"] or 1
        if c := estimate(con, e):
            grams += c[0]
            if c[1] is not None:
                eur = (eur or 0) + c[1]
    return n, grams, eur


def parse_at(s):
    """'TT.MM.JJJJ HH:MM' (so speichert now() Zeitpunkte) → datetime oder None."""
    try:
        return datetime.strptime(s, "%d.%m.%Y %H:%M")
    except (TypeError, ValueError):
        return None


def stats(con, user_id=None, months=12):
    """Zahlen für die Statistik: alle Aufträge (Werkstatt) oder nur die einer Person.
    ponytail: rechnet bei jedem Aufruf alles in Python durch; reicht für ein paar tausend Aufträge."""
    sql, args = ("SELECT * FROM links WHERE user_id = ?", (user_id,)) if user_id else ("SELECT * FROM links", ())
    rows = con.execute(sql, args).fetchall()
    logs = {}
    for lid, s, at in con.execute("SELECT link_id, status, at FROM status_log ORDER BY rowid"):
        logs.setdefault(lid, {})[s] = at   # letzter Eintrag je Status gewinnt
    y, m = date.today().year, date.today().month
    keys = []
    for i in range(months - 1, -1, -1):   # die letzten Monate, ältester zuerst
        k = y * 12 + m - 1 - i
        keys.append((k // 12, k % 12 + 1))
    per = {k: {"in": 0, "out": 0, "g": 0.0, "eur": 0.0} for k in keys}
    total = {"orders": len(rows), "pieces": 0, "g": 0.0, "eur": None, "status": Counter()}
    waits, fil, col, reasons = [], Counter(), Counter(), Counter()
    for e in rows:
        at = logs.get(e["id"], {})
        start = parse_at(at.get("neu") or e["created"])
        total["status"][e["status"]] += 1
        if start and (start.year, start.month) in per:
            per[(start.year, start.month)]["in"] += 1
        if e["filament"]:
            fil[e["filament"]] += 1
            if e["color"] and e["color"] != RANDOM:
                col[(e["filament"], e["color"], e["color_hex"])] += 1
        if e["status"] == "abgelehnt":
            reasons[e["reason"] or ""] += 1
        if e["status"] != "gedruckt":
            continue
        done, c = parse_at(at.get("gedruckt")), estimate(con, e)
        total["pieces"] += e["qty"] or 1
        if c:
            total["g"] += c[0]
            if c[1] is not None:
                total["eur"] = (total["eur"] or 0) + c[1]
        if done and start:
            waits.append((done - start).total_seconds() / 86400)
        if done and (done.year, done.month) in per:
            p = per[(done.year, done.month)]
            p["out"] += 1
            if c:
                p["g"] += c[0]
                p["eur"] += c[1] or 0
    top = max([p["in"] for p in per.values()] + [p["out"] for p in per.values()] + [1])
    return {"total": total, "months": [(f"{mo:02d}/{yr}", per[(yr, mo)]) for yr, mo in keys], "top": top,
            "wait": sum(waits) / len(waits) if waits else None, "filaments": fil.most_common(5),
            "colors": col.most_common(5), "reasons": reasons.most_common()}


def bed(con):
    """Druckbereich (x, y, z) in mm; 0 = keine Grenze."""
    return tuple(setting(con, k) for k in ("bed_x", "bed_y", "bed_z"))


def filament_options(con):
    """[(filament, [(wert, farbname, hex), …]), …] für das Auswahlfeld; Random immer zuerst."""
    out = []
    for f in con.execute("SELECT * FROM filaments ORDER BY name").fetchall():
        colors = con.execute("SELECT * FROM colors WHERE filament_id = ? ORDER BY name", (f["id"],)).fetchall()
        out.append((f, [(f"r:{f['id']}", RANDOM, None)] +
                    [(f"c:{c['id']}", c["name"], c["hex"]) for c in colors]))
    return out


def parse_choice(con, value):
    """Auswahl 'c:<farbe>' oder 'r:<filament>' → (filament, farbe, hex). None, wenn ungültig."""
    kind_, _sep, ident = (value or "").partition(":")
    if not ident.isdigit():
        return None
    if kind_ == "c":
        r = con.execute("SELECT f.name AS f, c.name AS c, c.hex FROM colors c JOIN filaments f ON f.id = c.filament_id "
                        "WHERE c.id = ?", (int(ident),)).fetchone()
        return (r["f"], r["c"], r["hex"]) if r else None
    if kind_ == "r":
        r = con.execute("SELECT name FROM filaments WHERE id = ?", (int(ident),)).fetchone()
        return (r["name"], RANDOM, None) if r else None
    return None


MAX_QTY = 50


def parse_qty(form):
    """Stückzahl 1–MAX_QTY; Unsinn wird zu 1."""
    v = form.get("qty", "1").strip()
    return min(max(int(v), 1), MAX_QTY) if v.isdigit() else 1


def parse_dims(form):
    """Vom Browser gemessene Maße (x, y, z) oder None."""
    try:
        d = tuple(float(form.get(k, "")) for k in ("dims_x", "dims_y", "dims_z"))
    except ValueError:
        return None
    return d if all(0 < v < 100_000 for v in d) else None


def fmt_dims(d):
    return " × ".join(f"{v:.1f}".rstrip("0").rstrip(".").replace(".", ",") for v in d)


def domain(url):
    host = urlparse(url).hostname or ""
    return host.removeprefix("www.")


def kind(row):
    return row["file"].rsplit(".", 1)[1] if row["file"] else None


def limit_error(con, new_bytes=0):
    """Fehlertext, wenn ein Freund sein Kontingent überschreitet, sonst None."""
    if g.admin:
        return None
    uid = g.user["id"]
    open_count, used = con.execute(
        "SELECT SUM(status IN ('neu', 'geplant')), COALESCE(SUM(size), 0) FROM links WHERE user_id = ?",
        (uid,)).fetchone()
    if (open_count or 0) >= MAX_OPEN:
        return _("Du hast schon {n} offene Aufträge. Warte, bis welche gedruckt sind.", n=MAX_OPEN)
    if used + new_bytes > MAX_STORAGE:
        return _("Dein Speicherplatz ({mb} MB) ist voll.", mb=MAX_STORAGE // 1024 // 1024)
    return None


MAX_VOLUME = 1_000_000   # cm³ = 1 m³; mehr kann kein Hobbydrucker


# --- Anmeldung und Rechte -------------------------------------------------

PUBLIC = {"index", "login", "static", "invite", "legal", "robots", "forgot", "reset", "set_lang"}
PAGES = {"entry", "new", "profile", "users", "settings", "stats_page"}   # ohne Anmeldung → Login, danach zurück
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ADMIN_ONLY = {"set_status", "attach_model", "users", "create_invite", "toggle_user", "settings", "save_bed",
              "add_filament", "delete_filament", "add_color", "delete_color", "save_filament_price",
              "save_legal", "create_reset", "archive", "stats_page", "save_tip"}
# Ablehnungsgründe: kurz für die Werkstatt (wird gespeichert) → ausformuliert für den Freund (Seite + Mail)
REASONS = {
    "Zu komplex": "Das Modell ist für meinen Drucker leider zu komplex – zum Beispiel wegen vieler Stützstrukturen "
                  "oder sehr feiner Details.",
    "Druckdauer zu lang": "Der Druck würde sehr lange dauern und den Drucker zu lange blockieren. "
                          "Vielleicht klappt es mit einer kleineren Version?",
    "Zu groß für den Drucker": "Das Modell ist größer als mein Druckbereich. Wenn es sich verkleinern oder in Teile "
                               "zerlegen lässt, versuch es gern noch einmal.",
    "Filament nicht vorrätig": "Das gewünschte Filament habe ich gerade nicht da. Magst du eine andere Farbe oder "
                               "ein anderes Material wählen?",
    "Material zu teuer": "Das Material für diesen Druck wäre leider zu teuer. Lass uns kurz sprechen, ob es eine "
                         "günstigere Lösung gibt.",
    "Modell fehlerhaft": "Die Datei hat Fehler (zum Beispiel Löcher im Modell) und lässt sich so nicht sauber drucken. "
                         "Hast du vielleicht eine andere Version?",
}


def reason_text(reason):
    """Was der Freund liest: Vorlage ausformuliert (übersetzt), Freitext unverändert."""
    return _(REASONS[reason]) if reason in REASONS else reason


def reason_short(reason):
    """Kurzform für die Werkstatt; gespeichert wird immer der deutsche Schlüssel."""
    return _(reason) if reason in REASONS else reason


# --- Sprache: Konto > Cookie > Browser > Deutsch ---------------------------------

def _(text, /, **kw):
    return i18n.t(g.get("lang", i18n.DEFAULT), text, **kw)


def pick_lang():
    if g.user and g.user["lang"] in i18n.LANGS:
        return g.user["lang"]
    if request.cookies.get("lang") in i18n.LANGS:
        return request.cookies["lang"]
    return request.accept_languages.best_match(list(i18n.LANGS)) or i18n.DEFAULT


class in_lang:
    """Kurz in einer anderen Sprache rendern, z. B. eine Mail für den Empfänger."""
    def __init__(self, lang):
        self.lang = lang if lang in i18n.LANGS else i18n.DEFAULT

    def __enter__(self):
        self.old, g.lang = g.get("lang"), self.lang

    def __exit__(self, *exc):
        g.lang = self.old


def status_label(s):
    return _(s.capitalize())


def color_name(name):
    return _("Random") if name == RANDOM else name


def num(v, digits=1):
    """Zahl mit dem Dezimalzeichen der Sprache (Englisch Punkt, sonst Komma)."""
    return dec(f"{v:.{digits}f}".replace(".", ","))


def dec(text):
    return (text or "").replace(",", ".") if g.get("lang") == "en" else text


def money(v):
    return f"€{v:.2f}" if g.get("lang") == "en" else f"{num(v, 2)} €"


@app.post("/lang")
def set_lang():
    lang = request.form.get("lang")
    r = redirect(safe_next())
    if lang in i18n.LANGS:
        r.set_cookie("lang", lang, max_age=365 * 24 * 3600, samesite="Lax", httponly=True,
                     secure=app.config["SESSION_COOKIE_SECURE"])
        if g.user:
            with db() as con:
                con.execute("UPDATE users SET lang = ? WHERE id = ?", (lang, g.user["id"]))
    return r


@app.before_request
def load_user():
    g.nonce = secrets.token_urlsafe(16)
    g.admin = bool(session.get("admin"))
    g.user = None
    if uid := session.get("uid"):
        with db() as con:
            g.user = con.execute("SELECT * FROM users WHERE id = ? AND active = 1", (uid,)).fetchone()
        if not g.user:
            session.clear()
    g.lang = pick_lang()
    if request.endpoint not in PUBLIC and not (g.admin or g.user):
        if request.method == "GET" and request.endpoint in PAGES:   # z. B. Link aus einer Status-Mail
            return redirect(url_for("index", next=request.full_path.rstrip("?")))
        abort(403)
    if request.endpoint in ADMIN_ONLY and not g.admin:
        abort(403)


@app.after_request
def security_headers(r):
    # Nur eigene Skripte (plus das eine Inline-Importmap mit Nonce) – bremst eingeschleusten Code aus
    r.headers["Content-Security-Policy"] = (
        f"default-src 'self'; script-src 'self' 'nonce-{g.get('nonce', '')}'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
    if request.path.startswith("/static/occt/"):
        # STEP-Leser: läuft nur im Web Worker (eigene Regel aus diesem Header, kein Zugriff auf die Seite)
        # und braucht WebAssembly plus eval (embind). Die Seiten selbst bleiben ohne eval.
        r.headers["Content-Security-Policy"] = ("default-src 'self'; script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'; "
                                                "object-src 'none'; base-uri 'none'")
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["Referrer-Policy"] = "same-origin"
    if app.config["SESSION_COOKIE_SECURE"]:
        r.headers["Strict-Transport-Security"] = "max-age=31536000"   # Browser nutzen nur noch HTTPS
    return r


@app.context_processor
def helpers():
    return {"domain": domain, "kind": kind, "statuses": STATUSES, "fmt_dims": fmt_dims, "reasons": REASONS,
            "reason_text": reason_text, "reason_short": reason_short, "_": _, "status_label": status_label,
            "color_name": color_name, "num": num, "dec": dec, "money": money, "languages": i18n.LANGS,
            "js_texts": lambda: i18n.js_texts(g.lang),
            "year": time.localtime().tm_year, "public": public, "max_qty": MAX_QTY}


# ponytail: Fehlversuche im Arbeitsspeicher (ein Prozess); nach Neustart leer. Reicht für einen Freundeskreis.
FAILS = {}
MAX_FAILS, FAIL_WINDOW = 10, 15 * 60


def too_many_fails(ip):
    now = time.monotonic()
    FAILS[ip] = [t for t in FAILS.get(ip, []) if now - t < FAIL_WINDOW]
    return len(FAILS[ip]) >= MAX_FAILS


def fail(ip):
    FAILS.setdefault(ip, []).append(time.monotonic())


def slowed():
    return render_template("login.html", error=_("Zu viele Fehlversuche. Bitte 15 Minuten warten.")), 429


def sign_in(uid):
    session.clear()
    session.permanent = True
    session["uid"] = uid


def safe_next():
    """Nur Pfade auf dieser Seite, damit niemand über den Login auf fremde Seiten weiterleiten kann."""
    nxt = request.form.get("next", "")
    return nxt if nxt.startswith("/") and not nxt.startswith(("//", "/\\")) else url_for("index")


@app.post("/login")
def login():
    ip = request.remote_addr
    if too_many_fails(ip):
        return slowed()
    name = request.form.get("name", "").strip()
    pw = request.form.get("password", "")
    if name.lower() == "admin":
        if hmac.compare_digest(pw, ADMIN_PASSWORD):
            sign_in(None)
            session["admin"] = True
            return redirect(safe_next())
    else:
        with db() as con:
            u = con.execute("SELECT * FROM users WHERE name = ? AND active = 1", (name,)).fetchone()
        if u and check_password_hash(u["pw"], pw):
            sign_in(u["id"])
            return redirect(safe_next())
    fail(ip)
    return render_template("login.html", error=_("Name oder Passwort falsch.")), 401


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/invite/<token>", methods=["GET", "POST"])
def invite(token):
    ip = request.remote_addr
    if too_many_fails(ip):
        return slowed()
    token = token.strip().lower() if len(token) == INVITE_LEN else token   # kurze Codes: Groß/Klein egal
    with db() as con:
        inv = con.execute("SELECT * FROM invites WHERE token = ? AND used_by IS NULL "
                          "AND julianday('now') - julianday(created) < ?", (token, INVITE_DAYS)).fetchone()
        if not inv:
            fail(ip)
            return render_template("login.html", error=_("Diese Einladung ist ungültig oder abgelaufen.")), 404
        if request.method == "GET":
            return render_template("invite.html")
        name = request.form.get("name", "").strip()
        pw = request.form.get("password", "")
        if not NAME_RE.match(name) or name.lower() == "admin":
            return render_template("invite.html", error=_("Name: 3–30 Zeichen, nur Buchstaben, Ziffern, . _ -")), 400
        if len(pw) < 8:
            return render_template("invite.html", error=_("Passwort: mindestens 8 Zeichen.")), 400
        try:
            cur = con.execute("INSERT INTO users (name, pw, created, lang) VALUES (?, ?, ?, ?)",
                              (name, generate_password_hash(pw), now(con), g.lang))
        except sqlite3.IntegrityError:
            return render_template("invite.html", error=_("Dieser Name ist schon vergeben.")), 400
        con.execute("UPDATE invites SET used_by = ? WHERE token = ?", (cur.lastrowid, token))
    sign_in(cur.lastrowid)
    return redirect(url_for("index"))


# --- Aufträge ----------------------------------------------------------------

@app.get("/")
def index():
    if not (g.admin or g.user):
        return render_template("login.html")
    where, args = [], []
    f = request.args
    arch = g.admin and f.get("archiv") == "1"
    if f.get("status") in STATUSES:
        where.append("l.status = ?")
        args.append(f["status"])
    if g.admin:
        if f.get("user", "").isdigit():
            where.append("l.user_id IS ?")
            args.append(int(f["user"]) or None)  # 0 = eigene Aufträge des Administrators
        if f.get("kind") == "link":
            where.append("l.file IS NULL")
        elif f.get("kind") == "file":
            where.append("l.file IS NOT NULL")
        if q := f.get("q", "").strip():
            where.append("(l.title LIKE ? OR l.url LIKE ? OR l.file_name LIKE ? OR u.name LIKE ?)")
            args += [f"%{q}%"] * 4
        for key, op in (("von", ">="), ("bis", "<=")):   # Zeitraum (Eingereicht), aus <input type="date">
            if DATE_RE.match(f.get(key, "")):
                where.append(f"{iso('l.created')} {op} ?")
                args.append(f[key])
        where.append("COALESCE(l.archived, '') != ''" if arch else "COALESCE(l.archived, '') = ''")
    else:
        where.append("l.user_id = ?")
        args.append(g.user["id"])
    sql = ("SELECT l.*, u.name AS user_name FROM links l LEFT JOIN users u ON u.id = l.user_id"
           + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY l.id DESC")
    with db() as con:
        if g.admin:
            auto_archive(con)
        entries = con.execute(sql, args).fetchall()
        people = con.execute("SELECT id, name FROM users ORDER BY name").fetchall() if g.admin else []
        costs = {e["id"]: estimate(con, e) for e in entries}
        scope = (f"COALESCE(archived, '') {'!=' if arch else '='} ''", ()) if g.admin else ("user_id = ?", (g.user["id"],))
        counts = dict(con.execute(f"SELECT status, COUNT(*) FROM links WHERE {scope[0]} GROUP BY status",
                                  scope[1]).fetchall())
    return render_template("list.html", entries=entries, people=people, f=f, costs=costs, counts=counts, arch=arch)


@app.post("/archive")
def archive():
    """Aufträge ins Archiv legen oder zurückholen: einzeln vom Auftrag aus oder mehrere aus der Liste."""
    ids = [int(i) for i in request.form.getlist("id") if i.isdigit()]
    with db() as con:
        stamp = "" if request.form.get("action") == "restore" else now(con)
        con.executemany("UPDATE links SET archived = ? WHERE id = ?", [(stamp, i) for i in ids])
    return redirect(safe_next())


def new_page(error=None, code=200):
    with db() as con:
        return render_template("new.html", error=error, options=filament_options(con), bed=bed(con)), code


@app.get("/new")
def new():
    return new_page()


@app.post("/orders")
def create_order():
    """Ein Auftrag mit entweder Link oder 3D-Datei, dazu Filament/Farbe."""
    f = request.files.get("model")
    has_file = bool(f and f.filename)
    url = request.form.get("url", "").strip()[:2000]
    title = request.form.get("title", "").strip()[:200]
    if has_file == bool(url):
        return new_page(_("Bitte entweder einen Link oder eine 3D-Datei angeben."), 400)
    # nur http/https, damit kein "javascript:"-Link gespeichert werden kann
    if url and (urlparse(url).scheme not in ("http", "https") or not urlparse(url).hostname):
        return new_page(_("Bitte einen Link mit http:// oder https:// eingeben."), 400)
    with db() as con:
        choice = parse_choice(con, request.form.get("choice"))
        if not choice and con.execute("SELECT 1 FROM filaments").fetchone():
            return new_page(_("Bitte Filament und Farbe auswählen."), 400)
        filament, color, color_hex = choice or (None, None, None)
        # ponytail: Maße misst der Browser des Freundes (umgehbar); Server-Messung für 3MF wäre deutlich aufwendiger
        dims = parse_dims(request.form)
        if dims and not g.admin and not fits(dims, bed(con)):
            return new_page(_("Das Modell ({dims} mm) passt nicht in den Druckbereich ({bed} mm).",
                              dims=dec(fmt_dims(dims)), bed=dec(fmt_dims(bed(con)))), 400)
        if err := limit_error(con):
            return new_page(err, 400)
    extra = {"filament": filament, "color": color, "color_hex": color_hex,
             "dims": fmt_dims(dims) if dims else None, "qty": parse_qty(request.form)}
    return save_file_order(f, title, extra) if has_file else save_link_order(url, title, extra)


def save_link_order(url, title, extra):
    p = preview(url)
    if p["error"]:
        app.logger.warning("Vorschau für %s: %s", url, p["error"])
    with db() as con:
        link_id = insert(con, title=title or p["title"] or domain(url), url=url, site=p["site"], **extra)
        if p["image"]:
            save_image(con, link_id, *p["image"])
    return redirect(url_for("entry", link_id=link_id))


def store_model(f):
    """Upload prüfen und unter Zufallsnamen ablegen (Originalname wird nie als Pfad benutzt).
    → dict mit den Spalten für links, oder None bei ungültiger Datei."""
    tmp = os.path.join(MODELS, secrets.token_hex(16) + ".upload")
    f.save(tmp)
    k = model_kind(tmp)
    if not k:
        os.remove(tmp)
        return None
    name = tmp.removesuffix(".upload") + "." + k
    os.replace(tmp, name)
    return {"file": os.path.basename(name), "file_name": os.path.basename(f.filename.replace("\\", "/"))[:200],
            "size": os.path.getsize(name), "volume": volume_cm3(name, k)}


def add_thumbnail(con, link_id, m):
    if m["file"].endswith(".3mf") and (thumb := embedded_thumbnail(os.path.join(MODELS, m["file"]), MAX_IMAGE)):
        save_image(con, link_id, thumb, "png")


def save_file_order(f, title, extra):
    m = store_model(f)
    with db() as con:
        err = limit_error(con, m["size"]) if m else _("Nur echte STL-, 3MF- oder STEP-Dateien bis 100 MB.")
        if err:
            if m:
                os.remove(os.path.join(MODELS, m["file"]))
            return new_page(err, 400)
        link_id = insert(con, title=title or os.path.splitext(m["file_name"])[0], url="", **m, **extra)
        add_thumbnail(con, link_id, m)
    return redirect(url_for("entry", link_id=link_id))


@app.errorhandler(413)
def too_large(_err):
    return new_page(_("Die Datei ist zu groß (max. 100 MB)."), 413)


@app.get("/entry/<int:link_id>")
def entry(link_id):
    with db() as con:
        e = get_entry(con, link_id)
        if e["file"] and e["volume"] is None:   # ältere Aufträge: Volumen einmalig nachrechnen (0 = nicht lesbar)
            v = volume_cm3(os.path.join(MODELS, e["file"]), kind(e)) or 0
            con.execute("UPDATE links SET volume = ? WHERE id = ?", (v, link_id))
            e = get_entry(con, link_id)
        owner = con.execute("SELECT name FROM users WHERE id = ?", (e["user_id"],)).fetchone()
        return render_template("detail.html", e=e, owner=owner["name"] if owner else _("ich"), bed=bed(con),
                               cost=estimate(con, e), flow=flow(con, e), options=filament_options(con),
                               can_resubmit=can_resubmit(e), tip=text_setting(con, "tip_url"))


NO_FILAMENT = "Filament nicht vorrätig"


def can_resubmit(e):
    """Nur der Besitzer, nur bei 'Filament nicht vorrätig', nur einmal."""
    mine = (e["user_id"] is None) if g.admin else (g.user and e["user_id"] == g.user["id"])
    return bool(mine and e["status"] == "abgelehnt" and e["reason"] == NO_FILAMENT and not e["successor"])


@app.post("/entry/<int:link_id>/resubmit")
def resubmit(link_id):
    """Abgelehnten Auftrag mit anderem Filament als neuen Auftrag übernehmen.
    Datei und Vorschaubild ziehen um (nichts liegt doppelt auf der Platte)."""
    with db() as con:
        old = get_entry(con, link_id)
        if not can_resubmit(old):
            abort(400)
        choice = parse_choice(con, request.form.get("choice"))
        if not choice:
            abort(400, _("Bitte Filament und Farbe auswählen."))
        if err := limit_error(con):
            abort(400, err)
        filament, color, color_hex = choice
        new_id = insert(con, title=old["title"], url=old["url"], site=old["site"], file=old["file"],
                        file_name=old["file_name"], size=old["size"], dims=old["dims"], volume=old["volume"],
                        qty=parse_qty(request.form), filament=filament, color=color, color_hex=color_hex)
        image = None
        if old["image"]:
            image = f"{new_id}.{old['image'].rsplit('.', 1)[1]}"
            os.replace(os.path.join(IMAGES, old["image"]), os.path.join(IMAGES, image))
        con.execute("UPDATE links SET image = ? WHERE id = ?", (image, new_id))
        con.execute("UPDATE links SET file = NULL, size = 0, image = NULL, successor = ? WHERE id = ?",
                    (new_id, link_id))
    return redirect(url_for("entry", link_id=new_id))


@app.post("/entry/<int:link_id>/status")
def set_status(link_id):
    # Status kommt vom Status-Knopf oder (bei den Ablehnungs-Knöpfen) aus der Adresse
    status = request.form.get("status") or request.args.get("status")
    if status not in STATUSES:
        abort(400)
    reason = ""
    if status == "abgelehnt":
        reason = request.form.get("reason", "").strip()
        if reason not in REASONS:   # Freitext
            reason = (request.form.get("free") or reason).strip()[:300]
    with db() as con:
        old = get_entry(con, link_id)
        con.execute("UPDATE links SET status = ?, reason = ? WHERE id = ?", (status, reason or None, link_id))
        if old["status"] != status:
            con.execute("UPDATE links SET archived = NULL WHERE id = ?", (link_id,))   # Frist beginnt neu
            log_status(con, link_id, status)
            notify(con, get_entry(con, link_id))
    return redirect(url_for("entry", link_id=link_id))


def public(endpoint, **kw):
    return (PUBLIC_URL or request.host_url.rstrip("/")) + url_for(endpoint, **kw)


def status_mail(con, e, to, lang):
    title = " ".join(e["title"].split())   # keine Zeilenumbrüche im Betreff
    with in_lang(lang):
        ctx = {"e": e, "flow": flow(con, e), "cost": estimate(con, e), "url": public("entry", link_id=e["id"]),
               "profile_url": public("profile")}
        return mail.build(to, f"#{e['id']:04d} {title}: {status_label(e['status'])}",
                          render_template("mail_status.txt", **ctx),
                          lambda cid: render_template("mail_status.html", cid=cid, **ctx))


def notify(con, e):
    """Status-Mail an den Freund, falls er eine Adresse hinterlegt hat."""
    if not (mail.configured() and e["user_id"]):
        return
    u = con.execute("SELECT email, lang FROM users WHERE id = ? AND active = 1", (e["user_id"],)).fetchone()
    if u and u["email"]:
        mail.send(status_mail(con, e, u["email"], u["lang"]))


@app.post("/entry/<int:link_id>/model")
def attach_model(link_id):
    """Werkstatt hinterlegt (oder ersetzt) die 3D-Datei zu einem Auftrag, z. B. zu einem Link."""
    f = request.files.get("model")
    with db() as con:
        old = get_entry(con, link_id)
        m = store_model(f) if f and f.filename else None
        if not m:
            abort(400, _("Nur echte STL-, 3MF- oder STEP-Dateien bis 100 MB."))
        con.execute("UPDATE links SET file = ?, file_name = ?, size = ?, volume = ? WHERE id = ?",
                    (m["file"], m["file_name"], m["size"], m["volume"], link_id))
        if old["file"]:
            os.remove(os.path.join(MODELS, old["file"]))
        if not old["image"]:
            add_thumbnail(con, link_id, m)
    return redirect(url_for("entry", link_id=link_id))


@app.post("/entry/<int:link_id>/measure")
def measure(link_id):
    """STEP kann der Server nicht vermessen: Die Auftragsseite schickt Volumen und Maße einmalig nach.
    Nur plausible Werte; sie steuern nur die Kostenschätzung, nicht die Rechte."""
    try:
        v = float(request.form.get("volume", ""))
    except ValueError:
        abort(400)
    with db() as con:
        e = get_entry(con, link_id)
        if kind(e) != "step" or e["volume"]:
            abort(409)   # nur STEP, nur einmal
        b = bed(con)
        top = MAX_VOLUME if g.admin or not all(b) else min(MAX_VOLUME, b[0] * b[1] * b[2] / 1000)
        if not 0 < v <= top:
            abort(400)
        d = parse_dims(request.form)
        con.execute("UPDATE links SET volume = ?, dims = ? WHERE id = ?",
                    (v, e["dims"] or (fmt_dims(d) if d else None), link_id))
    return "", 204


@app.get("/models/<int:link_id>/file")
def model_file(link_id):
    download = bool(request.args.get("download"))
    if download and not g.admin:
        abort(403)
    with db() as con:
        e = get_entry(con, link_id)
    if not e["file"]:
        abort(404)
    return send_from_directory(MODELS, e["file"], mimetype="application/octet-stream",
                               as_attachment=download, download_name=e["file_name"])


@app.post("/links/<int:link_id>/image")
def replace_image(link_id):
    f = request.files.get("image")
    data = f.read(MAX_IMAGE + 1) if f else b""
    ext = image_ext(data)
    if not ext or len(data) > MAX_IMAGE:
        abort(400, _("Nur JPG, PNG, GIF oder WebP bis 5 MB."))
    with db() as con:
        save_image(con, link_id, data, ext)
    return redirect(url_for("entry", link_id=link_id))


@app.get("/img/<name>")
def image(name):
    with db() as con:
        e = con.execute("SELECT id FROM links WHERE image = ?", (name,)).fetchone()
        if not e:
            abort(404)
        get_entry(con, e["id"])  # Rechte prüfen
    return send_from_directory(IMAGES, name)


# --- Eigenes Profil (Freunde) -------------------------------------------------

@app.route("/me", methods=["GET", "POST"])
def profile():
    if not g.user:
        return redirect(url_for("index"))
    msg = err = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()[:200]
        if email and not EMAIL_RE.match(email):
            err = _("Das sieht nicht wie eine E-Mail-Adresse aus.")
        else:
            with db() as con:
                con.execute("UPDATE users SET email = ? WHERE id = ?", (email or None, g.user["id"]))
            msg = _("Gespeichert.") if email else _("E-Mail-Adresse gelöscht – du bekommst keine Mails mehr.")
            g.user = dict(g.user, email=email or None)
    with db() as con:
        ctx = mine(con)
    return render_template("profile.html", msg=msg, error=err, mail_on=mail.configured(), **ctx), 400 if err else 200


def mine(con):
    """Zahlen fürs Profil: „Für dich gedruckt“ und die eigene Statistik."""
    return {"done": printed(con, g.user["id"]), "st": stats(con, g.user["id"], months=6),
            "tip": text_setting(con, "tip_url")}


@app.post("/me/test")
def test_mail():
    if not (g.user and g.user["email"] and mail.configured()):
        abort(400)
    with db() as con:
        e = con.execute("SELECT * FROM links WHERE user_id = ? ORDER BY id DESC", (g.user["id"],)).fetchone()
        if not e:
            return render_template("profile.html", mail_on=True, **mine(con),
                                   error=_("Reich zuerst einen Auftrag ein – die Testmail zeigt deinen neuesten.")), 400
        fail = mail.send_now(status_mail(con, e, g.user["email"], g.lang))
        ctx = mine(con)
    return render_template("profile.html", mail_on=True, **ctx, error=fail and _("Versand fehlgeschlagen. Die Werkstatt schaut nach."),
                           msg=None if fail else _("Testmail an {to} ist raus.", to=g.user["email"])), 502 if fail else 200


# --- Freunde verwalten (nur Administrator) -----------------------------------

@app.get("/stats")
def stats_page():
    with db() as con:
        return render_template("stats.html", st=stats(con))


@app.get("/users")
def users():
    with db() as con:
        people = con.execute("""
            SELECT u.*, COUNT(l.id) AS orders, COALESCE(SUM(l.size), 0) AS used
            FROM users u LEFT JOIN links l ON l.user_id = u.id GROUP BY u.id ORDER BY u.name""").fetchall()
        invites = con.execute("SELECT token, strftime('%d.%m.%Y', created, 'localtime') AS day FROM invites "
                              "WHERE used_by IS NULL AND julianday('now') - julianday(created) < ? "
                              "ORDER BY created DESC", (INVITE_DAYS,)).fetchall()
        resets = con.execute("SELECT r.token, u.name, strftime('%d.%m. %H:%M', r.created, 'localtime') AS at "
                             "FROM resets r JOIN users u ON u.id = r.user_id WHERE r.used = 0 "
                             "AND (julianday('now') - julianday(r.created)) * 24 < ? ORDER BY r.created DESC",
                             (RESET_HOURS,)).fetchall()
        done = {p["id"]: printed(con, p["id"]) for p in people}
    return render_template("users.html", people=people, done=done, invites=invites, days=INVITE_DAYS,
                           mail_on=mail.configured(), resets=resets, reset_hours=RESET_HOURS)


@app.post("/users/invite")
def create_invite():
    with db() as con:
        con.execute("INSERT INTO invites (token) VALUES (?)", (short_token(con, "invites"),))
    return redirect(url_for("users"))


def short_token(con, table):
    """5 Zeichen: kurz zum Abtippen; Schutz gegen Raten über die Bremse (FAILS) beim Einlösen."""
    while True:
        token = "".join(secrets.choice(INVITE_ALPHABET) for _i in range(INVITE_LEN))
        if not con.execute(f"SELECT 1 FROM {table} WHERE token = ?", (token,)).fetchone():
            return token


# --- Passwort vergessen: Link per Mail (wenn hinterlegt) oder von der Werkstatt ---------

RESET_HOURS = 24


def new_reset(con, uid):
    token = short_token(con, "resets")
    con.execute("INSERT INTO resets (token, user_id) VALUES (?, ?)", (token, uid))
    return token


@app.post("/users/<int:uid>/reset")
def create_reset(uid):
    with db() as con:
        if not con.execute("SELECT 1 FROM users WHERE id = ?", (uid,)).fetchone():
            abort(404)
        new_reset(con, uid)
    return redirect(url_for("users"))


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html", mail_on=mail.configured())
    ip = request.remote_addr
    if too_many_fails(ip):
        return render_template("forgot.html", mail_on=mail.configured(),
                               error=_("Zu viele Versuche. Bitte 15 Minuten warten.")), 429
    fail(ip)   # jede Anfrage zählt: bremst Massen-Mails und Ausspähen
    who = request.form.get("who", "").strip()[:200]
    with db() as con:
        u = con.execute("SELECT * FROM users WHERE active = 1 AND email IS NOT NULL AND "
                        "(name = ? COLLATE NOCASE OR email = ? COLLATE NOCASE)", (who, who)).fetchone()
        if u and who and mail.configured():
            url = public("reset", token=new_reset(con, u["id"]))
            ctx = {"name": u["name"], "url": url, "hours": RESET_HOURS}
            with in_lang(u["lang"]):   # Mail in der Sprache des Empfängers
                msg = mail.build(u["email"], "PleasePrintit: " + _("Passwort zurücksetzen"),
                                 render_template("mail_reset.txt", **ctx),
                                 lambda cid: render_template("mail_reset.html", cid=cid, **ctx))
            mail.send(msg)
    # Immer dieselbe Antwort: verrät nicht, ob es Name oder Adresse gibt
    return render_template("forgot.html", mail_on=mail.configured(), sent=True)


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    ip = request.remote_addr
    if too_many_fails(ip):
        return slowed()
    token = token.strip().lower()
    with db() as con:
        r = con.execute("SELECT r.*, u.name FROM resets r JOIN users u ON u.id = r.user_id "
                        "WHERE r.token = ? AND r.used = 0 AND u.active = 1 "
                        "AND (julianday('now') - julianday(r.created)) * 24 < ?", (token, RESET_HOURS)).fetchone()
        if not r:
            fail(ip)
            return render_template("login.html", error=_("Dieser Link ist ungültig oder abgelaufen.")), 404
        if request.method == "GET":
            return render_template("reset.html", name=r["name"])
        pw = request.form.get("password", "")
        if len(pw) < 8:
            return render_template("reset.html", name=r["name"], error=_("Passwort: mindestens 8 Zeichen.")), 400
        con.execute("UPDATE users SET pw = ? WHERE id = ?", (generate_password_hash(pw), r["user_id"]))
        con.execute("UPDATE resets SET used = 1 WHERE user_id = ?", (r["user_id"],))   # alle offenen Links ungültig
    sign_in(r["user_id"])
    return redirect(url_for("index"))


@app.post("/users/<int:uid>/toggle")
def toggle_user(uid):
    with db() as con:
        con.execute("UPDATE users SET active = 1 - active WHERE id = ?", (uid,))
    return redirect(url_for("users"))


# --- Werkstatt-Einstellungen: Druckbereich, Filamente, Farben (nur Administrator) ---

@app.get("/settings")
def settings():
    tab = request.args.get("tab")
    tab = tab if tab in ("drucker", "filamente", "werkstatt", "rechtliches") else "drucker"
    with db() as con:
        options = filament_options(con)
        have = {f["name"].lower() for f, _c in options}
        return render_template("settings.html", tab=tab, bed=bed(con), options=options, random=RANDOM,
                               types=[t for t in FILAMENT_TYPES if t.lower() not in have],
                               fill=setting(con, "fill", FILL), imp=impressum_data(con), imp_fields=IMPRESSUM,
                               archive_days=int(setting(con, "archive_days", ARCHIVE_DAYS)),
                               tip=text_setting(con, "tip_url"),
                               datenschutz=text_setting(con, "datenschutz"),
                               template=i18n.PRIVACY_TEMPLATES.get(g.lang, DATENSCHUTZ_TEMPLATE))


# --- Impressum und Datenschutz (öffentlich; die Werkstatt pflegt beides in den Einstellungen) ---

IMPRESSUM = (("imp_name", "Name", True), ("imp_street", "Straße und Hausnummer", True),
             ("imp_city", "PLZ und Ort", True), ("imp_email", "E-Mail", True), ("imp_phone", "Telefon", False))
DATENSCHUTZ_TEMPLATE = i18n.PRIVACY_TEMPLATES["de"] = """Verantwortlich
Die Person aus dem Impressum.

Was gespeichert wird
– Konto: Name, Passwort (nur als verschlüsselter Hash), optional E-Mail-Adresse, Sprache
– Aufträge: Links, hochgeladene 3D-Dateien, Vorschaubilder, gewähltes Filament
– Ein Anmelde-Cookie (30 Tage) und ein Sprach-Cookie, beide technisch notwendig; keine Tracking- oder Werbe-Cookies
– Der Server protokolliert kurzzeitig IP-Adressen zum Schutz vor Angriffen

Wozu
Nur um Druckwünsche anzunehmen, abzuarbeiten und – falls gewünscht – per E-Mail über den Status zu informieren. Keine Weitergabe an Dritte, keine Analyse-Dienste, keine externen Schriften oder Skripte.

Wo
Auf einem privaten Server in Deutschland. Status-Mails werden über den E-Mail-Anbieter der Werkstatt verschickt.

Deine Rechte
Auskunft, Berichtigung und Löschung deiner Daten: kurze Nachricht an die Werkstatt genügt. Die E-Mail-Adresse kannst du jederzeit selbst im Profil löschen."""


def impressum_data(con):
    return {k: text_setting(con, k) for k, *_rest in IMPRESSUM}


def scramble(data):
    """Impressum-Daten nicht lesbar ins HTML: JSON → Base64 → umgedreht. static/legal.js setzt es im Browser
    zusammen. ponytail: hält Adress-Sammler ohne JavaScript ab, keine echte Verschlüsselung."""
    return base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode()[::-1]


@app.get("/<any(impressum, datenschutz):page>")
def legal(page):
    with db() as con:
        if page == "impressum":
            data = impressum_data(con)
            ctx = {"blob": scramble(data) if data["imp_name"] else ""}
        else:
            ctx = {"text": text_setting(con, "datenschutz")}
    return render_template("legal.html", title=_(page.capitalize()), page=page, **ctx)


@app.get("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.post("/settings/legal")
def save_legal():
    f = request.form
    with db() as con:
        values = {k: f.get(k, "").strip()[:200] for k, *_rest in IMPRESSUM}
        if values["imp_email"] and not EMAIL_RE.match(values["imp_email"]):
            abort(400, _("Die E-Mail-Adresse im Impressum sieht nicht richtig aus."))
        ds = f.get("datenschutz", "").strip()[:10000]
        templates = {t.strip() for t in i18n.PRIVACY_TEMPLATES.values()}
        values["datenschutz"] = "" if ds in templates else ds   # unveränderte Vorlage nicht veröffentlichen
        for k, v in values.items():
            put_setting(con, k, v)
    return redirect(url_for("settings", tab="rechtliches"))


def valid_tip(url):
    """Trinkgeld-Link: nur https mit echtem Rechnernamen, sonst None. Leer = kein Knopf."""
    p = urlparse(url)
    return url if p.scheme == "https" and p.hostname and "." in p.hostname and not p.username else None


@app.post("/settings/tip")
def save_tip():
    """Link für den Trinkgeld-Knopf, z. B. PayPal.me oder Ko-fi. Die App selbst verarbeitet kein Geld."""
    url = request.form.get("tip_url", "").strip()[:300]
    if url and not valid_tip(url):
        abort(400, _("Bitte eine vollständige Adresse mit https:// eintragen, z. B. https://paypal.me/deinname."))
    with db() as con:
        put_setting(con, "tip_url", url)
    return redirect(url_for("settings", tab="werkstatt"))


@app.post("/settings/bed")
def save_bed():
    with db() as con:
        for k in ("bed_x", "bed_y", "bed_z", "fill", "archive_days"):
            if k not in request.form:
                continue
            v = request.form[k].strip().replace(",", ".")
            top = {"fill": 100.0, "archive_days": 3650.0}.get(k, 10_000.0)
            try:
                v = str(max(0.0, min(float(v), top))) if v else ""
            except ValueError:
                abort(400)
            put_setting(con, k, v)
    return redirect(url_for("settings", tab="werkstatt" if "archive_days" in request.form else "drucker"))


@app.post("/settings/filaments")
def add_filament():
    name = request.form.get("name", "")
    if name not in FILAMENT_TYPES:
        abort(400)
    with db() as con:   # schon vorhanden → nichts tun (Name ist UNIQUE)
        con.execute("INSERT OR IGNORE INTO filaments (name, density) VALUES (?, ?)", (name, FILAMENT_TYPES[name]))
    return redirect(url_for("settings", tab="filamente"))


@app.post("/settings/filaments/<int:fid>/delete")
def delete_filament(fid):
    with db() as con:
        con.execute("DELETE FROM filaments WHERE id = ?", (fid,))   # Farben fallen mit weg (CASCADE)
    return redirect(url_for("settings", tab="filamente"))


@app.post("/settings/filaments/<int:fid>/price")
def save_filament_price(fid):
    vals = []
    for k, top in (("density", 10), ("price_kg", 1000)):
        v = request.form.get(k, "").strip().replace(",", ".")
        try:
            vals.append((min(max(float(v), 0), top) or None) if v else None)
        except ValueError:
            abort(400)
    with db() as con:
        con.execute("UPDATE filaments SET density = ?, price_kg = ? WHERE id = ?", (*vals, fid))
    return redirect(url_for("settings", tab="filamente"))


@app.post("/settings/filaments/<int:fid>/colors")
def add_color(fid):
    name = request.form.get("name", "").strip()[:40]
    hex_ = request.form.get("hex", "")
    if not name or not HEX_RE.match(hex_) or name.lower() == RANDOM.lower():
        abort(400)
    with db() as con:
        if not con.execute("SELECT 1 FROM filaments WHERE id = ?", (fid,)).fetchone():
            abort(404)
        con.execute("INSERT INTO colors (filament_id, name, hex) VALUES (?, ?, ?)", (fid, name, hex_.lower()))
    return redirect(url_for("settings", tab="filamente"))


@app.post("/settings/colors/<int:cid>/delete")
def delete_color(cid):
    with db() as con:
        con.execute("DELETE FROM colors WHERE id = ?", (cid,))
    return redirect(url_for("settings", tab="filamente"))
