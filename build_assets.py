import os
from PIL import Image, ImageOps, ImageEnhance

SRC = r'C:\Users\Hamdy\Downloads\OneDrive_2026-09-24\OPRELL PROFILE'
DST = r'C:\Users\Hamdy\Downloads\Oprell-new\assets\img'

def put(src, dst, w=2000, q=82, bright=1.0, sat=1.0):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert('RGB')
    if bright != 1.0: im = ImageEnhance.Brightness(im).enhance(bright)
    if sat != 1.0:    im = ImageEnhance.Color(im).enhance(sat)
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(os.path.join(DST, dst), quality=q)
    print(dst, im.size)

def crop(src, dst, box, w=1400, q=82):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert('RGB')
    W, H = im.size
    im = im.crop((int(box[0]*W), int(box[1]*H), int(box[2]*W), int(box[3]*H)))
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(os.path.join(DST, dst), quality=q)
    print(dst, im.size)

V = SRC + r'\villa'
J = SRC + r'\JUMEIRAH HILLS'
C = SRC + r'\CFO office'
B = SRC + r'\bedroom render'
K = SRC + r'\Kitchen'
S = SRC + "\\Susan's baking co"
W = SRC + r'\washroom'
JW = SRC + r'\JBR washroom'
O = SRC + r'\office'
L = SRC + r'\landscape'
SH = SRC + r'\Showroom before & drawings'

# hero — bright real living room with pool view
put(V + r'\IMG_1790 copy.jpg', 'hero.jpg')

# projects — real OPRELL projects
put(V + r'\IMG_1805 copy.jpg', 'p1.jpg')            # VILLA 172 — EMIRATES HILLS
put(B + r'\room 3.jpeg',       'p2.jpg')            # AMULFI VILLA 08 — JUMEIRAH BAY
put(C + r'\cfo render.jpg',    'p3.jpg')            # CFO OFFICE — JAFZA LOB 17
put(S + r'\IMG_0026.PNG',      'p4.jpg')            # SUSAN'S BAKING CO
put(JW + r'\O11.png',          'p5.jpg')            # JBR WASHROOM — JLT

# gallery
put(V + r'\IMG_1747-Enhanced-SR copy.jpg', 'g1.jpg')
put(V + r'\RES-3.jpg',                     'g2.jpg')
put(K + r'\kitchen edit.jpg',              'g3.jpg')
put(O + r'\image_50377985.JPG',            'g4.jpg')
put(L + r'\1b474ff7-632b-480d-afb3-e5262263d33e.jpg', 'g5.jpg')
put(V + r'\r3.jpg',                        'g6.jpg')
put(SH + r'\showroom office 1.jpg',        'g7.jpg')

# before / after — real showroom transformation
put(SH + r'\IMG_1919.JPG',          'ba-before.jpg')
put(SH + r'\showroom office 1.jpg', 'ba.jpg')

# statement reveal
put(V + r'\RES-3.jpg', 'transform.jpg')

# about
put(O + r'\image_50377985.JPG', 'a1.jpg')
put(K + r'\kitchen edit.jpg',   'a2.jpg')
put(B + r'\room 1.jpeg',        'a3.jpg')

# process — concept render / design materials / build site / delivery
put(B + r'\room 1.jpeg',   'pr1.jpg')
put(K + r'\kitchen edit.jpg', 'pr2.jpg')
put(SH + r'\IMG_1921.JPG', 'pr3.jpg')
put(V + r'\RES-2.jpg',     'pr4.jpg')

# materials — crops from real imagery
crop(V + r'\IMG_1747-Enhanced-SR copy.jpg', 'm1.jpg', (0.52, 0.05, 0.98, 0.85))  # stone wall
crop(V + r'\IMG_1790 copy.jpg',  'm-wood.jpg',    (0.30, 0.80, 0.80, 1.00))   # wood floor
crop(B + r'\room 3.jpeg',        'm-texture.jpg', (0.72, 0.05, 1.00, 0.85))   # terracotta wall
crop(V + r'\RES-2.jpg',          'm-light.jpg',   (0.30, 0.02, 0.75, 0.45))   # pendants
crop(O + r'\image_50377985.JPG', 'm-metal.jpg',   (0.00, 0.05, 0.32, 0.85))   # metal/glass frames
crop(B + r'\room 3.jpeg',        'm-fabric.jpg',  (0.02, 0.55, 0.55, 0.98))   # bedding fabric

print('done')
