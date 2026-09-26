"""Generate the project detail pages (project-*/index.html) from shared data + template.
Pages live in folders so URLs are clean: /project-cfo-office/ not .html
All copy and images come from the OPRELL company profile (OneDrive_2026-09-24\\OPRELL PROFILE).
Run: python build_pages.py
"""
import html
import json
import os

MANIFEST = json.load(open('image_manifest.json'))  # slug -> [files in assets/proj/]


def imgs(slug, extra=None):
    """Ordered image list for a project folder."""
    out = list(MANIFEST[slug])
    for s in (extra or []):
        out += MANIFEST[s]
    return ['../assets/proj/' + f for f in out]


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
    dict(slug='jlt-washroom', num='05', title='JLT Washroom',
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
         images=imgs('showroom') + ['../assets/proj/misc-02.jpg']),
    dict(slug='landscape', num='08', title='Landscape & Pool Works',
         meta='Outdoor works — UAE',
         sector='Landscape', location='UAE', status='Ongoing programme',
         desc='Landscape and outdoor works across the UAE — planting, hardscape, irrigation and pool surroundings executed as part of our design-and-build programme.',
         quote=None,
         images=imgs('landscape') + ['../assets/proj/misc-01.jpg', '../assets/proj/misc-03.jpg']),
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

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — OPRELL Interiors &amp; Fit-Out</title>
<meta name="description" content="{meta} — designed and built in-house by OPRELL Interiors, Dubai.">
<link rel="icon" type="image/png" href="../assets/mark.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/style.css?v=21">
<noscript><style>.loader{{display:none!important}}.cursor{{display:none!important}}.reveal{{opacity:1!important;transform:none!important}}</style></noscript>
</head>
<body class="inner">

<div class="loader" id="loader" aria-hidden="true">
  <div class="loader-mark"><i></i><i></i></div>
  <span class="loader-word">OPRELL</span>
</div>

<div class="cursor" id="cursor" aria-hidden="true"><div class="cur-ring"></div><div class="cur-dot"></div><span class="cur-txt"></span></div>
<div class="rail" aria-hidden="true"><i></i></div>

<header class="head" id="head">
  <a class="logo" href="../" aria-label="OPRELL Interiors"><img src="../assets/logo.png" alt="OPRELL Interiors"></a>
  <nav class="nav" aria-label="Primary">
    <a href="../">Home</a>
    <a href="../services/">Services</a>
    <a href="../projects/">Projects</a>
    <a href="../#transform">Before / After</a>
    <a href="../studio/">Studio</a>
    <a href="../contact/">Contact</a>
  </nav>
  <a class="cta" href="../contact/" data-mag>Start a project</a>
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="mnav"><span></span><span></span></button>
</header>

<div class="mnav" id="mnav" aria-hidden="true" role="dialog" aria-modal="true" inert>
  <button class="mnav-close" id="mnav-close" aria-label="Close menu">Close ×</button>
  <a href="../">Home</a>
  <a href="../services/">Services</a>
  <a href="../projects/">Projects</a>
  <a href="../#transform">Before / After</a>
  <a href="../studio/">Studio</a>
  <a href="../contact/">Contact</a>
  <div class="mnav-foot"><span>contact@oprell.ae</span><span>+971 52 520 1792</span></div>
</div>

<main>
<section class="page-hero" style="--ph:url('{banner}')">
  <div class="hero-line reveal">
    <nav class="crumbs" aria-label="Breadcrumb"><ol>
      <li><a href="../">Home</a></li>
      <li><a href="../projects/">Projects</a></li>
      <li aria-current="page"><span>{title}</span></li>
    </ol></nav>
    <span class="pill"><i></i>N°{num}</span>
  </div>
  <h1 class="reveal d1">{title}<em>.</em></h1>
  <p class="page-sub reveal d2">{meta}</p>
</section>

<section class="pd-body">
  <p class="pd-desc reveal">{desc}</p>
  <div class="pd-facts reveal">Sector — {sector}<br>Location — {location}<br>Status — {status}</div>
{quote_block}
  <h2 class="scope-title reveal">Project gallery</h2>
  <div class="pd-gallery reveal">
{gal_items}
  </div>
  <a class="btn-y pd-next" href="../project-{next_slug}/" data-mag>Next project: {next_title} →</a>
</section>
</main>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Project image viewer" inert>
  <button class="lb-btn lb-close" id="lb-close" aria-label="Close">×</button>
  <button class="lb-btn lb-prev" id="lb-prev" aria-label="Previous image">‹</button>
  <figure class="lb-stage"><img id="lb-img" src="" alt="{title} — gallery image"></figure>
  <button class="lb-btn lb-next" id="lb-next" aria-label="Next image">›</button>
  <span class="lb-count" id="lb-count"></span>
</div>

<footer class="foot">
  <a class="logo" href="../" aria-label="OPRELL Interiors"><img class="foot-logo" src="../assets/logo.png" alt="OPRELL Interiors"></a>
  <nav><a href="../services/">Services</a><a href="../projects/">Projects</a><a href="../studio/">Studio</a><a href="../contact/">Contact</a></nav>
  <span class="foot-note">© 2026 OPRELL Interiors — Dubai, UAE</span>
</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.14/dist/lenis.min.js"></script>
<script src="../js/page.js?v=21"></script>
<script>
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

for i, p in enumerate(PROJECTS):
    nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    banner = p['images'][0]
    gal_items = '\n'.join(
        '    <button class="gal-item" data-i="{0}" aria-label="View image {1} of {2}"><img src="{3}" alt="{4} — photo {1}" loading="lazy" decoding="async"></button>'.format(
            j, j + 1, len(p['images']), src, html.escape(p['title']))
        for j, src in enumerate(p['images']))
    quote_block = ''
    if p.get('quote'):
        q, who = p['quote']
        quote_block = '  <blockquote class="pd-quote reveal">\u201c' + html.escape(q) + '\u201d<cite>— ' + html.escape(who) + '</cite></blockquote>\n'
    out = TEMPLATE.format(
        num=p['num'],
        title=html.escape(p['title']), meta=html.escape(p['meta']),
        banner=banner, desc=html.escape(p['desc']),
        sector=html.escape(p['sector']), location=html.escape(p['location']),
        status=html.escape(p['status']),
        quote_block=quote_block, gal_items=gal_items,
        next_slug=nxt['slug'], next_title=html.escape(nxt['title']))
    folder = 'project-' + p['slug']
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8').write(out)
    print('wrote', folder + '/index.html', len(p['images']), 'images')

# remove folders for retired slugs
import shutil
for d in os.listdir('.'):
    if d.startswith('project-') and os.path.isdir(d):
        if d[8:] not in [p['slug'] for p in PROJECTS]:
            shutil.rmtree(d)
            print('removed old', d)
