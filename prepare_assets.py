"""Prepare OPRELL assets: transparent logo + local interior photography."""
import os
import urllib.request
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

# ---------------------------------------------------------------- logo
src = Image.open(os.path.join(ROOT, "images.jpg")).convert("RGB")
src = src.resize((src.width * 3, src.height * 3), Image.LANCZOS)  # upscale for smooth edges
px = src.load()
w, h = src.size
out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
op = out.load()
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        # distance from white
        m = min(r, g, b)
        if m > 235:
            a = 0
        elif m > 200:
            a = int((235 - m) / 35 * 255)
        else:
            a = 255
        op[x, y] = (r, g, b, a)
# trim transparent border
bbox = out.getbbox()
out = out.crop(bbox)
out.save(os.path.join(ASSETS, "logo.png"))
print("logo.png", out.size)

# also save the yellow mark only (left portion) for reuse as a motif
mark = out.crop((0, 0, int(out.width * 0.24), out.height)).crop(
    out.crop((0, 0, int(out.width * 0.24), out.height)).getbbox())
mark.save(os.path.join(ASSETS, "mark.png"))
print("mark.png", mark.size)

# sample the yellow
for y in range(0, mark.height, 4):
    for x in range(0, mark.width, 4):
        r, g, b, a = mark.load()[x, y]
        if a > 200 and r > 180 and g > 140 and b < 90:
            print("yellow sample #%02x%02x%02x" % (r, g, b))
            raise SystemExit if False else None
# (loop continues; collect instead)
samples = []
mk = mark.load()
for y in range(0, mark.height, 3):
    for x in range(0, mark.width, 3):
        r, g, b, a = mk[x, y]
        if a > 200 and r > 180 and g > 140 and b < 100:
            samples.append((r, g, b))
if samples:
    ar = sum(s[0] for s in samples) // len(samples)
    ag = sum(s[1] for s in samples) // len(samples)
    ab = sum(s[2] for s in samples) // len(samples)
    print("avg yellow #%02x%02x%02x" % (ar, ag, ab))
