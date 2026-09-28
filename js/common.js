/* ============================================================
   OPRELL — shared chrome (all pages)
   loader · cursor · menu · scroll · reveals · counters
   Everything essential works WITHOUT gsap/lenis — they only add
   decoration. If a CDN fails the site stays fully usable.
   ============================================================ */
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE = matchMedia('(hover:hover) and (pointer:fine)').matches;
const HAS_GSAP = !!(window.gsap && window.ScrollTrigger);
if (HAS_GSAP) gsap.registerPlugin(ScrollTrigger);
const ANIM = HAS_GSAP && !REDUCED;          // scroll/entrance animation allowed
const FX = ANIM && FINE;                    // pointer-driven decoration (cursor, tilt, magnetic)

const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

/* ---------------- loader ----------------
   Short delay on first visit, near-instant on repeats / reduced motion. */
const loader = $('#loader');
let seen = false;
try { seen = !!sessionStorage.getItem('op-seen'); } catch (e) {}
const LOADER_MS = REDUCED ? 60 : (seen ? 350 : 1150);
setTimeout(() => {
  if (loader) {
    loader.classList.add('out');
    setTimeout(() => loader.remove(), 600);
  }
  document.body.classList.add('loaded');
  try { sessionStorage.setItem('op-seen', '1'); } catch (e) {}
}, LOADER_MS);

/* ---------------- custom cursor ---------------- */
const cur = $('#cursor');
if (FX && cur) {
  document.body.classList.add('cur-on');
  const cx = gsap.quickTo(cur, 'x', { duration: 0.12, ease: 'power3' });
  const cy = gsap.quickTo(cur, 'y', { duration: 0.12, ease: 'power3' });
  const txt = $('.cur-txt');
  addEventListener('mousemove', e => { cx(e.clientX); cy(e.clientY); });
  document.addEventListener('mouseover', e => {
    const spot = e.target.closest('.ba-spot');
    const view = e.target.closest('[data-cursor="view"]');
    const drag = e.target.closest('[data-cursor="drag"],[data-cursor="swipe"]');
    const hov = spot || e.target.closest('a,button,[data-mag],.svcard,.pcell');
    cur.classList.toggle('view', !!view);
    cur.classList.toggle('drag', !!drag && !spot);
    cur.classList.toggle('hov', !!hov && !view && !drag);
    txt.textContent = view ? 'VIEW' : drag ? drag.dataset.cursor.toUpperCase() : '';
  });
}

/* ---------------- magnetic ---------------- */
if (FX) $$('[data-mag]').forEach(el => {
  el.addEventListener('mousemove', e => {
    const r = el.getBoundingClientRect();
    gsap.to(el, { x: (e.clientX - r.left - r.width/2) * .3, y: (e.clientY - r.top - r.height/2) * .3, duration: .4, ease: 'power3.out' });
  });
  el.addEventListener('mouseleave', () => gsap.to(el, { x: 0, y: 0, duration: .7, ease: 'elastic.out(1,.4)' }));
});

/* ---------------- card tilt ---------------- */
if (FX) $$('[data-tilt]').forEach(el => {
  el.addEventListener('mousemove', e => {
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
    gsap.to(el, { rotateY: px * 6, rotateX: -py * 6, y: -4, duration: .5, ease: 'power3.out', transformPerspective: 900 });
  });
  el.addEventListener('mouseleave', () => gsap.to(el, { rotateX: 0, rotateY: 0, y: 0, duration: .7, ease: 'power3.out' }));
});

/* ---------------- smooth scroll ---------------- */
let lenis = null;
if (!REDUCED && window.Lenis) {
  lenis = new Lenis({ duration: 1.1, smoothWheel: true });
  if (HAS_GSAP) {
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(t => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  } else {
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  }
}

/* ---------------- reveals ---------------- */
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), { threshold: 0.12 });
$$('.reveal').forEach(el => io.observe(el));

/* ---------------- header + scroll rail (no gsap needed) ---------------- */
const head = $('#head'), railFill = $('.rail i');
addEventListener('scroll', () => {
  head.classList.toggle('scrolled', scrollY > 60);
  if (railFill) {
    const h = document.documentElement;
    railFill.style.transform =
      `scaleY(${h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)})`;
  }
}, { passive: true });

/* ---------------- mobile nav ---------------- */
const burger = $('#burger'), mnav = $('#mnav');
const bgEls = $$('main,.head,.foot,.rail');
const setMenu = open => {
  mnav.classList.toggle('open', open);
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  mnav.setAttribute('aria-hidden', !open);
  mnav.toggleAttribute('inert', !open);
  bgEls.forEach(el => el.toggleAttribute('inert', open));
  if (lenis) open ? lenis.stop() : lenis.start();
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) $('.mnav-close').focus();
};
burger.addEventListener('click', () => setMenu(!mnav.classList.contains('open')));
$('#mnav-close').addEventListener('click', () => setMenu(false));
addEventListener('keydown', e => {
  if (e.key === 'Escape' && mnav.classList.contains('open')) {
    setMenu(false); burger.focus();
  }
});

/* ---------------- anchors — smooth eased travel ---------------- */
$$('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
  const id = a.getAttribute('href');
  if (id === '#') { e.preventDefault(); return; }
  const t = id === '#top' ? 0 : document.querySelector(id);
  if (t === null) return;
  e.preventDefault();
  if (mnav.classList.contains('open')) setMenu(false);
  const offset = id === '#top' ? 0 : -90;          // clear the fixed header
  const ease = x => 1 - Math.pow(1 - x, 4);
  if (lenis) lenis.scrollTo(t, { offset, duration: 1.6, easing: ease });
  else if (t === 0) scrollTo({ top: 0, behavior: 'smooth' });
  else t.scrollIntoView({ behavior: 'smooth', block: 'start' });
}));

/* ---------------- subtle parallax ---------------- */
if (ANIM) $$('[data-parallax]').forEach(img => {
  gsap.fromTo(img, { yPercent: -6 }, {
    yPercent: 6, ease: 'none',
    scrollTrigger: { trigger: img.closest('figure'), start: 'top bottom', end: 'bottom top', scrub: true }
  });
});

/* ---------------- counters (no gsap needed) ---------------- */
$$('[data-count]').forEach(el => {
  const end = +el.dataset.count;
  const co = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    co.unobserve(el);
    if (REDUCED) { el.textContent = end; return; }
    const t0 = performance.now();
    const tick = t => {
      const p = Math.min(1, (t - t0) / 1600);
      el.textContent = Math.round(end * (1 - Math.pow(1 - p, 2)));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }), { threshold: .4 });
  co.observe(el);
});

