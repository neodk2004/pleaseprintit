"""Selbsttest für models.py: python test_models.py"""
import os
import struct
import tempfile
import zipfile

from models import embedded_thumbnail, fits, model_kind, volume_cm3

assert fits((20, 30, 10), (256, 256, 256))
assert fits((300, 100, 50), (256, 256, 320)), "gedreht passt es"
assert not fits((300, 300, 10), (256, 256, 320))
assert fits((256.0, 256.0, 256.0), (256, 256, 256))
assert fits((999, 10, 10), (0, 0, 0)), "keine Grenze"
assert not fits((10, 10, 300), (0, 0, 250)) and fits((500, 10, 200), (0, 0, 250))

d = tempfile.mkdtemp()


def file(name, data):
    p = os.path.join(d, name)
    with open(p, "wb") as f:
        f.write(data)
    return p


tri = struct.pack("<12fH", *[0.0] * 12, 0)
assert model_kind(file("bin.stl", b"solid tricky header".ljust(80, b"\0") + struct.pack("<I", 2) + tri * 2)) == "stl"
assert model_kind(file("ascii.stl", b"solid cube\n facet normal 0 0 1\n outer loop\n")) == "stl"
assert model_kind(file("kaputt.stl", b"\0" * 80 + struct.pack("<I", 5) + tri)) is None
assert model_kind(file("leer.stl", b"")) is None
assert model_kind(file("bild.stl", b"\x89PNG\r\n\x1a\n" + b"\0" * 200)) is None

p = os.path.join(d, "ok.3mf")
with zipfile.ZipFile(p, "w") as z:
    z.writestr("3D/3dmodel.model", "<model/>")
assert model_kind(p) == "3mf"
assert embedded_thumbnail(p, 1000) is None

png = b"\x89PNG\r\n\x1a\n" + b"\0" * 50
p = os.path.join(d, "slicer.3mf")
with zipfile.ZipFile(p, "w") as z:
    z.writestr("3D/3dmodel.model", "<model/>")
    z.writestr("Metadata/plate_1.png", png)
assert embedded_thumbnail(p, 1000) == png
assert embedded_thumbnail(p, 10) is None, "Größenlimit ignoriert"

p = os.path.join(d, "fremd.3mf")
with zipfile.ZipFile(p, "w") as z:
    z.writestr("word/document.xml", "<doc/>")
assert model_kind(p) is None

p = os.path.join(d, "bombe.3mf")
with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("3D/3dmodel.model", b"\0" * (501 * 1024 * 1024))
assert model_kind(p) is None, "Zip-Bombe nicht erkannt"
# Volumen: Würfel 10 mm = 1 cm³, als binäres STL, ASCII-STL und 3MF
V = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0), (0, 0, 10), (10, 0, 10), (10, 10, 10), (0, 10, 10)]
T = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6),
     (3, 0, 4), (3, 4, 7)]
cube = file("cube.stl", b"\0" * 80 + struct.pack("<I", 12) + b"".join(
    struct.pack("<12fH", 0, 0, 0, *V[a], *V[b], *V[c], 0) for a, b, c in T))
assert abs(volume_cm3(cube, "stl") - 1) < 1e-6
ascii_ = file("cube_a.stl", ("solid c\n" + "".join(
    "facet normal 0 0 0\nouter loop\n" + "".join("vertex %d %d %d\n" % V[i] for i in t) + "endloop\nendfacet\n"
    for t in T) + "endsolid c\n").encode())
assert abs(volume_cm3(ascii_, "stl") - 1) < 1e-6
p = os.path.join(d, "cube.3mf")
with zipfile.ZipFile(p, "w") as z:
    z.writestr("3D/3dmodel.model", '<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
               "<resources><object id='1'><mesh><vertices>" + "".join(f"<vertex x='{x}' y='{y}' z='{z}'/>" for x, y, z in V)
               + "</vertices><triangles>" + "".join(f"<triangle v1='{a}' v2='{b}' v3='{c}'/>" for a, b, c in T)
               + "</triangles></mesh></object></resources></model>")
assert abs(volume_cm3(p, "3mf") - 1) < 1e-6
assert volume_cm3(os.path.join(d, "ok.3mf"), "3mf") == 0
assert volume_cm3(os.path.join(d, "fremd.3mf"), "3mf") == 0
print("OK")
