"""E-Mail-Versand über SMTP (nur Standardbibliothek). Zugangsdaten kommen aus der .env:
SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SMTP_SECURITY (starttls | ssl | none).
Ohne SMTP_HOST ist der Versand einfach abgeschaltet."""
import logging
import os
import smtplib
import ssl
import threading
from email.message import EmailMessage
from email.utils import make_msgid

log = logging.getLogger("mail")
LOGO = os.path.join(os.path.dirname(__file__), "static", "icon-192.png")


def configured():
    return bool(os.environ.get("SMTP_HOST"))


def build(to, subject, text, html_with_cid):
    """html_with_cid(cid) → HTML; das Logo hängt als eingebettetes Bild an (Gmail & Co. zeigen kein SVG)."""
    msg = EmailMessage()
    msg["Subject"], msg["To"] = subject, to
    msg["From"] = os.environ.get("SMTP_FROM") or os.environ.get("SMTP_USER", "")
    msg.set_content(text)
    cid = make_msgid("logo")
    msg.add_alternative(html_with_cid(cid[1:-1]), subtype="html")
    with open(LOGO, "rb") as f:
        msg.get_payload()[1].add_related(f.read(), "image", "png", cid=cid)
    return msg


def send_now(msg):
    """Sofort verschicken; gibt None oder die Fehlermeldung zurück."""
    host = os.environ["SMTP_HOST"]
    sec = os.environ.get("SMTP_SECURITY", "starttls").lower()
    port = int(os.environ.get("SMTP_PORT") or (465 if sec == "ssl" else 587))
    ctx = ssl.create_default_context()
    try:
        with (smtplib.SMTP_SSL(host, port, context=ctx, timeout=20) if sec == "ssl"
              else smtplib.SMTP(host, port, timeout=20)) as s:
            if sec == "starttls":
                s.starttls(context=ctx)
            if os.environ.get("SMTP_USER"):
                s.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASSWORD", ""))
            s.send_message(msg)
        log.info("Mail an %s verschickt", msg["To"])
        return None
    except (OSError, smtplib.SMTPException) as e:
        log.warning("Mail an %s fehlgeschlagen: %s", msg["To"], e)
        return str(e)


def send(msg):
    """Im Hintergrund verschicken, damit die Seite nicht auf den Mailserver wartet."""
    if not configured():
        return
    threading.Thread(target=send_now, args=(msg,), daemon=True).start()
