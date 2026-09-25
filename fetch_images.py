import os, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "assets", "img")
os.makedirs(IMG, exist_ok=True)

U = "https://images.unsplash.com/photo-{}?q=80&w={}&auto=format&fit=crop"

files = {
    # hero — spectacular bright interior
    "hero.jpg":        ("1618221195710-dd6b41faaea6", 2000),
    # featured projects
    "p1.jpg":          ("1600607687939-ce8a6c25118c", 1800),
    "p2.jpg":          ("1600210492486-724fe5c67fb0", 1800),
    "p3.jpg":          ("1615873968403-89e068629265", 1800),
    "p4.jpg":          ("1567016432779-094069958ea5", 1800),
    "p5.jpg":          ("1556912167-f556f1f39fdf",    1800),
    # horizontal gallery — mixed proportions
    "g1.jpg":          ("1615874959474-d609969a20ed", 900),   # portrait
    "g2.jpg":          ("1522708323590-d24dbb6b0267", 1600),  # wide
    "g3.jpg":          ("1586023492125-27b2c045efd7", 900),   # square detail
    "g4.jpg":          ("1598928506311-c55ded91a20c", 800),   # small crop
    "g5.jpg":          ("1600121848594-d8644e57abab", 1900),  # huge
    "g6.jpg":          ("1613545325278-f24b0cae1224", 1000),  # arch detail
    "g7.jpg":          ("1560448204-e02f11c3d0e2",   1200),
    # services hover images
    "s1.jpg":          ("1616486338812-3dadae4b4ace", 1000),
    "s2.jpg":          ("1497366216548-37526070297c", 1000),
    "s3.jpg":          ("1600585152220-90363fe7e115", 1000),
    "s4.jpg":          ("1560185127-6ed189bf02f4",   1000),
    "s5.jpg":          ("1524758631624-e2822e304c36", 1000),
    # statement reveal
    "transform.jpg":   ("1631679706909-1844bbd07221", 1800),
    # before/after
    "ba.jpg":          ("1560185007-cde436f6a4d0",   1600),
    # about collage
    "a1.jpg":          ("1493809842364-78817add7ffb", 1000),
    "a2.jpg":          ("1502672260266-1c1ef2d93688", 900),
    "a3.jpg":          ("1536376072261-38c75010e6c9", 900),
    # process
    "pr1.jpg":         ("1586023492125-27b2c045efd7", 900),
    "pr2.jpg":         ("1600607687644-c7171b42498b", 900),
    "pr3.jpg":         ("1613545325278-f24b0cae1224", 900),
    "pr4.jpg":         ("1600585154340-be6161a56a0c", 1400),
    # materials / macro textures
    "m1.jpg":          ("1604147706283-d7119b5b822c", 800),   # marble
    "m2.jpg":          ("1541123437800-1bb1317badc2", 800),   # wood?
    "m3.jpg":          ("1519974719765-e6559eac2575", 800),   # concrete?
    "m4.jpg":          ("1528459801416-a9e53bbf4e17", 800),   # texture?
}

for name, (pid, w) in files.items():
    dest = os.path.join(IMG, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 20000:
        print("skip", name)
        continue
    url = U.format(pid, w)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dest, "wb") as f:
            f.write(data)
        print(name, len(data) // 1024, "KB")
    except Exception as e:
        print("FAIL", name, e)
