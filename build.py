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
for _f in ('css/theme.css', 'css/components.css', 'js/site.js', 'js/page.js'):
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
    r'<img\b([^>]*?)(?<![\w-])src="((?:\.\./)?assets/proj/([\w/-]+)\.jpg)"([^>]*)>')


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
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Red+Hat+Display:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
<meta property="og:site_name" content="OPRELL Interiors &amp; Fit-Out">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{path}">
<meta property="og:image" content="{SITE}/{og_img}">
<meta name="twitter:card" content="summary_large_image">
{extra}<link rel="stylesheet" href="{root}css/theme.css?{V}">
<link rel="stylesheet" href="{root}css/components.css?{V}">
<noscript><style>.page-loader{{display:none!important}}</style></noscript>
</head>
"""


ARROW_R = ('<svg class="nav-link-cta-arrow icon icon-18" viewBox="0 0 24 24" aria-hidden="true">'
           '<path d="M13.2 5.2a1 1 0 0 1 1.4 0l6.2 6.2a1 1 0 0 1 0 1.4l-6.2 6.2a1 1 0 1 1-1.4-1.4'
           'l4.5-4.5H4a1 1 0 0 1 0-2h13.7l-4.5-4.5a1 1 0 0 1 0-1.4Z"/></svg>')
ARROW_INLINE = ('<svg class="icon icon-18" viewBox="0 0 24 24" aria-hidden="true">'
                '<path d="M13.2 5.2a1 1 0 0 1 1.4 0l6.2 6.2a1 1 0 0 1 0 1.4l-6.2 6.2a1 1 0 1 1-1.4-1.4'
                'l4.5-4.5H4a1 1 0 0 1 0-2h13.7l-4.5-4.5a1 1 0 0 1 0-1.4Z"/></svg>')
BURGER_SVG = ('<svg class="icon icon-22" viewBox="0 0 24 24" aria-hidden="true">'
              '<path d="M4 7a1 1 0 0 1 1-1h14a1 1 0 1 1 0 2H5a1 1 0 0 1-1-1Zm0 5a1 1 0 0 1 1-1h14'
              'a1 1 0 1 1 0 2H5a1 1 0 0 1-1-1Zm1 4a1 1 0 1 0 0 2h14a1 1 0 1 0 0-2H5Z"/></svg>')
CLOSE_SVG = ('<svg class="icon icon-22" viewBox="0 0 24 24" aria-hidden="true">'
             '<path d="M6.3 5a1 1 0 0 1 1.4 0L12 9.3 16.3 5a1 1 0 1 1 1.4 1.4L13.4 10.7 17.7 15'
             'a1 1 0 1 1-1.4 1.4L12 12.1l-4.3 4.3A1 1 0 0 1 6.3 15l4.3-4.3L6.3 6.4a1 1 0 0 1 0-1.4Z"/></svg>')
CHEV_DN = ('<svg class="icon icon-20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>')
CHEV_UP = ('<svg class="icon icon-20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" aria-hidden="true"><path d="M18 15l-6-6-6 6"/></svg>')

NAV_ITEMS = [('Home', '{home}'), ('About us', '{root}about/'),
             ('Projects', '{root}projects/')]
SERVICES_DD = [('Interior Design', 'interior-design'), ('Fit-Out & Joinery', 'fit-out-joinery'),
               ('Design + Build', 'design-build'),
               ('Landscape & Pools', 'landscape-pools'), ('Project Management', 'project-management')]


def chrome_top(root, home, inner):
    nav = '\n      '.join(
        f'<a class="nav-link" href="{h.format(root=root, home=home)}">{t}</a>'
        for t, h in NAV_ITEMS[:1])
    nav2 = '\n      '.join(
        f'<a class="nav-link" href="{h.format(root=root, home=home)}">{t}</a>'
        for t, h in NAV_ITEMS[1:])
    dd = '\n          '.join(
        f'<a class="nav-dropdown-link" href="{root}services/#{a}" role="menuitem">{t}</a>'
        for t, a in SERVICES_DD)
    mnav = '\n      '.join(
        f'<a class="mobile-nav-link" href="{h.format(root=root, home=home)}">{t}</a>'
        for t, h in NAV_ITEMS[:1])
    mnav2 = '\n      '.join(
        f'<a class="mobile-nav-link" href="{h.format(root=root, home=home)}">{t}</a>'
        for t, h in NAV_ITEMS[1:])
    mdd = '\n          '.join(
        f'<a class="mobile-nav-link" href="{root}services/#{a}">{t}</a>'
        for t, a in SERVICES_DD)
    return f"""<body{' class="inner"' if inner else ''}>

<div class="page-loader" id="page-loader">
  <div class="page-loader-content">
    <div class="page-loader-logo"><img src="{root}assets/logo-white.png" alt="OPRELL Interiors"></div>
    <div class="page-loader-spinner"></div>
  </div>
</div>
<a class="skip-link" href="#main">Skip to content</a>
<div class="scroll-rail" data-variant="dark" role="slider" aria-label="Scroll"
     aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" tabindex="0">
  <div class="scroll-rail-fill" aria-hidden="true"></div>
  <div class="scroll-rail-thumb" aria-hidden="true"></div>
</div>

<header class="site-header is-visible">
  <div class="container header-inner">
    <a class="brand" href="{home}" aria-label="OPRELL Home">
      <img class="brand-logo" src="{root}assets/logo.png" alt="OPRELL Interiors">
    </a>
    <nav class="nav-shell" aria-label="Primary">
      {nav}
      <div class="nav-dropdown">
        <button class="nav-link nav-dropdown-toggle" type="button" aria-haspopup="true" aria-expanded="false">
          Our Services +
        </button>
        <div class="nav-dropdown-menu" role="menu" aria-label="Our services">
          {dd}
        </div>
      </div>
      {nav2}
    </nav>
    <div class="header-actions">
      <a class="nav-link nav-link-cta" href="{root}contact/">Contact us {ARROW_R}</a>
      <button class="menu-button" type="button" aria-haspopup="dialog" aria-expanded="false">
        <span class="sr-only">Open menu</span>{BURGER_SVG}
      </button>
    </div>
  </div>
</header>

<div class="menu-overlay" hidden></div>
<div class="mobile-menu" role="dialog" aria-modal="true" aria-label="Mobile menu">
  <div class="mobile-menu-inner">
    <div class="mobile-menu-top">
      <a class="brand" href="{home}" aria-label="OPRELL Home">
        <img class="brand-logo" src="{root}assets/logo.png" alt="OPRELL Interiors">
      </a>
      <button class="menu-close" type="button">
        <span class="sr-only">Close menu</span>{CLOSE_SVG}
      </button>
    </div>
    <nav class="mobile-nav" aria-label="Mobile primary">
      {mnav}
      <button class="mobile-nav-toggle" type="button" aria-expanded="false">
        <div class="mobile-nav-toggle-header">
          <span class="mobile-nav-title">Our Services</span>
          <i class="fa-solid fa-plus mobile-nav-toggle-icon" style="font-size: 12px;"></i>
        </div>
        <div class="mobile-nav-links">
          {mdd}
        </div>
      </button>
      {mnav2}
      <a class="mobile-nav-link nav-link-cta" href="{root}contact/">Contact us {ARROW_R}</a>
    </nav>
  </div>
</div>
"""


def chrome_bottom(root, home, cta=True):
    band = f"""
<section class="iconic-banner" aria-label="Start a project">
  <div class="iconic-banner-bg" style="background-image:url('{root}assets/proj/hr-office/62759850.png')"></div>
  <div class="iconic-banner-inner">
    <div class="iconic-banner-kicker">Start a project</div>
    <h2 class="iconic-banner-title">HAVE A SPACE IN MIND? <span class="accent">LET'S BUILD IT.</span></h2>
    <a class="btn btn-primary" href="{root}contact/" style="margin-top:26px">Contact us {ARROW_INLINE}</a>
  </div>
</section>""" if cta else ''
    return band + f"""
<footer class="footer" id="contact">
  <div class="container footer-top">
    <div class="footer-grid">
      <div class="footer-col">
        <div class="footer-brand">
          <img class="footer-logo" src="{root}assets/logo.png" alt="OPRELL Interiors">
        </div>
        <div class="footer-social-grid" aria-label="Social links">
          <a class="social-link" href="{IG}" target="_blank" rel="noopener" aria-label="Instagram"><i class="fa-brands fa-instagram"></i></a>
          <a class="social-link" href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>
        </div>
      </div>
      <div class="footer-col">
        <div class="footer-title">Our services</div>
        <nav class="footer-links" aria-label="Footer services">
          <a href="{root}services/">Interior Design</a>
          <a href="{root}services/">Fit-Out &amp; Joinery</a>
          <a href="{root}services/">Design + Build</a>
          <a href="{root}services/">Villa Renovation</a>
          <a href="{root}services/">Landscape &amp; Pools</a>
        </nav>
      </div>
      <div class="footer-col">
        <div class="footer-title">Company</div>
        <nav class="footer-links" aria-label="Footer company">
          <a href="{home}">Home</a>
          <a href="{root}about/">About us</a>
          <a href="{root}projects/">Projects</a>
          <a href="{root}contact/">Contact us</a>
        </nav>
      </div>
      <div class="footer-col">
        <div class="footer-title">Contact</div>
        <div class="footer-meta muted">
          <div>Grosvenor Business Tower, Barsha Heights, Dubai, UAE</div>
          <a class="footer-contact" href="mailto:{EMAIL}">{EMAIL}</a>
          <a class="footer-contact" href="{PHONE_TEL}">{PHONE_DISP}</a>
        </div>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <div class="muted">© <span id="year">2026</span> OPRELL Interiors &amp; Fit-Out. All rights reserved.</div>
      <nav class="footer-legal" aria-label="Footer legal">
        <a href="#" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;">Back to top</a>
      </nav>
    </div>
  </div>
</footer>
"""


def scripts(root, js):
    extra = f'<script src="{root}js/{js}?{V}"></script>' if js else ''
    return f"""
<script src="{root}js/site.js?{V}"></script>
{extra}
<script>
/* failsafe — if the JS bundle died, never leave the loader up */
addEventListener('load', () => setTimeout(() => {{
  const l = document.getElementById('page-loader');
  if (l) l.classList.add('is-hidden');
}}, 2600));
</script>
</body>
</html>
"""


JSONLD = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"LocalBusiness",
 "name":"OPRELL Interiors & Fit-Out",
 "description":"Dubai design and build practice — interior design, fit-out, joinery and landscape works across the UAE.",
 "url":"https://oprell.ae/","email":"contact@oprell.ae","telephone":"+971525201792",
 "image":"https://oprell.ae/assets/proj/villa-01.jpg",
 "address":{"@type":"PostalAddress","streetAddress":"Grosvenor Business Tower, Barsha Heights","addressLocality":"Dubai","addressCountry":"AE"},
 "sameAs":["https://www.instagram.com/oprell_interiors"]}
</script>
"""

# ------------------------------------------------------------- pages --------
PAGES = [
    dict(file='index.html', frag='index', js=None, inner=False, path='',
         og='assets/proj/villa-01.jpg', extra=JSONLD,
         title='OPRELL Interiors &amp; Fit-Out — Dubai',
         desc='OPRELL Interiors & Fit-Out — Dubai design and build practice. Interior design, fit-out, villa renovation and landscape works across the UAE.'),
    dict(file='services/index.html', frag='services', js=None, inner=True, path='services/',
         og='assets/proj/villa-11.jpg',
         title='Services — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='Interior design, fit-out, design + build, villa renovation, landscape and project management — delivered entirely in-house across the UAE.'),
    dict(file='projects/index.html', frag='projects', js=None, inner=True, path='projects/',
         og='assets/proj/villa-03.jpg',
         title='Projects — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='Selected OPRELL projects — residential villas, commercial offices and F&B fit-outs delivered across the UAE, 2022–2024.'),
    dict(file='about/index.html', frag='about', js=None, inner=True, path='about/',
         og='assets/proj/office-08.jpg',
         title='About — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='OPRELL Interiors & Fit-Out — a Dubai design and build practice established 2020. 165+ in-house workforce, ISO 9001 · 14001 · 45001 certified.'),
    dict(file='contact/index.html', frag='contact', js=None, inner=True, path='contact/',
         og='assets/proj/landscape-09.jpg',
         title='Contact — OPRELL Interiors &amp; Fit-Out, Dubai',
         desc='Start a project with OPRELL — interior design and fit-out across the UAE. contact@oprell.ae · +971 52 520 1792 · Barsha Heights, Dubai.'),
]


# ------------------------------------------------------------- projects -----
def imgs(slug, first=None):
    """All source images inside assets/proj/<slug>/ as 'slug/name.jpg' paths.

    first: optional filename to pin as the lead/cover image.
    """
    exts = {'.jpg', '.jpeg', '.png'}
    files = sorted(
        f'{slug}/{os.path.basename(p)}'
        for p in glob.glob(f'assets/proj/{slug}/*')
        if os.path.isfile(p)
        and os.path.splitext(p)[1].lower() in exts
        and not p.lower().endswith('-800.webp'))
    if first and f'{slug}/{first}' in files:
        files.remove(f'{slug}/{first}')
        files.insert(0, f'{slug}/{first}')
    return files


PROJECTS = [
    dict(slug='susans-baking', num='01', title="Susan's Baking Co.",
         meta='Retail / F&B fit-out — Dubai',
         sector='Retail / F&B', location='Dubai', status='Delivered',
         desc="A retail and F&B fit-out for Susan's Baking Co. — counters, shelving, display units and finishes built in our joinery to the brand palette. From drawings to opening day under one team.",
         quote=('We are proud to showcase our bakery and coffee shop set-up, and we owe it all to the expertise of Oprell Interiors.',
                "Susan's Bakery & Co."),
         images=imgs('susans-baking')),
    dict(slug='cfo-office', num='02', title='CFO Office - DP World',
         meta='Commercial fit-out — Jafza LOB 17, Dubai',
         sector='Commercial', location='Jafza LOB 17, Dubai', status='Delivered',
         desc='An executive office fit-out for DP World at Jafza LOB 17 — designed, produced and installed by our in-house team. From the 3D proposal through fit-out works to handover.',
         quote=('The transformation is truly remarkable and has left a lasting impression on both our clients and employees.',
                'DP World'),
         images=imgs('cfo-office', first='86856087.jpg')),
    dict(slug='hr-office', num='03', title='HR Office',
         meta='Commercial fit-out — Jafza LOB 15, Dubai',
         sector='Commercial', location='Jafza LOB 15, Dubai', status='Delivered',
         desc='An HR department office fit-out at Jafza LOB 15 — workstations, partitions, ceiling and services delivered by OPRELL in-house trades.',
         quote=None,
         images=imgs('hr-office')),
    dict(slug='jlt-hanfinia', num='06', title='JLT, Hanfinia',
         meta='Renovation — JLT, Dubai',
         sector='Renovation', location='JLT, Dubai', status='Delivered',
         desc='A complete renovation in JLT — stripped to the shell, replumbed and refitted with marble finishes, brass fittings and custom joinery, shown here from the original state to the design proposal and the finished room.',
         quote=('Not only does the new bathroom meet our practical needs, but it also elevates our entire space.',
                'JLT Washroom Client'),
         images=imgs('jlt-hanfinia')),
    dict(slug='dubai-hills', num='07', title='Dubai Hills Villa',
         meta='Residential — Dubai Hills, Dubai',
         sector='Residential', location='Dubai Hills, Dubai', status='Delivered',
         desc='A family villa in Dubai Hills — interior design, joinery and finishes documented from site progress to the finished home.',
         quote=None,
         images=imgs('dubai-hills', first='11641661.jpg')),
    dict(slug='villa-798', num='08', title='Private Villa, District One',
         meta='Residential — District One, Dubai',
         sector='Residential', location='District One, Dubai', status='Delivered',
         desc='A complete villa interior in District One, MBR City — documented across every stage from first site photos to the finished rooms.',
         quote=None,
         images=imgs('villa-798', first='92823847.jpg')),
    dict(slug='villa-arabian-ranches', num='09', title='Private Villa, Arabian Ranches',
         meta='Residential — Arabian Ranches, Dubai',
         sector='Residential', location='Arabian Ranches, Dubai', status='Delivered',
         desc='A private villa interior in Arabian Ranches — designed, produced and installed by the OPRELL in-house team.',
         quote=None,
         images=imgs('villa-arabian-ranches', first='54741262.jpg')),
    dict(slug='villa-arabian-ranches-1', num='10', title='Private Villa 2, Arabian Ranches',
         meta='Residential — Arabian Ranches, Dubai',
         sector='Residential', location='Arabian Ranches, Dubai', status='Delivered',
         desc='A second private villa interior in Arabian Ranches — photographed through the works to handover.',
         quote=None,
         images=imgs('villa-arabian-ranches-1', first='24166224.jpg')),
    dict(slug='villa-saheel', num='11', title='Private Villa, Saheel',
         meta='Residential — Saheel, Arabian Ranches',
         sector='Residential', location='Saheel, Arabian Ranches', status='Delivered',
         desc='A private villa in Saheel, Arabian Ranches — interior works delivered end-to-end by one accountable team.',
         quote=None,
         images=imgs('villa-saheel', first='24172882.jpg')),
    dict(slug='villa-saheel-1', num='12', title='Private Villa 2, Saheel',
         meta='Residential — Saheel, Arabian Ranches',
         sector='Residential', location='Saheel, Arabian Ranches', status='Delivered',
         desc='A second private villa in Saheel, Arabian Ranches — full documentation from site progress to finished rooms.',
         quote=None,
         images=imgs('villa-saheel-1')),
    dict(slug='jumeirah-bay', num='13', title='Jumeirah Bay Villa',
         meta='Residential — Jumeirah Bay, Dubai',
         sector='Residential', location='Jumeirah Bay, Dubai', status='Delivered',
         desc='A private villa interior on Jumeirah Bay — joinery, finishes and detailing produced and installed in-house.',
         quote=None,
         images=imgs('jumeirah-bay', first='85162815.jpg')),
    dict(slug='jumeirah-golf-estate', num='14', title='Private Villa, Jumeirah Golf Estates',
         meta='Residential — Jumeirah Golf Estates, Dubai',
         sector='Residential', location='Jumeirah Golf Estates, Dubai', status='Delivered',
         desc='A private villa in Jumeirah Golf Estates — documented through site progress to the finished interior.',
         quote=None,
         images=imgs('jumeirah-golf-estate', first='50972804.jpg')),
    dict(slug='jumeirah-palm', num='15', title='Private Villa, Jumeirah Palm',
         meta='Residential — Palm Jumeirah, Dubai',
         sector='Residential', location='Palm Jumeirah, Dubai', status='Delivered',
         desc='A private villa interior on the Palm Jumeirah — delivered by OPRELL design and build teams.',
         quote=None,
         images=imgs('jumeirah-palm')),
    dict(slug='jumeirah-villa', num='16', title='Private Villa, Jumeirah',
         meta='Residential — Jumeirah, Dubai',
         sector='Residential', location='Jumeirah, Dubai', status='Delivered',
         desc='A private villa in Jumeirah — interior works from first visit photos through to the finished spaces.',
         quote=None,
         images=imgs('jumeirah-villa', first='45390960.jpg')),
    dict(slug='maeen-villa', num='17', title='Maeen Private Villa, The Lakes',
         meta='Residential — The Lakes, Dubai',
         sector='Residential', location='The Lakes, Dubai', status='Delivered',
         desc='A private villa renovation at The Lakes — room-by-room documentation from before to finished.',
         quote=None,
         images=imgs('maeen-villa', first='3720514.jpg')),
    dict(slug='meadows', num='18', title='Meadows Villa',
         meta='Residential renovation — Meadows, Dubai',
         sector='Renovation', location='Meadows, Dubai', status='Delivered',
         desc='A Meadows villa renovation delivered in stages — documented before, during and after the works.',
         quote=None,
         images=imgs('meadows', first='40689616.jpg')),
    dict(slug='landscape', num='19', title='Landscape & Pool Works',
         meta='Outdoor works — UAE',
         sector='Landscape', location='UAE', status='Delivered',
         desc='Landscape and outdoor works across the UAE — planting, hardscape, irrigation and pool surroundings executed as part of our design-and-build programme.',
         quote=None,
         images=imgs('landscape')),
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
<section class="projects-hero" id="hero">
  <div class="projects-hero-bg" style="background-image:url('{hero_img}')"></div>
  <div class="projects-hero-overlay"></div>
  <div class="container projects-hero-inner">
    <nav class="crumbs" aria-label="Breadcrumb"><ol>
      <li><a href="../">Home</a></li>
      <li><a href="../projects/">Projects</a></li>
      <li aria-current="page"><span>{t}</span></li>
    </ol></nav>
    <div class="projects-hero-kicker">{html.escape(p['sector'])} · {html.escape(p['location'])}</div>
    <h1 class="projects-hero-title">{t}</h1>
    <p class="projects-hero-lead">{html.escape(p['meta'])}</p>
  </div>
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

def cover_src(p):
    """Best card image for a project — flat highlight first, then imported cover.
    Prefers .webp so the file isn't re-wrapped in a <picture> by enhance_imgs."""
    if p['images']:
        stem = p['images'][0]
        for cand in (f'assets/proj/{stem[:-4]}.webp', f'assets/proj/{stem}'):
            if stem.lower().endswith('.jpg') and os.path.exists(cand):
                return cand
        return f'assets/proj/{stem}'
    c = p.get('cover')
    if c:
        for cand in (f'assets/proj/{c}-800.webp', f'assets/proj/{c}.webp'):
            if os.path.exists(cand):
                return cand
    return ''


STATUS_MAP = {'delivered': 'completed', 'in progress': 'in_progress',
              'ongoing programme': 'in_progress', 'ongoing': 'in_progress',
              'design stage': 'upcoming', 'upcoming': 'upcoming'}


GRID_ICON = '<i class="fa-regular fa-images" aria-hidden="true"></i>'
EXPAND_ICON = '<i class="fa-solid fa-expand" aria-hidden="true"></i>'


def project_photos(p):
    """Full-size gallery image URLs for a project (webp where available)."""
    out = []
    for src in p['images']:
        st = src[:-4] if src.lower().endswith('.jpg') else src
        out.append(f'assets/proj/{st}.webp'
                   if os.path.exists(f'assets/proj/{st}.webp')
                   else f'assets/proj/{src}')
    for s in p.get('sections', []):
        out += [f'assets/proj/{stem}.webp' for stem in s['images']]
    return out


def project_rows():
    rows = []
    for i, p in enumerate(PROJECTS):
        t = html.escape(p['title'])
        cat = re.sub(r'[^a-z]+', '_', p['sector'].lower()).strip('_')
        loc = html.escape(p.get('location', 'Dubai'))
        city = html.escape(p['location'].split(',')[-1].strip())
        status = STATUS_MAP.get(p['status'].lower(), 'completed')
        img = cover_src(p)
        rev = ' project-row--reverse' if i % 2 else ''
        media = (f'<img src="../{img}" alt="{t}" loading="lazy">' if img
                 else '<span class="project-media-empty">OPRELL</span>')
        photos = html.escape(json.dumps([f'../{u}' for u in project_photos(p)]), quote=True)
        rows.append(f"""      <article class="project-row{rev}" id="project-{p['slug']}" data-category="{cat}" data-status="{status}" data-city="{city}">
        <div class="project-row-media" data-photos="{photos}" tabindex="0" role="button" aria-label="Open {t} gallery">
          {media}
          <span class="project-status project-status-{status}">{html.escape(p['status'])}</span>
          <div class="project-media-actions">
            <button class="pma-btn" type="button" data-open-gallery aria-label="Open gallery">{GRID_ICON}</button>
            <button class="pma-btn" type="button" data-open-full aria-label="Open fullscreen">{EXPAND_ICON}</button>
          </div>
        </div>
        <div class="project-row-body">
          <p class="project-row-eyebrow">{html.escape(p['sector'])} · {loc}</p>
          <h2 class="project-row-title">{t}</h2>
          <p class="project-row-summary">{html.escape(p['desc'])}</p>
          <dl class="project-row-facts">
            <div class="project-row-fact"><dt>Sector</dt><dd>{html.escape(p['sector'])}</dd></div>
            <div class="project-row-fact"><dt>Location</dt><dd>{loc}</dd></div>
            <div class="project-row-fact"><dt>Status</dt><dd>{html.escape(p['status'])}</dd></div>
          </dl>
        </div>
      </article>""")
    return '\n'.join(rows)


FEATURED = ('susans-baking', 'cfo-office', 'villa-arabian-ranches', 'dubai-hills')

FEATURED_BLURBS = {
    'susans-baking': 'Counters and display units for Dubai’s artisan bakery.',
    'cfo-office': 'Executive office for DP World, built entirely in-house.',
    'villa-arabian-ranches': 'A private villa interior in Arabian Ranches, built in-house.',
    'dubai-hills': 'A family villa in Dubai Hills, documented to delivery.',
    'villa-798-mbr-city-district-one': 'A complete interior transformation in District One.',
    'maeen-villa-165-the-lakes': 'A full villa renovation at The Lakes community.',
    'landscape': 'Gardens, hardscape and pools built by our own crews.',
    'meadows-2': 'A Meadows villa renovation, delivered in stages.',
}


MAP_GEO = [
    ('arabian ranches 2', 55.250, 25.030),
    ('arabian ranches', 55.268, 25.045),
    ('dubai hills', 55.248, 25.110),
    ('district one', 55.318, 25.165),
    ('mbr city', 55.318, 25.165),
    ('jumeirah golf', 55.205, 24.985),
    ('jumeirah bay', 55.252, 25.215),
    ('jumeirah park', 55.170, 25.040),
    ('jumeirah hills', 55.200, 25.050),
    ('jumeirah islands', 55.155, 25.060),
    ('palm jumeirah', 55.135, 25.110),
    ('jumeirah', 55.240, 25.190),
    ('the lakes', 55.165, 25.058),
    ('meadows', 55.152, 25.050),
    ('jafza', 55.080, 24.990),
    ('jlt', 55.145, 25.070),
    ('barsha heights', 55.175, 25.095),
    ('tecom', 55.175, 25.095),
    ('al quoz', 55.220, 25.140),
    ('dubai', 55.270, 25.200),
]


def geo_xy(lon, lat):
    W, N, E, S = 51.530570, 26.079028, 56.382213, 22.496694
    return round((lon - W) / (E - W) * 760.1441, 1), round((N - lat) / (N - S) * 612.5336, 1)


def map_locations_json():
    locs = []
    for i, p in enumerate(PROJECTS):
        text = (p['location'] + ' ' + p['title']).lower()
        lon, lat = next(((ln, lt) for kw, ln, lt in MAP_GEO if kw in text),
                      (55.270, 25.200))
        jx = ((i % 3) - 1) * 7.0
        jy = ((i % 2) - 0.5) * 9.0
        x, y = geo_xy(lon, lat)
        locs.append({
            'id': p['slug'], 'slug': p['slug'], 'title': p['title'],
            'city': 'Dubai', 'type': 'project',
            'x': round(x + jx, 1), 'y': round(y + jy, 1),
            'page': i // 8 + 1,
            'description': p['desc'][:140],
        })
    return json.dumps(locs)


def marquee_items():
    pin = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"'
           ' style="display: inline-block; vertical-align: middle; width: 14px; height: 14px;'
           ' margin-right: 6px; color: rgba(0, 0, 0, 0.6);">'
           '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>'
           '<circle cx="12" cy="10" r="3"></circle></svg>')
    items = []
    for p in PROJECTS:
        t = html.escape(p['title'])
        img = cover_src(p)
        media = (f'<img src="{img}" alt="{t}" class="presence-project-image" loading="lazy">' if img
                 else f'<div class="presence-project-placeholder"><span>{html.escape(p["title"][:2])}</span></div>')
        items.append(f"""          <div class="presence-project-item">
            <a href="projects/#project-{p['slug']}" class="presence-project-link">
              {media}
              <div class="presence-project-info">
                <h4 class="presence-project-title">{t}</h4>
                <p class="presence-project-location">{pin}{html.escape(p['location'])}</p>
                <span class="presence-project-status">{html.escape(p['status'])}</span>
              </div>
            </a>
          </div>""")
    return '\n'.join(items * 2)


def featured_cards():
    by_slug = {p['slug']: p for p in PROJECTS}
    cards = []
    for i, slug in enumerate(FEATURED, 1):
        p = by_slug.get(slug)
        if not p:
            continue
        t = html.escape(p['title'])
        img = cover_src(p)
        media = (f'<img src="{img}" alt="{t}" loading="lazy">' if img
                 else '<span class="project-media-empty">OPRELL</span>')
        cards.append(f"""          <article class="project-card">
            <a href="projects/#project-{p['slug']}" class="project-link">
              <div class="project-media">{media}
                <span class="project-card-n">{i:02d}</span>
              </div>
              <div class="project-body">
                <h3 class="h3">{t}</h3>
                <p class="muted">{html.escape(FEATURED_BLURBS.get(slug, p['desc']))}</p>
              </div>
            </a>
          </article>""")
    return '\n'.join(cards)




def build():
    gen_webp()
    written = []

    for pg in PAGES:
        root = '' if not pg['inner'] else '../'
        home = '#top' if not pg['inner'] else '../'
        body = open('content/' + pg['frag'] + '.html', encoding='utf-8').read()
        body = body.replace('%%PROJECT_ROWS%%', project_rows()) \
                   .replace('%%FEATURED_CARDS%%', featured_cards()) \
                   .replace('%%MAP_LOCATIONS%%', map_locations_json()) \
                   .replace('%%MAP_MARQUEE%%', marquee_items()) \
                   .replace('%%PROJECT_COUNT%%', str(len(PROJECTS)))
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

