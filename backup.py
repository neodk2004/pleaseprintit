"""Sicherung von Datenbank, Vorschaubildern und 3D-Dateien als .tar.gz.

  python backup.py            täglich sichern (läuft dauerhaft, für den backup-Container)
  python backup.py --once     jetzt einmal sichern
  python backup.py --check X  Sicherung X probeweise auspacken und prüfen (Wiederherstellungstest)
"""
import glob
import os
import sqlite3
import sys
import tarfile
import tempfile
import time
from datetime import datetime

DATA, OUT = "/data", "/backups"   # Volumes aus compose.server.yaml
KEEP = 14                        # so viele Sicherungen bleiben liegen


def backup():
    target = os.path.join(OUT, f"pleaseprintit-{datetime.now():%Y-%m-%d_%H%M}.tar.gz")
    with tempfile.TemporaryDirectory() as tmp:
        snap = os.path.join(tmp, "app.db")
        src = sqlite3.connect(f"file:{DATA}/app.db?mode=ro", uri=True)
        dst = sqlite3.connect(snap)
        src.backup(dst)            # in sich stimmige Kopie, auch während die App schreibt
        dst.close()
        src.close()
        with tarfile.open(target + ".part", "w:gz") as tar:
            tar.add(snap, "app.db")
            for folder in ("images", "models"):
                if os.path.isdir(os.path.join(DATA, folder)):
                    tar.add(os.path.join(DATA, folder), folder)
        os.replace(target + ".part", target)
    for old in sorted(glob.glob(os.path.join(OUT, "pleaseprintit-*.tar.gz")))[:-KEEP]:
        os.remove(old)
    return target


def check(archive):
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(archive) as tar:
            tar.extractall(tmp, filter="data")
        con = sqlite3.connect(os.path.join(tmp, "app.db"))
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "Datenbank beschädigt"
        rows = con.execute("SELECT image, file FROM links").fetchall()
        missing = [n for img, f in rows for n in (f"images/{img}" if img else None, f"models/{f}" if f else None)
                   if n and not os.path.isfile(os.path.join(tmp, n))]
        assert not missing, f"fehlende Dateien: {missing}"
        users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0] if con.execute(
            "SELECT 1 FROM sqlite_master WHERE name = 'users'").fetchone() else 0
        return f"OK: {len(rows)} Aufträge, {users} Freunde, alle Dateien vorhanden"


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        print(check(sys.argv[2]))
    elif sys.argv[1:2] == ["--once"]:
        print(backup())
    else:
        while True:
            try:
                if not os.path.exists(os.path.join(DATA, "app.db")):
                    print("Noch keine Datenbank (frische Installation), nichts zu sichern.", flush=True)
                else:
                    print("Sicherung:", backup(), flush=True)
            except Exception as e:  # nicht abstürzen; morgen erneut versuchen
                print("Sicherung fehlgeschlagen:", e, flush=True)
            time.sleep(24 * 3600)
