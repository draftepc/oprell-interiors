/* ============================================================
   OPRELL — inner pages
   shared chrome: loader · cursor · header · menu · reveals
   ============================================================ */
gsap.registerPlugin(ScrollTrigger);

const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $  = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

/* ---------------- loader ---------------- */
const loader = $('#loader');
setTimeout(() => {
  loader.classList.add('out');
  document.body.classList.add('loaded');
  setTimeout(() => loader.remove(), 600);
}, 1200);

/* ---------------- custom cursor ---------------- */
const cur = $('#cursor');
if (matchMedia('(hover:hover) and (pointer:fine)').matches && !REDUCED) {
  document.body.classList.add('cur-on');
  const cx = gsap.quickTo(cur, 'x', { duration: 0.12, ease: 'power3' });
  const cy = gsap.quickTo(cur, 'y', { duration: 0.12, ease: 'power3' });
  const txt = $('.cur-txt');
  addEventListener('mousemove', e => { cx(e.clientX); cy(e.clientY); });
  document.addEventListener('mouseover', e => {
    const view = e.target.closest('[data-cursor="view"]');
    const hov = e.target.closest('a,button,[data-mag]');
    cur.classList.toggle('view', !!view);
    cur.classList.toggle('hov', !!hov && !view);
    txt.textContent = view ? 'VIEW' : '';
  });
}

/* ---------------- magnetic ---------------- */
if (!REDUCED) $$('[data-mag]').forEach(el => {
  el.addEventListener('mousemove', e => {
    const r = el.getBoundingClientRect();
    gsap.to(el, { x: (e.clientX - r.left - r.width/2) * .3, y: (e.clientY - r.top - r.height/2) * .3, duration: .4, ease: 'power3.out' });
  });
  el.addEventListener('mouseleave', () => gsap.to(el, { x: 0, y: 0, duration: .7, ease: 'elastic.out(1,.4)' }));
});

/* ---------------- smooth scroll ---------------- */
let lenis = null;
if (!REDUCED && window.Lenis) {
  lenis = new Lenis({ duration: 1.1, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
}

/* ---------------- reveals ---------------- */
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), { threshold: 0.12 });
$$('.reveal').forEach(el => io.observe(el));

/* ---------------- header ---------------- */
const head = $('#head');
addEventListener('scroll', () => {
  head.classList.toggle('scrolled', scrollY > 60);
}, { passive: true });

/* ---------------- scroll rail ---------------- */
ScrollTrigger.create({
  start: 0, end: 'max',
  onUpdate: s => { $('.rail i').style.transform = `scaleY(${s.progress})`; }
});

/* ---------------- mobile nav ---------------- */
const burger = $('#burger'), mnav = $('#mnav');
const bgEls = $$('main,.head,.foot,.rail');
burger.addEventListener('click', () => {
  const open = mnav.classList.toggle('open');
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  mnav.setAttribute('aria-hidden', !open);
  mnav.toggleAttribute('inert', !open);
  bgEls.forEach(el => el.toggleAttribute('inert', open));
  if (lenis) open ? lenis.stop() : lenis.start();
  document.body.style.overflow = open ? 'hidden' : '';
});
$('#mnav-close').addEventListener('click', () => burger.click());
addEventListener('keydown', e => {
  if (e.key === 'Escape' && mnav.classList.contains('open')) burger.click();
});

/* ---------------- anchors ---------------- */
$$('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
  const id = a.getAttribute('href');
  if (id === '#') { e.preventDefault(); return; }
  const t = document.querySelector(id);
  if (t === null) return;
  e.preventDefault();
  if (mnav.classList.contains('open')) burger.click();
  const ease = x => 1 - Math.pow(1 - x, 4);
  if (lenis) lenis.scrollTo(t, { offset: -90, duration: 1.6, easing: ease });
  else t.scrollIntoView({ behavior: 'smooth', block: 'start' });
}));

/* ---------------- counters ---------------- */
$$('[data-count]').forEach(el => {
  const end = +el.dataset.count;
  ScrollTrigger.create({
    trigger: el, start: 'top 88%', once: true,
    onEnter() {
      gsap.fromTo(el, { innerText: 0 }, {
        innerText: end, duration: 1.6, ease: 'power2.out', snap: { innerText: 1 }
      });
    }
  });
});

/* ---------------- subtle parallax ---------------- */
if (!REDUCED) $$('[data-parallax]').forEach(img => {
  gsap.fromTo(img, { yPercent: -6 }, {
    yPercent: 6, ease: 'none',
    scrollTrigger: { trigger: img.closest('figure'), start: 'top bottom', end: 'bottom top', scrub: true }
  });
});

/* ---------------- gallery lightbox ---------------- */
const lb = $('#lb');
if (lb) {
  const items = $$('.gal-item');
  const lbImg = $('#lb-img'), lbCount = $('#lb-count'), lbClose = $('#lb-close');
  let li = 0, lbOpen = false, lastFocus = null;

  const show = i => {
    li = (i + items.length) % items.length;
    lbImg.src = items[li].querySelector('img').src;
    lbCount.textContent = (li + 1) + ' / ' + items.length;
  };
  const openLb = i => {
    lastFocus = document.activeElement;
    show(i);
    lb.classList.add('open'); lb.removeAttribute('inert');
    lbOpen = true; lbClose.focus();
    if (lenis) lenis.stop();
  };
  const closeLb = () => {
    lb.classList.remove('open'); lb.setAttribute('inert', '');
    lbOpen = false;
    if (lenis) lenis.start();
    if (lastFocus) lastFocus.focus();
  };

  items.forEach((b, i) => b.addEventListener('click', () => openLb(i)));
  lbClose.addEventListener('click', closeLb);
  $('#lb-prev').addEventListener('click', e => { e.stopPropagation(); show(li - 1); });
  $('#lb-next').addEventListener('click', e => { e.stopPropagation(); show(li + 1); });
  lb.addEventListener('click', e => { if (e.target === lb) closeLb(); });
  addEventListener('keydown', e => {
    if (!lbOpen) return;
    if (e.key === 'Escape') closeLb();
    if (e.key === 'ArrowLeft') show(li - 1);
    if (e.key === 'ArrowRight') show(li + 1);
  });
  let tx = 0;
  lb.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 50) show(li + (dx < 0 ? 1 : -1));
  }, { passive: true });
}
