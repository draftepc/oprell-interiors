/* ============================================================
   OPRELL — professional UI
   smooth scroll · reveals · drag compare · project overlay
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
  gsap.to('.hero-carousel img', { scale: 1, duration: 1.6, ease: 'power3.out' });
  setTimeout(() => loader.remove(), 600);
}, 1200);

/* ---------------- custom cursor ---------------- */
const cur = $('#cursor');
if (matchMedia('(hover:hover) and (pointer:fine)').matches && !REDUCED) {
  const cx = gsap.quickTo(cur, 'x', { duration: 0.12, ease: 'power3' });
  const cy = gsap.quickTo(cur, 'y', { duration: 0.12, ease: 'power3' });
  const txt = $('.cur-txt');
  addEventListener('mousemove', e => { cx(e.clientX); cy(e.clientY); });
  document.addEventListener('mouseover', e => {
    const spot = e.target.closest('.ba-spot');
    const view = e.target.closest('[data-cursor="view"]');
    const drag = e.target.closest('[data-cursor="drag"]');
    const hov = spot || e.target.closest('a,button,[data-mag],.svcard,.pcell');
    cur.classList.toggle('view', !!view);
    cur.classList.toggle('drag', !!drag && !spot);
    cur.classList.toggle('hov', !!hov && !view && !drag);
    txt.textContent = view ? 'VIEW' : drag ? 'DRAG' : '';
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

/* ---------------- card tilt ---------------- */
if (!REDUCED) $$('[data-tilt]').forEach(el => {
  el.addEventListener('mousemove', e => {
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
    gsap.to(el, { rotateY: px * 6, rotateX: -py * 6, y: -4, duration: .5, ease: 'power3.out', transformPerspective: 900 });
  });
  el.addEventListener('mouseleave', () => gsap.to(el, { rotateX: 0, rotateY: 0, y: 0, duration: .7, ease: 'power3.out' }));
});

/* ---------------- hero slider — drag-to-wipe (like Before/After) ---------------- */
const hImgs = $$('#hero-carousel img');
const dotsBox = $('#hero-dots');
const hCar = $('#hero-carousel');
const hDiv = $('#hc-div');
const HN = hImgs.length;
let hCur = 0, hTimer = null, wiping = false;
const state = { pos: 100 };        // divider position %
let peekIdx = 1, peekFrom = 'right', peekEl = null;

/* per-slide context for the floating chips */
const HERO_CTX = [
  { b: 'Villa 172',       s: 'Emirates Hills — Dubai', y: '2024', t: 'Residential fit-out', p: 0 },
  { b: 'Amulfi Villa 08', s: 'Jumeirah Bay — Dubai',   y: '2023', t: 'Residential',         p: 1 },
  { b: 'CFO Office',      s: 'Jafza LOB 17 — Dubai',   y: '2022', t: 'Commercial',          p: 2 },
];
const chipA = $('#chip-a'), chipB = $('#chip-b');
const setCtx = i => {
  const c = HERO_CTX[i % HERO_CTX.length];
  chipA.dataset.proj = c.p; chipB.dataset.proj = c.p;
  chipA.innerHTML = `<b>${c.b}</b><span>${c.s}</span>`;
  chipB.innerHTML = `<b>${c.y}</b><span>${c.t}</span>`;
  gsap.fromTo([chipA, chipB], { opacity: 0, y: 10 },
    { opacity: 1, y: 0, duration: .55, ease: 'power3.out', stagger: .08, delay: .15 });
};
[chipA, chipB].forEach(ch => ch.addEventListener('click', () => openProject(+ch.dataset.proj || 0)));

const applyWipe = () => {
  if (!peekEl) return;
  if (peekFrom === 'right') {
    peekEl.style.clipPath = `inset(0 0 0 ${state.pos}%)`;
    hDiv.style.left = state.pos + '%';
  } else {
    peekEl.style.clipPath = `inset(0 ${100 - state.pos}% 0 0)`;
    hDiv.style.left = (100 - state.pos) + '%';
  }
};
const clearPeek = () => {
  if (peekEl) { peekEl.classList.remove('peek'); peekEl.style.clipPath = ''; peekEl = null; }
  hCar.classList.remove('wiping');
};
const commitWipe = () => {
  hImgs[hCur].classList.remove('on');
  hCur = peekIdx;
  hImgs[hCur].classList.add('on');
  $$('#hero-dots i').forEach((d, i) => d.classList.toggle('on', i === hCur));
  setCtx(hCur);
  clearPeek();
};

if (HN > 1) {
  hImgs.forEach((_, i) => {
    const d = document.createElement('i');
    if (!i) d.classList.add('on');
    dotsBox.appendChild(d);
  });
  const wipe = (target, from, dur = 1.2) => {
    if (wiping || target === hCur) return;
    wiping = true; peekIdx = target; peekFrom = from;
    peekEl = hImgs[peekIdx];
    peekEl.classList.add('peek');
    hCar.classList.add('wiping');
    state.pos = from === 'right' ? 100 : 0;
    applyWipe();
    gsap.to(state, {
      pos: from === 'right' ? 0 : 100, duration: dur, ease: 'power3.inOut',
      onUpdate: applyWipe,
      onComplete: () => { commitWipe(); wiping = false; }
    });
  };
  const next = () => wipe((hCur + 1) % HN, 'right');
  const prev = () => wipe((hCur - 1 + HN) % HN, 'left');
  const auto = () => { if (!REDUCED) hTimer = setInterval(next, 5500); };
  const stop = () => { clearInterval(hTimer); hTimer = null; };
  auto();
  $$('#hero-dots i').forEach((d, i) => d.addEventListener('click', () => {
    stop(); wipe(i, i > hCur ? 'right' : 'left', .9); auto();
  }));
  $('#hc-prev').addEventListener('click', e => { e.stopPropagation(); stop(); prev(); auto(); });
  $('#hc-next').addEventListener('click', e => { e.stopPropagation(); stop(); next(); auto(); });
  hCar.addEventListener('mouseenter', stop);
  hCar.addEventListener('mouseleave', () => { if (!hTimer) auto(); });

  /* drag the divider */
  let startX = null, dir = null;
  hCar.addEventListener('pointerdown', e => {
    if (wiping || e.target.closest('.hc-arrow')) return;
    startX = e.clientX; dir = null;
    hCar.classList.add('used');
    hCar.setPointerCapture(e.pointerId);
  });
  hCar.addEventListener('pointermove', e => {
    if (startX === null || wiping) return;
    const dx = e.clientX - startX;
    if (!dir && Math.abs(dx) > 8) {
      dir = dx < 0 ? 'right' : 'left';
      peekIdx = dir === 'right' ? (hCur + 1) % HN : (hCur - 1 + HN) % HN;
      peekEl = hImgs[peekIdx]; peekFrom = dir;
      peekEl.classList.add('peek');
      hCar.classList.add('wiping');
      state.pos = dir === 'right' ? 100 : 0;
    }
    if (dir) {
      state.pos = Math.min(Math.max(
        dir === 'right' ? 100 + dx / hCar.offsetWidth * 100 : dx / hCar.offsetWidth * 100, 0), 100);
      applyWipe();
    }
  });
  const endDrag = () => {
    if (startX === null) return;
    startX = null;
    if (!dir || wiping) return;
    const done = dir === 'right' ? state.pos < 45 : state.pos > 55;
    wiping = true;
    gsap.to(state, {
      pos: dir === 'right' ? (done ? 0 : 100) : (done ? 100 : 0),
      duration: .6, ease: 'power3.out', onUpdate: applyWipe,
      onComplete: () => {
        if (done) { commitWipe(); stop(); auto(); }
        else clearPeek();
        wiping = false; dir = null;
      }
    });
  };
  hCar.addEventListener('pointerup', endDrag);
  hCar.addEventListener('pointercancel', endDrag);
}

/* ---------------- hero word rotator — letter flip ---------------- */
(() => {
  const rw = $('.rw'), words = $$('.rw i');
  if (!rw || words.length < 2) return;
  words.forEach(w => {
    w.innerHTML = [...w.textContent].map(c => `<b>${c}</b>`).join('');
  });
  rw.style.width = words[0].offsetWidth + 'px';
  let wi = 0, busy = false;
  const flip = () => {
    if (busy) return; busy = true;
    const out = words[wi], next = words[(wi + 1) % words.length];
    wi = (wi + 1) % words.length;
    const outChars = out.querySelectorAll('b'), inChars = next.querySelectorAll('b');
    const outDur = .38 + outChars.length * .022;   // let the old word fully leave first
    gsap.to(outChars, {
      yPercent: -115, opacity: 0, duration: .38, ease: 'power2.in', stagger: .022,
      onComplete: () => { out.classList.remove('on'); gsap.set(outChars, { yPercent: 0, opacity: 1 }); }
    });
    gsap.to(rw, { width: next.offsetWidth, duration: .55, ease: 'power3.inOut', delay: outDur * .5 });
    next.classList.add('on');
    gsap.fromTo(inChars,
      { yPercent: 115, opacity: 0 },
      { yPercent: 0, opacity: 1, duration: .5, ease: 'power3.out', stagger: .024, delay: outDur,
        onComplete: () => { busy = false; } });
  };
  if (!REDUCED) setInterval(flip, 3600);
})();

/* ---------------- hero media tilt + chip parallax ---------------- */
if (!REDUCED) {
  const media = $('#hero-media'), chips = $$('.hero-chip');
  media.addEventListener('mousemove', e => {
    const r = media.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
    gsap.to(media, { rotateY: px * 3.5, rotateX: -py * 3, duration: .8, ease: 'power3.out', transformPerspective: 1400 });
    gsap.to(chips[0], { x: px * -18, y: py * -14, duration: .8, ease: 'power3.out' });
    gsap.to(chips[1], { x: px * 22, y: py * 16, duration: .8, ease: 'power3.out' });
  });
  media.addEventListener('mouseleave', () => {
    gsap.to(media, { rotateX: 0, rotateY: 0, duration: .9, ease: 'power3.out' });
    chips.forEach(c => gsap.to(c, { x: 0, y: 0, duration: .9, ease: 'power3.out' }));
  });
}



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
let lastY = 0;
addEventListener('scroll', () => {
  const y = scrollY;
  head.classList.toggle('scrolled', y > 60);
  head.style.transform = (y > 500 && y > lastY) ? 'translateY(-100%)' : '';
  lastY = y;
}, { passive: true });
head.style.transition = 'background .4s,border-color .4s,backdrop-filter .4s,transform .5s cubic-bezier(.22,1,.36,1)';

/* ---------------- scroll rail ---------------- */
ScrollTrigger.create({
  start: 0, end: 'max',
  onUpdate: s => { $('.rail i').style.transform = `scaleY(${s.progress})`; }
});

/* ---------------- mobile nav ---------------- */
const burger = $('#burger'), mnav = $('#mnav');
burger.addEventListener('click', () => {
  const open = mnav.classList.toggle('open');
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  mnav.setAttribute('aria-hidden', !open);
  if (lenis) open ? lenis.stop() : lenis.start();
  document.body.style.overflow = open ? 'hidden' : '';
});
$('#mnav-close').addEventListener('click', () => burger.click());

/* ---------------- anchors — smooth eased travel ---------------- */
$$('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
  const id = a.getAttribute('href');
  if (id === '#') { e.preventDefault(); return; }
  const t = id === '#top' ? 0 : document.querySelector(id);
  if (t === null) return;
  e.preventDefault();
  if (mnav.classList.contains('open')) burger.click();
  const offset = id === '#top' ? 0 : -90;          // clear the fixed header
  const ease = x => 1 - Math.pow(1 - x, 4);        // long soft ease-out
  if (lenis) lenis.scrollTo(t, { offset, duration: 1.6, easing: ease });
  else if (t === 0) scrollTo({ top: 0, behavior: 'smooth' });
  else t.scrollIntoView({ behavior: 'smooth', block: 'start' });
}));

/* ---------------- subtle parallax ---------------- */
if (!REDUCED) $$('[data-parallax]').forEach(img => {
  gsap.fromTo(img, { yPercent: -6 }, {
    yPercent: 6, ease: 'none',
    scrollTrigger: { trigger: img.closest('figure'), start: 'top bottom', end: 'bottom top', scrub: true }
  });
});

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

/* ---------------- before / after slider ---------------- */
(() => {
  const ba = $('#ba'), wrap = $('#ba-before-wrap'), handle = $('#ba-handle');
  if (!ba) return;
  const setPct = p => {
    p = Math.min(Math.max(p, 2), 98);
    wrap.style.width = p + '%';
    handle.style.left = p + '%';
    wrap.querySelector('img').style.width = ba.offsetWidth + 'px';
  };
  const setX = x => {
    const r = ba.getBoundingClientRect();
    setPct((x - r.left) / r.width * 100);
  };
  setPct(50);
  addEventListener('resize', () => setPct(parseFloat(wrap.style.width) || 50));

  /* invite: gentle sweep when it scrolls into view */
  if (!REDUCED) ScrollTrigger.create({
    trigger: ba, start: 'top 70%', once: true,
    onEnter() {
      const proxy = { p: 50 };
      gsap.timeline()
        .to(proxy, { p: 66, duration: 1.0, ease: 'power3.inOut', onUpdate: () => setPct(proxy.p) })
        .to(proxy, { p: 46, duration: 1.0, ease: 'power3.inOut', onUpdate: () => setPct(proxy.p) });
    }
  });

  let drag = false;
  ba.addEventListener('pointerdown', e => {
    if (e.target.closest('.ba-spot')) return;
    drag = true; ba.classList.add('used');
    ba.setPointerCapture(e.pointerId); setX(e.clientX);
  });
  ba.addEventListener('pointermove', e => drag && setX(e.clientX));
  addEventListener('pointerup', () => drag = false);
})();

/* ---------------- process — dashed curve through the cards ---------------- */
(() => {
  const wrap = $('#pcwrap'), line = $('#pc-line'), fill = $('#pc-fl');
  const cells = $$('.pcell'), badges = $$('.pcell-n');
  if (!wrap || !cells.length) return;

  let L = 0, fracs = [];
  const draw = () => {
    const wr = wrap.getBoundingClientRect();
    const pts = badges.map(b => {
      const r = b.getBoundingClientRect();
      return { x: r.left - wr.left + r.width / 2, y: r.top - wr.top + r.height / 2, r: r.width / 2 + 5 };
    });
    // bowed segments between badges — alternates direction so the line snakes
    let d = '';
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i];
      const dx = b.x - a.x, dy = b.y - a.y, dist = Math.hypot(dx, dy) || 1;
      const ux = dx / dist, uy = dy / dist;
      const x0 = a.x + ux * a.r, y0 = a.y + uy * a.r;
      const x1 = b.x - ux * b.r, y1 = b.y - uy * b.r;
      const mx = (x0 + x1) / 2, my = (y0 + y1) / 2;
      const bow = (i % 2 ? 1 : -1) * Math.min(38, dist * 0.22);
      d += ` M ${x0.toFixed(1)} ${y0.toFixed(1)} Q ${(mx - uy * bow).toFixed(1)} ${(my + ux * bow).toFixed(1)}, ${x1.toFixed(1)} ${y1.toFixed(1)}`;
    }
    line.setAttribute('d', d); fill.setAttribute('d', d);
    $('#pc-svg').setAttribute('viewBox', `0 0 ${wrap.offsetWidth} ${wrap.offsetHeight}`);
    L = line.getTotalLength();
    fill.style.strokeDasharray = `${L * 0.26} ${L}`;
    fill.style.strokeDashoffset = 0;
    // badge positions as fractions along the path
    fracs = pts.map(p => {
      let best = 0, bd = 1e9;
      for (let s = 0; s <= 200; s++) {
        const pt = line.getPointAtLength(L * s / 200);
        const dd = Math.hypot(pt.x - p.x, pt.y - p.y);
        if (dd < bd) { bd = dd; best = s / 200; }
      }
      return best;
    });
  };
  draw();
  addEventListener('load', draw);
  addEventListener('resize', draw);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);

  /* continuous travelling pulse — always animating */
  if (!REDUCED) {
    const pulse = { v: 0 };
    gsap.to(pulse, {
      v: 1, duration: 4.6, ease: 'none', repeat: -1,
      onUpdate() {
        fill.style.strokeDashoffset = -(pulse.v * L);
        cells.forEach((c, i) => {
          c.classList.toggle('step-on', pulse.v + 0.26 >= fracs[i]);
        });
      }
    });
  } else {
    fill.style.strokeDasharray = 'none';
    cells.forEach(c => c.classList.add('step-on'));
  }
})();

/* ---------------- project overlay ---------------- */
const pp = $('#pp');
const ppBody = $('.pp-inner');
let ppIdx = 0, ppOpen = false;
const rows = $$('.pcard');

const PP_COPY = {
  'VILLA 172': 'A full interior renovation in Emirates Hills — marble floors, warm oak joinery and a palette built around daylight. Living spaces open onto the pool; every finish was produced by our in-house craftsmen.',
  'AMULFI VILLA 08': 'A family villa on Jumeirah Bay designed around texture — terracotta walls, herringbone floors and joinery that reads as furniture. Interior and garden were composed as one continuous space.',
  'CFO OFFICE — DP WORLD': 'An executive suite at JAFZA LOB 17 — dark timber, copper detailing and controlled light. Reception, office and majlis planned as a sequence of calibrated thresholds.',
  "SUSAN'S BAKING CO.": 'A retail and F&B fit-out for Susan\'s Baking Co. — counters, shelving and signage built in our joinery, with a palette tuned to the brand. From drawings to opening day under one team.',
  'JBR WASHROOM': 'A complete washroom renovation in JLT — demolished to the shell, replumbed, retiled and refitted with custom vanity, mirror and lighting. A small room treated with the same discipline as a villa.',
  'VILLA 32': 'A villa renovation in Arabian Ranches — interiors reworked room by room with new joinery, flooring and lighting, executed by our in-house team while the family remained in residence.'
};

function fillProject(i) {
  const el = rows[i]; ppIdx = i;
  $('.pp-hero img').src = el.dataset.img;
  $('.pp-num').textContent = 'N°' + String(i + 1).padStart(2, '0') + ' — ' + el.dataset.year;
  $('.pp-title').textContent = el.dataset.title;
  $('.pp-meta').textContent = el.dataset.meta;
  $('.pp-desc').textContent = PP_COPY[el.dataset.title] || '';
  const parts = el.dataset.meta.split('—');
  $('.pp-facts').innerHTML =
    'Sector — ' + (parts[0] || '').trim() + '<br>' +
    'Location — ' + (parts[1] || 'Dubai').trim() + '<br>' +
    'Year — ' + el.dataset.year + '<br>Status — Delivered';
  const pool = ['g1.jpg', 'g2.jpg', 'g3.jpg', 'g5.jpg', 'g6.jpg', 'g7.jpg'];
  $$('.pp-thumbs img').forEach((t, k) => t.src = 'assets/img/' + pool[(i + k) % pool.length]);
}

function openProject(i) {
  fillProject(i);
  ppOpen = true;
  pp.classList.add('open');
  pp.setAttribute('aria-hidden', 'false');
  ppBody.scrollTop = 0;
  if (lenis) lenis.stop();
  document.body.style.overflow = 'hidden';
  gsap.from('.pp-hero img', { scale: 1.15, duration: 1.1, ease: 'power3.out' });
  gsap.from('.pp-body > *', { y: 26, opacity: 0, stagger: 0.06, duration: 0.7, ease: 'power3.out', delay: 0.25 });
}
function closeProject() {
  pp.classList.remove('open');
  pp.setAttribute('aria-hidden', 'true');
  ppOpen = false;
  if (lenis) lenis.start();
  document.body.style.overflow = '';
}
rows.forEach((r, i) => r.addEventListener('click', e => { e.preventDefault(); openProject(i); }));
$('.pp-close').addEventListener('click', closeProject);
$('.pp-next').addEventListener('click', () => {
  fillProject((ppIdx + 1) % rows.length);
  ppBody.scrollTop = 0;
  gsap.from('.pp-hero img', { scale: 1.15, duration: 1, ease: 'power3.out' });
});
addEventListener('keydown', e => {
  if (e.key === 'Escape') { if (ppOpen) closeProject(); else if (mnav.classList.contains('open')) burger.click(); }
});
