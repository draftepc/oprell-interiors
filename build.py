"""Build the OPRELL static site.

All pages are assembled from shared partials (head / header / mobile nav /
footer / scripts) so a change to the chrome is made once, not 14 times.

Sources:
  content/*.html     - <main> fragments for the hand-written pages
  PROJECTS below     - data for the generated project-* pages
  assets/proj/*.jpg  - project photography (webp variants generated here)

Run:  python build.py
Outputs are the index.html / <dir>/index.html files - GENERATED, do not edit
them directly (edits get overwritten). Edit content/*.html or this file.
"""
import html
import json
import os
import re
import glob

SITE = 'https://oprell.ae'
import hashlib
_h = hashlib.md5()
for _f in ('css/style.css', 'js/common.js', 'js/page.js', 'js/home.js'):
    try:
        _h.update(open(_f, 'rb').read())
    except OSError:
        pass
V = 'v=' + _h.hexdigest()[:10]  # auto-bust caches whenever css/js changes
EMAIL = 'contact@oprell.ae'
PHONE_DISP = '+971 52 520 1792'
PHONE_TEL = 'tel:+971525201792'
WA = 'https://wa.me/971525201792'
IG = 'https://www.instagram.com/oprell_interiors'
ADDR = 'Grosvenor Business Tower<br>Barsha Heights, Dubai, UAE'

# ---------------------------------------------------------------- images ----
def gen_webp():
    """Create assets/proj/{name}.webp (<=1600w) and {name}-800.webp variants."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print('PIL not installed - skipping webp generation')
        return
    for path in sorted(glob.glob('assets/proj/**/*.jp*g', recursive=True)):
        stem = path[:-4]
        im = ImageOps.exif_transpose(Image.open(path))
        w, h = im.size
        mw = min(w, 1600)
        out = stem + '.webp'
        if not os.path.exists(out):
            if mw < w:
                im2 = im.resize((mw, int(h * mw / w)), Image.LANCZOS)
            else:
                im2 = im
            im2.save(out, 'WEBP', quality=80, method=6)
        if w > 900:
            out8 = stem + '-800.webp'
            if not os.path.exists(out8):
                im.resize((800, int(h * 800 / w)), Image.LANCZOS) \
                  .save(out8, 'WEBP', quality=80, method=6)
    print('webp variants ready')


def webp_srcset(root, name):
    """srcset string for the webp variants that exist for assets/proj/{name}.jpg"""
    cands = []
    if os.path.exists(f'assets/proj/{name}-800.webp'):
        cands.append(f'{root}assets/proj/{name}-800.webp 800w')
    main = f'assets/proj/{name}.webp'
    if os.path.exists(main):
        try:
            from PIL import Image
            w = Image.open(main).width
        except Exception:
            w = 1600
        cands.append(f'{root}assets/proj/{name}.webp {w}w')
    return ', '.join(cands)


IMG_RE = re.compile(
    r'<img\b([^>]*?)(?<![\w-])src="((?:\.\./)?assets/proj/([\w-]+)\.jpg)"([^>]*)>')


def enhance_imgs(html_text):
    """Wrap assets/proj jpgs in <picture> with a webp srcset.

    Skipped for imgs whose src is swapped by JS (#pds-img, #lb-img) - a
    <source srcset> would keep overriding the img src after a swap.
    """
    def repl(m):
        pre, src, name, rest = m.groups()
        attrs = pre + rest
        if 'id="pds-img"' in attrs or 'id="lb-img"' in attrs or 'data-nopicture' in attrs:
            return m.group(0)
        ss = webp_srcset(src.split('assets/proj/')[0], name)
        if not ss:
            return m.group(0)
        sizes = '(max-width:640px) 94vw, (max-width:1280px) 88vw, 1200px'
        return (f'<picture><source type="image/webp" '
                f'srcset="{ss}" sizes="{sizes}">'
                f'<img{pre}src="{src}"{rest}></picture>')
    return IMG_RE.sub(repl, html_text)


# ------------------------------------------------------------- partials -----
def head(title, desc, root, path, og_img, extra=''):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#ffffff">
<link rel="canonical" href="{SITE}/{path}">
<link rel="icon" type="image/png" href="{root}assets/mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700&display=swap" rel="stylesheet">
<meta property="og:site_name" content="OPRELL Interiors &amp; Fit-Out">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{path}">
<meta property="og:image" content="{SITE}/{og_img}">
<meta name="twitter:card" content="summary_large_image">
{extra}<link rel="stylesheet" href="{root}css/style.css?{V}">
<noscript><style>.loader{{display:none!important}}.reveal{{opacity:1!important;transform:none!important}}</style></noscript>
</head>
"""


IG_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
          '<rect x="3" y="3" width="18" height="18" rx="5.5"/><circle cx="12" cy="12" r="4"/>'
          '<circle cx="17.3" cy="6.7" r="1.1" fill="currentColor" stroke="none"/></svg>')
WA_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3'
          'A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 '
          '20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3'
          '-2.9c-.3-.4.2-.4.5-.9l.4-.5c.1-.2.1-.4 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3'
          '-.9.9-1.1 2.2-.2 3.9a11.6 11.6 0 0 0 4.5 4.3c1.7.8 2.4.9 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6'
          '.2-1.1.1-1.2l-.7-.3z"/></svg>')


def chrome_top(root, home, inner):
    nav = f"""<nav class="nav" aria-label="Primary">
    <a href="{home}">Home</a>
    <a href="{root}about/">About</a>
    <a href="{root}services/">Services</a>
    <a href="{root}projects/">Projects</a>
    <a href="{root}contact/">Contact</a>
  </nav>"""
    mnav_links = f"""<a href="{home}">Home</a>
  <a href="{root}about/">About</a>
  <a href="{root}services/">Services</a>
  <a href="{root}projects/">Projects</a>
  <a href="{root}contact/">Contact</a>"""
    return f"""<body{' class="inner"' if inner else ''}>

<a class="skip" href="#main">Skip to content</a>

<div class="loader" id="loader" aria-hidden="true">
  <div class="loader-mark"><i></i><i></i></div>
  <span class="loader-word">OPRELL</span>
</div>

<div class="rail" aria-hidden="true"><i></i></div>

<header class="head" id="head">
  <a class="logo" href="{home}" aria-label="OPRELL Interiors"><img src="{root}assets/logo.png" alt="OPRELL Interiors"></a>
  {nav}
  <a class="cta" href="{root}contact/" data-mag>Start a project</a>
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="mnav"><span></span><span></span></button>
</header>

<div class="mnav" id="mnav" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Menu" inert>
  <button class="mnav-close" id="mnav-close" aria-label="Close menu">Close ×</button>
  {mnav_links}
  <div class="mnav-foot"><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{PHONE_TEL}">{PHONE_DISP}</a></div>
</div>
"""


def chrome_bottom(root, home, cta=True):
    band = f"""
<section class="cta-band reveal" aria-label="Start a project">
  <div class="cta-band-in">
    <span class="cta-ghost" aria-hidden="true">OPRELL</span>
    <div class="cta-band-l">
      <span class="pill pill-d"><i></i>Start a project</span>
      <h2 class="cta-band-t">Have a space in mind?<br><em>Let&rsquo;s build it.</em></h2>
      <a class="cta-band-btn" href="{root}contact/" data-mag>Get in touch →</a>
    </div>
    <div class="cta-band-r">
      <a href="mailto:contact@oprell.ae">contact@oprell.ae</a>
      <a href="tel:+971525201792">+971 52 520 1792</a>
      <span>Grosvenor Business Tower<br>Barsha Heights, Dubai</span>
    </div>
  </div>
</section>""" if cta else ''
    return band + f"""
<footer class="foot">
  <div class="foot-brand">
    <a class="logo" href="{home}" aria-label="OPRELL Interiors"><img class="foot-logo" src="{root}assets/logo-white.png" alt="OPRELL Interiors"></a>
    <p class="foot-addr">{ADDR}</p>
  </div>
  <nav class="foot-nav" aria-label="Footer">
    <a href="{root}about/">About</a>
    <a href="{root}services/">Services</a>
    <a href="{root}projects/">Projects</a>
    <a href="{root}contact/">Contact</a>
  </nav>
  <div class="foot-contact">
    <a href="mailto:{EMAIL}">{EMAIL}</a>
    <a href="{PHONE_TEL}">{PHONE_DISP}</a>
    <div class="soc">
      <a href="{IG}" target="_blank" rel="noopener" aria-label="Instagram">{IG_SVG}Instagram</a>
      <a href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_SVG}WhatsApp</a>
    </div>
  </div>
  <span class="foot-note">© 2026 OPRELL Interiors — Dubai, UAE</span>
  <div class="foot-mark" aria-hidden="true">OPRELL</div>
</footer>
"""


def scripts(root, js):
    return f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.14/dist/lenis.min.js"></script>
<script src="{root}js/common.js?{V}"></script>
<script src="{root}js/{js}?{V}"></script>
<script>
/* failsafe — if the JS bundle died, never leave the loader up */
addEventListener('load', () => setTimeout(() => {{
  const l = document.getElementById('loader');
  if (l && !document.body.classList.contains('loaded')) {{
    l.remove();
    document.querySelectorAll('.reveal').forEach(e => e.classList.add('in'));
  }}
}}, 2600));
</script>
</body>
</html>
"""


JSONLD = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"LocalBusiness",
 "name":"OPRELL Interiors & Fit-Out",
 "description":"Dubai design and build practice — interior design, fit-out, villa renovation and landscape works across the UAE.",
 "url":"https://oprell.ae/","email":"contact@oprell.ae","telephone":"+971525201792",
 "image":"https://oprell.ae/assets/proj/villa-01.jpg",
 "address":{"@type":"PostalAddress","streetAddress":"Grosvenor Business Tower, Barsha Heights","addressLocality":"Dubai","addressCountry":"AE"},
 "sameAs":["https://www.instagram.com/oprell_interiors"]}
</script>
"""

# ------------------------------------------------------------- pages --------
PAGES = [
    dict(file='index.html', frag='index', js='main.js', inner=False, path='',
         og='assets/proj/villa-01.jpg', extra=JSONLD,
         title='OPRELL Interiors &amp; Fit-Out — Dubai',
         desc='OPRELL Interiors & Fit-Out — Dubai design and build practice. Interior design, fit-out, villa renovation and landscape works across the UAE.'),
    dict(file='services/index.html', frag='services', js='page.js', inner=True, path='services/',
         og='assets/proj/villa-11.jpg',
         title='Services — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='Interior design, fit-out, design + build, villa renovation, landscape and project management — delivered entirely in-house across the UAE.'),
    dict(file='projects/index.html', frag='projects', js='page.js', inner=True, path='projects/',
         og='assets/proj/villa-03.jpg',
         title='Projects — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='Selected OPRELL projects — residential villas, commercial offices and F&B fit-outs delivered across the UAE, 2022–2024.'),
    dict(file='about/index.html', frag='about', js='page.js', inner=True, path='about/',
         og='assets/proj/office-08.jpg',
         title='About — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='OPRELL Interiors & Fit-Out — a Dubai design and build practice established 2020. 165+ in-house workforce, ISO 9001 · 14001 · 45001 certified.'),
    dict(file='contact/index.html', frag='contact', js='page.js', inner=True, path='contact/',
         og='assets/proj/landscape-09.jpg',
         title='Contact — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='Start a project with OPRELL — interior design and fit-out across the UAE. contact@oprell.ae · +971 52 520 1792 · Barsha Heights, Dubai.'),
]


# ------------------------------------------------------------- projects -----
def imgs(slug, extra=()):
    files = sorted(os.path.basename(p)
                   for p in glob.glob(f'assets/proj/{slug}-*.jpg'))
    return list(files) + list(extra)


PROJECTS = [
    dict(slug='hattan-villa', num='01', title='Hattan Villa',
         meta='Residential renovation — Arabian Ranches, Dubai',
         sector='Residential', location='Arabian Ranches, Dubai', status='Delivered',
         desc='A full villa renovation in Hattan, Arabian Ranches — from structural approvals with Emaar to the final finishes, delivered by our in-house team. New joinery, flooring, lighting and a reworked layout tuned to family living.',
         quote=('We had a very positive experience working with Oprell, finding the company to be professional and organized with clear communication and a dedicated contact person. The work was completed to a high standard without any surprises or additional charges.',
                'Hattan Villa Owner'),
         images=imgs('villa')),
    dict(slug='jumeirah-hills', num='02', title='Jumeirah Hills Villa',
         meta='Residential — Jumeirah Hills, Dubai',
         sector='Residential', location='Jumeirah Hills, Dubai', status='Delivered',
         desc='A complete villa design and build in Jumeirah Hills — every room documented from shell to handover. Interior architecture, custom joinery and finishes produced by OPRELL craftsmen.',
         quote=None,
         images=imgs('jumeirah')),
    dict(slug='cfo-office', num='03', title='CFO Office — DP World',
         meta='Commercial fit-out — Jafza LOB 17, Dubai',
         sector='Commercial', location='Jafza LOB 17, Dubai', status='Delivered',
         desc='An executive office fit-out for DP World at Jafza LOB 17 — designed, produced and installed by our in-house team. From the 3D proposal through fit-out works to handover.',
         quote=('The transformation is truly remarkable and has left a lasting impression on both our clients and employees.',
                'DP World'),
         images=imgs('cfo')),
    dict(slug='susans-baking', num='04', title="Susan's Baking Co.",
         meta='Retail / F&B fit-out — Dubai',
         sector='Retail / F&B', location='Dubai', status='Delivered',
         desc="A retail and F&B fit-out for Susan's Baking Co. — counters, shelving, display units and finishes built in our joinery to the brand palette. From drawings to opening day under one team.",
         quote=('We are proud to showcase our bakery and coffee shop set-up, and we owe it all to the expertise of Oprell Interiors.',
                "Susan's Bakery & Co."),
         images=imgs('susans')),
    dict(slug='jlt-washroom', num='05', title='JLT, Hanfinia Washroom',
         meta='Renovation — JLT, Dubai',
         sector='Renovation', location='JLT, Dubai', status='Delivered',
         desc='A complete washroom renovation in JLT — stripped to the shell, replumbed and refitted with marble finishes, brass fittings and custom joinery, shown here from the original state to the design proposal and the finished room.',
         quote=('Not only does the new bathroom meet our practical needs, but it also elevates our entire space.',
                'JLT Washroom Client'),
         images=imgs('jbr') + imgs('washroom')),
    dict(slug='hr-office', num='06', title='HR Office',
         meta='Commercial fit-out — Jafza LOB 15, Dubai',
         sector='Commercial', location='Jafza LOB 15, Dubai', status='Delivered',
         desc='An HR department office fit-out at Jafza LOB 15 — workstations, partitions, ceiling and services delivered by OPRELL in-house trades.',
         quote=None,
         images=imgs('office')),
    dict(slug='trucks-showroom', num='07', title='Trucks Showroom',
         meta='Commercial — Dubai',
         sector='Commercial', location='Dubai', status='In progress',
         desc='A trucks showroom and office — documented from the existing shell through drawings to the design proposal, with fit-out works in progress.',
         quote=None,
         images=imgs('showroom') + ['misc-02.jpg']),
    dict(slug='landscape', num='08', title='Landscape & Pool Works',
         meta='Outdoor works — UAE',
         sector='Landscape', location='UAE', status='Ongoing programme',
         desc='Landscape and outdoor works across the UAE — planting, hardscape, irrigation and pool surroundings executed as part of our design-and-build programme.',
         quote=None,
         images=imgs('landscape') + ['misc-01.jpg', 'misc-03.jpg']),
    dict(slug='kitchen', num='09', title='Kitchen Design',
         meta='Residential interiors — Dubai',
         sector='Residential', location='Dubai', status='Delivered',
         desc='A kitchen designed and produced in our joinery — cabinetry, surfaces and lighting composed around daily use.',
         quote=None,
         images=imgs('kitchen')),
    dict(slug='bedroom', num='10', title='Bedroom Interiors',
         meta='Residential interiors — Dubai',
         sector='Residential', location='Dubai', status='Design stage',
         desc='Bedroom interior concepts produced by our design team — layouts, materials and lighting visualised before execution.',
         quote=None,
         images=imgs('bedroom')),
]


BLANK_GIF = ('data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAAB'
             'AAEAAAICTAEAOw==')

ARROWS = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M19 12H5M11 6l-6 6 6 6"/></svg>')
ARROWR = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')
EXPAND = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>')


def deck_markup(items, alt):
    """items: list of (thumb, full, sec) asset-proj-relative paths -> deck slider."""
    ni = len(items)
    lis = []
    for j, (th, fu, sec) in enumerate(items):
        src = (f'src="../assets/proj/{th}"' if j < 6 else
               f'src="{BLANK_GIF}" data-src="../assets/proj/{th}"')
        tag = (f'<span class="deck-tag">{html.escape(sec)}</span>'
               if sec else '')
        lis.append(
            f'      <li class="deck-slide" data-i="{j}" '
            f'data-sec="{html.escape(sec)}"><img {src} '
            f'data-full="../assets/proj/{fu}" alt="{alt}" '
            f'loading="lazy" decoding="async">{tag}'
            f'<div class="deck-cap"><span class="deck-n">'
            f'{j + 1:02d} / {ni:02d}</span>'
            f'<button class="deck-open" type="button" '
            f'aria-label="Open fullscreen">{EXPAND}</button></div></li>')
    return ('  <div class="pd-deck" data-cursor="drag">\n'
            '    <div class="deck-bg" aria-hidden="true"></div>\n'
            '    <ul class="deck-track">\n' + '\n'.join(lis) + '\n'
            '    </ul>\n'
            '    <nav class="deck-nav" aria-label="Gallery navigation">'
            f'<button class="deck-btn deck-prev" aria-label="Previous photo">'
            f'{ARROWS}</button>'
            f'<button class="deck-btn deck-next" aria-label="Next photo">'
            f'{ARROWR}</button></nav>\n'
            '    <div class="deck-prog" aria-hidden="true"><i></i></div>\n'
            '  </div>\n')


def project_main(p, nxt):
    """<main> + lightbox for a project detail page (paths are ../-relative)."""
    t = html.escape(p['title'])
    sections = p.get('sections', [])
    n = len(p['images'])
    n_sec = sum(len(s['images']) for s in sections)
    if p['images']:
        hero_img = f"../assets/proj/{p['images'][0]}"
    elif p.get('cover'):
        hero_img = f"../assets/proj/{p['cover']}.webp"
    else:
        hero_img = '../assets/proj/villa-03.jpg'

    if nxt['images']:
        nxt_img = nxt['images'][0]
    elif nxt.get('cover'):
        nxt_img = f"{nxt['cover']}.webp"
    elif nxt.get('sections') and nxt['sections'][0]['images']:
        nxt_img = f"{nxt['sections'][0]['images'][0]}-800.webp"
    else:
        nxt_img = 'villa-03.jpg'
    th = re.sub(r'\.\w+$', '-800.webp', nxt_img)
    if th != nxt_img and os.path.exists(f'assets/proj/{th}'):
        nxt_img = th

    # one unified deck: main highlights first, then every source section
    slides = [(src, src, '') for src in p['images']]
    for s in sections:
        slides += [(f'{stem}-800.webp', f'{stem}.webp', s['name'])
                   for stem in s['images']]

    chips = ''
    if len(sections) > 1:
        pos = n
        for s in sections:
            sname = html.escape(s['name'])
            chips += (f'<button class="sec-chip" type="button" data-i="{pos}" '
                      f'data-sec="{sname}">{sname} <i>{len(s["images"])}</i></button>')
            pos += len(s['images'])
        chips = f'  <nav class="pd-secs" aria-label="Gallery sections">{chips}</nav>\n'

    # videos + unrenderable files stay grouped per source section
    files_html = ''
    for s in sections:
        cell = ''
        if s['videos']:
            cell += '  <div class="pd-vids">\n    ' + '\n    '.join(
                f'<video class="gal-vid" src="../assets/proj/{html.escape(rel)}" '
                f'controls preload="metadata" '
                f'aria-label="{html.escape(disp)}"></video>'
                for disp, rel in s['videos']) + '\n  </div>\n'
        links = s['docs'] + s['raw']
        if links:
            cell += '  <ul class="pd-docs">\n    ' + '\n    '.join(
                f'<li><a href="../assets/proj/{html.escape(rel)}" '
                f'download>{html.escape(disp)}</a></li>'
                for disp, rel in links) + '\n  </ul>\n'
        if cell:
            files_html += (f'  <div class="pd-filegrp reveal">'
                           f'<h4 class="pd-filesec">{html.escape(s["name"])}</h4>\n'
                           f'{cell}  </div>\n')
    if files_html:
        files_html = ('  <h3 class="scope-title reveal">Additional media</h3>\n'
                      + files_html)

    if slides:
        gallery = (f'  <h2 class="scope-title reveal">Gallery'
                   f' <span class="gal-n">— {len(slides)} photos</span></h2>\n'
                   f'{chips}'
                   f'{deck_markup(slides, f"{t} — photo")}\n'
                   f'{files_html}')
    elif sections:
        gallery = files_html
    else:
        gallery = ('  <p class="pd-desc reveal" style="margin-top:3.4rem">'
                   'Photography for this project is being prepared '
                   'and will be added soon.</p>\n')

    quote = ''
    if p.get('quote'):
        q, who = p['quote']
        quote = ('  <blockquote class="pd-quote reveal">“' + html.escape(q) +
                 '”<cite>— ' + html.escape(who) + '</cite></blockquote>\n')
    return f"""<main id="main">
<section class="page-hero page-hero-dark">
  <span class="ph-ghost" aria-hidden="true">OPRELL</span>
  <div class="hero-line reveal">
    <nav class="crumbs" aria-label="Breadcrumb"><ol>
      <li><a href="../">Home</a></li>
      <li><a href="../projects/">Projects</a></li>
      <li aria-current="page"><span>{t}</span></li>
    </ol></nav>
    <span class="pill"><i></i>{p['sector']}</span>
  </div>
  <h1 class="reveal d1">{t}<em>.</em></h1>
  <p class="page-sub reveal d2">{html.escape(p['meta'])}</p>
</section>

<section class="pd-body">
  <div class="pd-intro">
    <p class="pd-desc reveal">{html.escape(p['desc'])}</p>
    <table class="pd-facts reveal"><tbody>
      <tr><th>Sector</th><td>{html.escape(p['sector'])}</td></tr>
      <tr><th>Location</th><td>{html.escape(p['location'])}</td></tr>
      <tr><th>Status</th><td>{html.escape(p['status'])}</td></tr>
    </tbody></table>
  </div>
{quote}{gallery}  <a class="pd-next" href="../project-{nxt['slug']}/" data-cursor="view">
    <span class="pd-next-t"><span>Next project</span><b>{html.escape(nxt['title'])} →</b></span>
    <img class="pd-next-img" src="../assets/proj/{nxt_img}" alt="" loading="lazy" decoding="async" data-nopicture></a>
</section>
</main>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Project image viewer" inert>
  <button class="lb-btn lb-close" id="lb-close" aria-label="Close">×</button>
  <button class="lb-btn lb-prev" id="lb-prev" aria-label="Previous image">‹</button>
  <figure class="lb-stage"><img id="lb-img" src="" alt="{t} — gallery image"></figure>
  <button class="lb-btn lb-next" id="lb-next" aria-label="Next image">›</button>
  <span class="lb-count" id="lb-count"></span>
</div>
"""


GENERATED = '<!-- GENERATED by build.py — edit content/*.html or build.py, then re-run -->\n'

# extra projects + gallery sections imported from the Desktop archive
try:
    from projects_new import SECTIONS, EXTRA_PROJECTS
except ImportError:
    SECTIONS, EXTRA_PROJECTS = {}, []
for _p in PROJECTS:
    _extra = SECTIONS.get(_p['slug'])
    if _extra:
        _p.setdefault('sections', []).extend(_extra)
PROJECTS.extend(EXTRA_PROJECTS)


def build():
    gen_webp()
    written = []

    for pg in PAGES:
        root = '' if not pg['inner'] else '../'
        home = '#top' if not pg['inner'] else '../'
        body = open('content/' + pg['frag'] + '.html', encoding='utf-8').read()
        out = (GENERATED + head(pg['title'], pg['desc'], root, pg['path'], pg['og'],
                                pg.get('extra', ''))
               + chrome_top(root, home, pg['inner']) + '\n'
               + body
               + chrome_bottom(root, home, cta=pg['frag'] != 'contact')
               + scripts(root, pg['js']))
        out = enhance_imgs(out)
        if os.path.dirname(pg['file']):
            os.makedirs(os.path.dirname(pg['file']), exist_ok=True)
        open(pg['file'], 'w', encoding='utf-8').write(out)
        written.append(pg['file'])

    for i, p in enumerate(PROJECTS):
        nxt = PROJECTS[(i + 1) % len(PROJECTS)]
        t = html.escape(p['title'])
        og = (f"assets/proj/{p['images'][0]}" if p['images']
              else f"assets/proj/{p['cover']}.webp" if p.get('cover')
              else 'assets/proj/villa-03.jpg')
        out = (GENERATED
               + head(f'{t} — OPRELL Interiors &amp; Fit-Out',
                      html.escape(p['meta']) + ' — designed and built in-house by OPRELL Interiors, Dubai.',
                      '../', f"project-{p['slug']}/", og)
               + chrome_top('../', '../', True) + '\n'
               + project_main(p, nxt)
               + chrome_bottom('../', '../')
               + scripts('../', 'page.js'))
        out = enhance_imgs(out)
        f = f"project-{p['slug']}/index.html"
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, 'w', encoding='utf-8').write(out)
        written.append(f)

    # sitemap + robots stay in sync with the page list
    urls = [''] + [p['path'] for p in PAGES if p['path']] + \
           [f"project-{p['slug']}/" for p in PROJECTS]
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{SITE}/{u}</loc></url>\n' for u in urls)
          + '</urlset>\n')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    open('robots.txt', 'w', encoding='utf-8').write(
        f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')

    print('wrote', len(written), 'pages + sitemap.xml + robots.txt')
    for f in written:
        print('  ', f)


if __name__ == '__main__':
    build()
