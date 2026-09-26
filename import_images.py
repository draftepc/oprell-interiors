import os, io, glob, hashlib, json
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

SRC = r'OneDrive_2026-09-24\OPRELL PROFILE'
DST = 'assets\\proj'
os.makedirs(DST, exist_ok=True)

# folder -> slug  (order matters: first image becomes card/banner)
FOLDERS = {
    'villa': 'villa',
    'JUMEIRAH HILLS': 'jumeirah',
    'CFO office': 'cfo',
    "Susan's baking co": 'susans',
    'JBR washroom': 'jbr',
    'washroom': 'washroom',
    'office': 'office',
    'Showroom before & drawings': 'showroom',
    'landscape': 'landscape',
    'Kitchen': 'kitchen',
    'bedroom render': 'bedroom',
}
EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.jfif'}
MAXW = 2000
Q = 82

manifest = {}
seen_hashes = {}

for folder, slug in FOLDERS.items():
    src_dir = os.path.join(SRC, folder)
    files = sorted(os.listdir(src_dir))
    out = []
    for fn in files:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in EXTS:
            continue
        p = os.path.join(src_dir, fn)
        data = open(p, 'rb').read()
        h = hashlib.md5(data).hexdigest()
        if h in seen_hashes:
            print('  dupe skip:', fn)
            continue
        try:
            im = Image.open(io.BytesIO(data))
            im.load()
        except Exception as e:
            print('  unreadable skip:', fn, str(e)[:60]); continue
        seen_hashes[h] = True
        if im.mode != 'RGB':
            im = im.convert('RGB')
        w, hh = im.size
        if w > MAXW:
            im = im.resize((MAXW, int(hh * MAXW / w)), Image.LANCZOS)
        name = f'{slug}-{len(out)+1:02d}.jpg'
        im.save(os.path.join(DST, name), 'JPEG', quality=Q, optimize=True)
        out.append(name)
        print(f'  {name} <- {fn} ({w}x{hh})')
    manifest[slug] = out

# root-level loose images -> landscape/extras bucket
extra = []
for fn in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, fn)
    if not os.path.isfile(p):
        continue
    ext = os.path.splitext(fn)[1].lower()
    if ext not in EXTS:
        continue
    low = fn.lower()
    if 'bg' in low or 'background' in low or 'slide' in low:
        continue  # ppt slide backgrounds, not project photos
    data = open(p, 'rb').read()
    h = hashlib.md5(data).hexdigest()
    if h in seen_hashes:
        print('dupe root skip:', fn); continue
    try:
        im = Image.open(io.BytesIO(data)); im.load()
    except Exception as e:
        print('unreadable root:', fn); continue
    seen_hashes[h] = True
    if im.mode != 'RGB':
        im = im.convert('RGB')
    w, hh = im.size
    if w > MAXW:
        im = im.resize((MAXW, int(hh * MAXW / w)), Image.LANCZOS)
    name = f'misc-{len(extra)+1:02d}.jpg'
    im.save(os.path.join(DST, name), 'JPEG', quality=Q, optimize=True)
    extra.append(name)
    print(f'{name} <- {fn} ({w}x{hh})')
manifest['misc'] = extra

json.dump(manifest, open('image_manifest.json', 'w'), indent=1)
print('\nTOTALS:', {k: len(v) for k, v in manifest.items()})
