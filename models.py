"""Prüft hochgeladene 3D-Dateien anhand ihres Inhalts, nicht anhand der Dateiendung."""
import struct
import xml.etree.ElementTree as ET
import zipfile

MAX_MODEL = 100 * 1024 * 1024           # 100 MB pro Datei
MAX_3MF_UNPACKED = 500 * 1024 * 1024    # 3MF ist ein ZIP: Schutz vor "Zip-Bomben" beim Entpacken im Browser


def model_kind(path):
    """Gibt 'stl', '3mf', 'step' oder None zurück."""
    with open(path, "rb") as f:
        head = f.read(84)
        size = f.seek(0, 2)
        # Binäres STL: 80 Byte Kopf, Anzahl Dreiecke, je Dreieck genau 50 Byte
        if len(head) == 84 and size > 84 and size == 84 + 50 * struct.unpack_from("<I", head, 80)[0]:
            return "stl"
        f.seek(0)
        start = f.read(65536).lower()
    if start.lstrip().startswith(b"solid") and b"facet" in start:
        return "stl"
    if start.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"iso-10303-21;"):   # STEP (ISO 10303-21), Text
        return "step"
    if zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path) as z:
                infos = z.infolist()
        except zipfile.BadZipFile:
            return None
        has_model = any(i.filename.lower().startswith("3d/") and i.filename.lower().endswith(".model") for i in infos)
        if has_model and sum(i.file_size for i in infos) <= MAX_3MF_UNPACKED:
            return "3mf"
    return None


def _signed(a, b, c):
    """Vorzeichenbehaftetes Volumen des Tetraeders (Ursprung, a, b, c) × 6."""
    return (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def volume_cm3(path, kind):
    """Volumen des Modells in cm³ (Einheit mm angenommen) oder None, wenn nicht lesbar.
    Summe über alle Netze; mehrfach platzierte Instanzen in 3MF zählen einmal."""
    if kind == "step":
        return None   # braucht OpenCascade; misst der Browser (static/step.js), siehe app.measure
    total = 0.0
    try:
        if kind == "stl":
            with open(path, "rb") as f:
                data = f.read()
            if len(data) == 84 + 50 * struct.unpack_from("<I", data, 80)[0]:
                for t in struct.iter_unpack("<12fH", memoryview(data)[84:]):
                    total += _signed(t[3:6], t[6:9], t[9:12])
            else:
                pts = [tuple(map(float, line.split()[1:4])) for line in data.decode("ascii", "ignore").splitlines()
                       if line.strip().startswith("vertex")]
                for i in range(0, len(pts) - 2, 3):
                    total += _signed(*pts[i:i + 3])
        else:
            with zipfile.ZipFile(path) as z:
                for n in z.namelist():
                    if not (n.lower().startswith("3d/") and n.lower().endswith(".model")):
                        continue
                    verts, stack = [], []
                    with z.open(n) as f:
                        for ev, el in ET.iterparse(f, ("start", "end")):
                            if ev == "start":
                                stack.append(el)
                                continue
                            stack.pop()
                            tag = el.tag.rsplit("}", 1)[-1]
                            if tag == "vertex":
                                verts.append((float(el.get("x")), float(el.get("y")), float(el.get("z"))))
                            elif tag == "triangle":
                                total += _signed(verts[int(el.get("v1"))], verts[int(el.get("v2"))],
                                                 verts[int(el.get("v3"))])
                            elif tag == "mesh":
                                verts = []
                            if stack:
                                del stack[-1][-1]   # fertiges Element sofort aus dem Baum werfen (Speicher)
    except (ValueError, IndexError, TypeError, struct.error, zipfile.BadZipFile, ET.ParseError):
        return None
    return abs(total) / 6 / 1000


def fits(dims, bed):
    """Passt ein Modell (x, y, z in mm) in den Druckbereich? Drehen ist erlaubt, daher sortiert vergleichen.
    bed mit 0-Werten = keine Grenze in dieser Achse."""
    if not all(bed):
        return all(d <= b for d, b in zip(dims, bed) if b)
    return all(d <= b + 0.01 for d, b in zip(sorted(dims), sorted(bed)))


# Vorschaubilder, die Slicer in ihre 3MF-Projekte legen (PrusaSlicer, Bambu/Orca/Creality)
THUMBNAILS = ("Metadata/thumbnail.png", "Metadata/plate_1.png")


def embedded_thumbnail(path, max_size):
    """PNG-Bytes des eingebetteten Slicer-Vorschaubilds oder None."""
    with zipfile.ZipFile(path) as z:
        names = {i.filename: i for i in z.infolist()}
        for n in THUMBNAILS:
            if n in names and names[n].file_size <= max_size:
                data = z.read(n)
                if data.startswith(b"\x89PNG\r\n\x1a\n"):
                    return data
    return None
